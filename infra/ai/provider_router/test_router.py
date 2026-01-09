"""
Tests for AI Provider Router

Run with: pytest test_router.py -v
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from router import ProviderRouter, call_ai, AIResponse, AIError, Provider


class TestProviderConfiguration:
    """Test provider configuration from environment"""

    def test_default_primary_provider(self):
        """Test default primary provider is OpenAI"""
        with patch.dict(os.environ, {}, clear=True):
            router = ProviderRouter()
            assert router.primary_provider == Provider.OPENAI

    def test_override_primary_provider(self):
        """Test AI_PROVIDER_PRIMARY overrides default"""
        with patch.dict(os.environ, {'AI_PROVIDER_PRIMARY': 'gemini'}):
            router = ProviderRouter()
            assert router.primary_provider == Provider.GEMINI

    def test_ipai_ai_provider_fallback(self):
        """Test IPAI_AI_PROVIDER is used if AI_PROVIDER_PRIMARY not set"""
        with patch.dict(os.environ, {'IPAI_AI_PROVIDER': 'anthropic'}):
            router = ProviderRouter()
            assert router.primary_provider == Provider.ANTHROPIC

    def test_secondary_provider(self):
        """Test secondary provider configuration"""
        with patch.dict(os.environ, {'AI_PROVIDER_SECONDARY': 'gemini'}):
            router = ProviderRouter()
            assert router.secondary_provider == Provider.GEMINI

    def test_tertiary_provider(self):
        """Test tertiary provider configuration"""
        with patch.dict(os.environ, {'AI_PROVIDER_TERTIARY': 'ollama'}):
            router = ProviderRouter()
            assert router.tertiary_provider == Provider.OLLAMA

    def test_retry_configuration(self):
        """Test retry attempts and delay configuration"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_RETRY_ATTEMPTS': '5',
            'AI_PROVIDER_RETRY_DELAY': '3'
        }):
            router = ProviderRouter()
            assert router.retry_attempts == 5
            assert router.retry_delay == 3

    def test_default_retry_configuration(self):
        """Test default retry values"""
        with patch.dict(os.environ, {}, clear=True):
            router = ProviderRouter()
            assert router.retry_attempts == 3
            assert router.retry_delay == 2


class TestProviderFailover:
    """Test automatic failover between providers"""

    def test_single_provider_success(self):
        """Test successful call with single provider"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'IPAI_LLM_API_KEY': 'test-key'
        }):
            router = ProviderRouter()

            with patch.object(router, '_call_openai', return_value={
                'content': 'Hello',
                'model': 'gpt-4o-mini',
                'tokens': 10,
                'metadata': {}
            }):
                response = router.call_ai("Test prompt")
                assert response.content == 'Hello'
                assert response.provider == 'openai'

    def test_failover_to_secondary(self):
        """Test failover to secondary provider on primary failure"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'AI_PROVIDER_SECONDARY': 'gemini',
            'IPAI_LLM_API_KEY': 'test-key',
            'GEMINI_API_KEY': 'test-gemini-key'
        }):
            router = ProviderRouter()

            # Mock primary failure, secondary success
            with patch.object(router, '_call_openai', side_effect=AIError("OpenAI failed", "openai")):
                with patch.object(router, '_call_gemini', return_value={
                    'content': 'Gemini response',
                    'model': 'gemini-1.5-flash',
                    'tokens': 15,
                    'metadata': {}
                }):
                    response = router.call_ai("Test prompt")
                    assert response.content == 'Gemini response'
                    assert response.provider == 'gemini'

    def test_failover_to_tertiary(self):
        """Test failover to tertiary provider when primary and secondary fail"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'AI_PROVIDER_SECONDARY': 'gemini',
            'AI_PROVIDER_TERTIARY': 'anthropic',
            'IPAI_LLM_API_KEY': 'test-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'ANTHROPIC_API_KEY': 'test-anthropic-key'
        }):
            router = ProviderRouter()

            # Mock primary and secondary failure, tertiary success
            with patch.object(router, '_call_openai', side_effect=AIError("OpenAI failed", "openai")):
                with patch.object(router, '_call_gemini', side_effect=AIError("Gemini failed", "gemini")):
                    with patch.object(router, '_call_anthropic', return_value={
                        'content': 'Anthropic response',
                        'model': 'claude-3-5-sonnet-20241022',
                        'tokens': 20,
                        'metadata': {}
                    }):
                        response = router.call_ai("Test prompt")
                        assert response.content == 'Anthropic response'
                        assert response.provider == 'anthropic'

    def test_all_providers_fail(self):
        """Test exception when all providers fail"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'AI_PROVIDER_SECONDARY': 'gemini',
            'IPAI_LLM_API_KEY': 'test-key',
            'GEMINI_API_KEY': 'test-gemini-key'
        }):
            router = ProviderRouter()

            with patch.object(router, '_call_openai', side_effect=AIError("OpenAI failed", "openai")):
                with patch.object(router, '_call_gemini', side_effect=AIError("Gemini failed", "gemini")):
                    with pytest.raises(AIError) as exc_info:
                        router.call_ai("Test prompt")
                    assert "All providers failed" in str(exc_info.value)


class TestRetryLogic:
    """Test retry logic for transient failures"""

    def test_retry_on_transient_failure(self):
        """Test retry on transient error"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'AI_PROVIDER_RETRY_ATTEMPTS': '3',
            'AI_PROVIDER_RETRY_DELAY': '0',  # No delay for tests
            'IPAI_LLM_API_KEY': 'test-key'
        }):
            router = ProviderRouter()

            # Fail twice, succeed on third attempt
            call_count = {'count': 0}

            def mock_openai(*args, **kwargs):
                call_count['count'] += 1
                if call_count['count'] < 3:
                    raise Exception("Transient error")
                return {
                    'content': 'Success',
                    'model': 'gpt-4o-mini',
                    'tokens': 10,
                    'metadata': {}
                }

            with patch.object(router, '_call_openai', side_effect=mock_openai):
                response = router.call_ai("Test prompt")
                assert response.content == 'Success'
                assert call_count['count'] == 3

    def test_max_retries_exceeded(self):
        """Test exception when max retries exceeded"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'AI_PROVIDER_RETRY_ATTEMPTS': '2',
            'AI_PROVIDER_RETRY_DELAY': '0',
            'IPAI_LLM_API_KEY': 'test-key'
        }):
            router = ProviderRouter()

            with patch.object(router, '_call_openai', side_effect=Exception("Persistent error")):
                with pytest.raises(AIError) as exc_info:
                    router.call_ai("Test prompt")
                assert "Max retries exceeded" in str(exc_info.value)


class TestParameterOverrides:
    """Test parameter override functionality"""

    def test_model_override(self):
        """Test model parameter override"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'IPAI_LLM_API_KEY': 'test-key',
            'IPAI_LLM_MODEL': 'gpt-4o-mini'
        }):
            router = ProviderRouter()

            with patch.object(router, '_call_openai', return_value={
                'content': 'Response',
                'model': 'gpt-4o',
                'tokens': 10,
                'metadata': {}
            }) as mock_openai:
                router.call_ai("Test", model='gpt-4o')
                mock_openai.assert_called_once()
                args, kwargs = mock_openai.call_args
                assert args[1] == 'gpt-4o'  # model parameter

    def test_temperature_override(self):
        """Test temperature parameter override"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'IPAI_LLM_API_KEY': 'test-key'
        }):
            router = ProviderRouter()

            with patch.object(router, '_call_openai', return_value={
                'content': 'Response',
                'model': 'gpt-4o-mini',
                'tokens': 10,
                'metadata': {}
            }) as mock_openai:
                router.call_ai("Test", temperature=0.9)
                mock_openai.assert_called_once()
                args, kwargs = mock_openai.call_args
                assert args[2] == 0.9  # temperature parameter

    def test_max_tokens_override(self):
        """Test max_tokens parameter override"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'IPAI_LLM_API_KEY': 'test-key'
        }):
            router = ProviderRouter()

            with patch.object(router, '_call_openai', return_value={
                'content': 'Response',
                'model': 'gpt-4o-mini',
                'tokens': 10,
                'metadata': {}
            }) as mock_openai:
                router.call_ai("Test", max_tokens=8192)
                mock_openai.assert_called_once()
                args, kwargs = mock_openai.call_args
                assert args[3] == 8192  # max_tokens parameter


class TestJSONMode:
    """Test structured JSON output mode"""

    def test_json_mode_enabled(self):
        """Test JSON mode flag is passed to provider"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'IPAI_LLM_API_KEY': 'test-key'
        }):
            router = ProviderRouter()

            with patch.object(router, '_call_openai', return_value={
                'content': '{"result": "json"}',
                'model': 'gpt-4o-mini',
                'tokens': 10,
                'metadata': {}
            }) as mock_openai:
                router.call_ai("Test", json_mode=True)
                mock_openai.assert_called_once()
                args, kwargs = mock_openai.call_args
                assert args[4] is True  # json_mode parameter


class TestMetadata:
    """Test metadata handling"""

    def test_metadata_passthrough(self):
        """Test custom metadata is included in response"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'IPAI_LLM_API_KEY': 'test-key'
        }):
            router = ProviderRouter()

            with patch.object(router, '_call_openai', return_value={
                'content': 'Response',
                'model': 'gpt-4o-mini',
                'tokens': 10,
                'metadata': {'provider_meta': 'value'}
            }):
                response = router.call_ai("Test", meta={'user_id': '123', 'request_id': 'abc'})
                assert response.metadata['user_id'] == '123'
                assert response.metadata['request_id'] == 'abc'
                assert response.metadata['provider_meta'] == 'value'

    def test_latency_tracking(self):
        """Test latency is tracked in response"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'IPAI_LLM_API_KEY': 'test-key'
        }):
            router = ProviderRouter()

            with patch.object(router, '_call_openai', return_value={
                'content': 'Response',
                'model': 'gpt-4o-mini',
                'tokens': 10,
                'metadata': {}
            }):
                response = router.call_ai("Test")
                assert response.latency_ms >= 0
                assert isinstance(response.latency_ms, int)


class TestAIResponse:
    """Test AIResponse dataclass"""

    def test_to_dict(self):
        """Test AIResponse conversion to dict"""
        response = AIResponse(
            content="Hello",
            model="gpt-4o-mini",
            provider="openai",
            tokens_used=10,
            latency_ms=150,
            metadata={"key": "value"}
        )
        data = response.to_dict()
        assert data['content'] == "Hello"
        assert data['model'] == "gpt-4o-mini"
        assert data['provider'] == "openai"
        assert data['tokens_used'] == 10
        assert data['latency_ms'] == 150
        assert data['metadata'] == {"key": "value"}

    def test_to_json(self):
        """Test AIResponse conversion to JSON"""
        response = AIResponse(
            content="Hello",
            model="gpt-4o-mini",
            provider="openai",
            tokens_used=10,
            latency_ms=150,
            metadata={}
        )
        json_str = response.to_json()
        assert '"content": "Hello"' in json_str
        assert '"provider": "openai"' in json_str


class TestConvenienceFunction:
    """Test module-level call_ai convenience function"""

    def test_call_ai_creates_router(self):
        """Test call_ai creates router singleton"""
        with patch.dict(os.environ, {
            'AI_PROVIDER_PRIMARY': 'openai',
            'IPAI_LLM_API_KEY': 'test-key'
        }):
            with patch('router.ProviderRouter') as MockRouter:
                mock_instance = MockRouter.return_value
                mock_instance.call_ai.return_value = AIResponse(
                    content="Hello",
                    model="gpt-4o-mini",
                    provider="openai",
                    tokens_used=10,
                    latency_ms=100,
                    metadata={}
                )

                response = call_ai("Test")
                assert response.content == "Hello"
                MockRouter.assert_called_once()


class TestMissingAPIKeys:
    """Test error handling for missing API keys"""

    def test_openai_missing_api_key(self):
        """Test error when OpenAI API key is missing"""
        with patch.dict(os.environ, {'AI_PROVIDER_PRIMARY': 'openai'}, clear=True):
            router = ProviderRouter()
            with pytest.raises(AIError) as exc_info:
                router._call_openai("Test", None, None, None, False)
            assert "IPAI_LLM_API_KEY not set" in str(exc_info.value)

    def test_gemini_missing_api_key(self):
        """Test error when Gemini API key is missing"""
        with patch.dict(os.environ, {}, clear=True):
            router = ProviderRouter()
            with pytest.raises(AIError) as exc_info:
                router._call_gemini("Test", None, None, None, False)
            assert "GEMINI_API_KEY not set" in str(exc_info.value)

    def test_anthropic_missing_api_key(self):
        """Test error when Anthropic API key is missing"""
        with patch.dict(os.environ, {}, clear=True):
            router = ProviderRouter()
            with pytest.raises(AIError) as exc_info:
                router._call_anthropic("Test", None, None, None, False)
            assert "ANTHROPIC_API_KEY not set" in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
