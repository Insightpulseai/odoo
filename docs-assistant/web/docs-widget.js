/**
 * Kapa.ai-style Documentation Widget
 * Self-hosted embeddable chat widget for documentation sites
 */

class DocsAssistantWidget {
    constructor(config = {}) {
        this.config = {
            apiUrl: config.apiUrl || 'http://localhost:8000',
            apiKey: config.apiKey,
            projectSlug: config.projectSlug || 'odoo-ce',
            position: config.position || 'bottom-right',
            theme: config.theme || 'light',
            ...config
        };

        this.isOpen = false;
        this.sessionId = this.generateSessionId();
        this.conversationHistory = [];
        
        this.init();
    }

    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }

    init() {
        this.createWidget();
        this.bindEvents();
        this.trackEvent('widget_loaded');
    }

    createWidget() {
        // Create FAB (Floating Action Button)
        this.fab = document.createElement('button');
        this.fab.className = `docs-assistant-fab docs-assistant-fab--${this.config.position} docs-assistant-fab--${this.config.theme}`;
        this.fab.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z" fill="currentColor"/>
            </svg>
        `;
        this.fab.setAttribute('aria-label', 'Open Documentation Assistant');

        // Create chat modal
        this.modal = document.createElement('div');
        this.modal.className = `docs-assistant-modal docs-assistant-modal--${this.config.position} docs-assistant-modal--${this.config.theme}`;
        this.modal.innerHTML = `
            <div class="docs-assistant-header">
                <h3>Documentation Assistant</h3>
                <button class="docs-assistant-close" aria-label="Close">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="2"/>
                    </svg>
                </button>
            </div>
            <div class="docs-assistant-chat">
                <div class="docs-assistant-messages"></div>
                <div class="docs-assistant-input-container">
                    <textarea 
                        class="docs-assistant-input" 
                        placeholder="Ask a question about the documentation..."
                        rows="1"
                    ></textarea>
                    <button class="docs-assistant-send" aria-label="Send message">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                            <path d="M2 21L23 12L2 3V10L17 12L2 14V21Z" fill="currentColor"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="docs-assistant-footer">
                <small>Powered by Docs Assistant</small>
            </div>
        `;

        // Add to DOM
        document.body.appendChild(this.fab);
        document.body.appendChild(this.modal);

        // Cache DOM elements
        this.messagesContainer = this.modal.querySelector('.docs-assistant-messages');
        this.input = this.modal.querySelector('.docs-assistant-input');
        this.sendButton = this.modal.querySelector('.docs-assistant-send');
        this.closeButton = this.modal.querySelector('.docs-assistant-close');
    }

    bindEvents() {
        this.fab.addEventListener('click', () => this.toggleModal());
        this.closeButton.addEventListener('click', () => this.closeModal());
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.input.addEventListener('input', () => {
            this.autoResizeTextarea();
        });

        // Close modal when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.modal.contains(e.target) && !this.fab.contains(e.target)) {
                this.closeModal();
            }
        });
    }

    toggleModal() {
        if (this.isOpen) {
            this.closeModal();
        } else {
            this.openModal();
        }
    }

    openModal() {
        this.isOpen = true;
        this.modal.classList.add('docs-assistant-modal--open');
        this.fab.classList.add('docs-assistant-fab--hidden');
        this.input.focus();
        this.trackEvent('modal_opened');
    }

    closeModal() {
        this.isOpen = false;
        this.modal.classList.remove('docs-assistant-modal--open');
        this.fab.classList.remove('docs-assistant-fab--hidden');
        this.trackEvent('modal_closed');
    }

    autoResizeTextarea() {
        this.input.style.height = 'auto';
        this.input.style.height = Math.min(this.input.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const message = this.input.value.trim();
        if (!message) return;

        // Clear input
        this.input.value = '';
        this.autoResizeTextarea();
        this.input.disabled = true;
        this.sendButton.disabled = true;

        // Add user message
        this.addMessage('user', message);

        // Show typing indicator
        const typingMessage = this.addMessage('assistant', '', true);

        try {
            const response = await this.askQuestion(message);
            
            // Remove typing indicator
            if (typingMessage && typingMessage.parentNode) {
                typingMessage.parentNode.remove();
            }

            // Add assistant response
            this.addMessage('assistant', response.answer, false, response.citations);
            
            // Track successful answer
            this.trackEvent('answer_received', {
                answer_id: response.metadata.answer_id,
                grounded: response.metadata.grounded,
                latency: response.metadata.latency_ms
            });

        } catch (error) {
            // Remove typing indicator
            if (typingMessage && typingMessage.parentNode) {
                typingMessage.parentNode.remove();
            }

            // Show error message
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            console.error('Docs Assistant error:', error);
            
            this.trackEvent('error_occurred', { error: error.message });
        } finally {
            this.input.disabled = false;
            this.sendButton.disabled = false;
            this.input.focus();
        }
    }

    async askQuestion(question) {
        const response = await fetch(`${this.config.apiUrl}/v1/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.config.apiKey
            },
            body: JSON.stringify({
                project_slug: this.config.projectSlug,
                question: question,
                history: this.conversationHistory,
                stream: false
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const result = await response.json();
        
        // Update conversation history
        this.conversationHistory.push(
            { role: 'user', content: question },
            { role: 'assistant', content: result.answer }
        );

        // Keep only last 10 messages
        if (this.conversationHistory.length > 20) {
            this.conversationHistory = this.conversationHistory.slice(-20);
        }

        return result;
    }

    addMessage(role, content, isTyping = false, citations = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `docs-assistant-message docs-assistant-message--${role}`;
        
        if (isTyping) {
            messageDiv.innerHTML = `
                <div class="docs-assistant-message-content">
                    <div class="docs-assistant-typing">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="docs-assistant-message-content">
                    ${this.formatMessage(content)}
                </div>
                ${citations.length > 0 ? this.renderCitations(citations) : ''}
            `;
        }

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        return messageDiv;
    }

    formatMessage(content) {
        // Convert markdown-like formatting and line breaks
        return content
            .replace(/\n/g, '<br>')
            .replace(/\[Source: ([^\]]+)\]/g, '<strong>[$1]</strong>');
    }

    renderCitations(citations) {
        const citationsHtml = citations.map(citation => `
            <div class="docs-assistant-citation" data-chunk-id="${citation.chunk_id}">
                <div class="docs-assistant-citation-title">
                    ${citation.document_title}
                    ${citation.heading ? ` - ${citation.heading}` : ''}
                </div>
                <div class="docs-assistant-citation-snippet">
                    ${citation.content_snippet}
                </div>
            </div>
        `).join('');

        return `
            <div class="docs-assistant-citations">
                <div class="docs-assistant-citations-title">Sources:</div>
                ${citationsHtml}
            </div>
        `;
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    trackEvent(eventType, metadata = {}) {
        // Emit custom event for analytics integration
        const event = new CustomEvent('docsAssistantEvent', {
            detail: {
                eventType,
                sessionId: this.sessionId,
                projectSlug: this.config.projectSlug,
                timestamp: new Date().toISOString(),
                metadata
            }
        });
        document.dispatchEvent(event);

        // Log to console in development
        if (this.config.debug) {
            console.log('Docs Assistant Event:', event.detail);
        }
    }

    // Public API methods
    open() {
        this.openModal();
    }

    close() {
        this.closeModal();
    }

    destroy() {
        if (this.fab && this.fab.parentNode) {
            this.fab.parentNode.removeChild(this.fab);
        }
        if (this.modal && this.modal.parentNode) {
            this.modal.parentNode.removeChild(this.modal);
        }
    }
}

// CSS styles (injected into document head)
const widgetStyles = `
.docs-assistant-fab {
    position: fixed;
    z-index: 10000;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    border: none;
    background: #007bff;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
}

.docs-assistant-fab:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.docs-assistant-fab--bottom-right {
    bottom: 20px;
    right: 20px;
}

.docs-assistant-fab--bottom-left {
    bottom: 20px;
    left: 20px;
}

.docs-assistant-fab--top-right {
    top: 20px;
    right: 20px;
}

.docs-assistant-fab--top-left {
    top: 20px;
    left: 20px;
}

.docs-assistant-fab--hidden {
    opacity: 0;
    visibility: hidden;
}

.docs-assistant-modal {
    position: fixed;
    z-index: 10001;
    width: 400px;
    height: 600px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
    opacity: 0;
    visibility: hidden;
    transform: scale(0.9);
    transition: all 0.3s ease;
}

.docs-assistant-modal--open {
    opacity: 1;
    visibility: visible;
    transform: scale(1);
}

.docs-assistant-modal--bottom-right {
    bottom: 20px;
    right: 20px;
}

.docs-assistant-modal--bottom-left {
    bottom: 20px;
    left: 20px;
}

.docs-assistant-modal--top-right {
    top: 20px;
    right: 20px;
}

.docs-assistant-modal--top-left {
    top: 20px;
    left: 20px;
}

.docs-assistant-modal--dark {
    background: #1a1a1a;
    color: white;
}

.docs-assistant-header {
    padding: 16px;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.docs-assistant-modal--dark .docs-assistant-header {
    border-bottom-color: #333;
}

.docs-assistant-header h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
}

.docs-assistant-close {
    background: none;
    border: none;
    color: #6c757d;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
}

.docs-assistant-close:hover {
    background: #f8f9fa;
}

.docs-assistant-modal--dark .docs-assistant-close:hover {
    background: #333;
}

.docs-assistant-chat {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.docs-assistant-messages {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.docs-assistant-message {
    display: flex;
}

.docs-assistant-message--user {
    justify-content: flex-end;
}

.docs-assistant-message--assistant {
    justify-content: flex-start;
}

.docs-assistant-message-content {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 16px;
    font-size: 14px;
    line-height: 1.4;
}

.docs-assistant-message--user .docs-assistant-message-content {
    background: #007bff;
    color: white;
    border-bottom-right-radius: 4px;
}

.docs-assistant-message--assistant .docs-assistant-message-content {
    background: #f8f9fa;
    color: #212529;
    border-bottom-left-radius: 4px;
}

.docs-assistant-modal--dark .docs-assistant-message--assistant .docs-assistant-message-content {
    background: #333;
    color: white;
}

.docs-assistant-typing {
    display: flex;
    gap: 4px;
    align-items: center;
}

.docs-assistant-typing span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #6c757d;
    animation: docs-assistant-typing 1.4s infinite ease-in-out;
}

.docs-assistant-typing span:nth-child(1) { animation-delay: -0.32s; }
.docs-assistant-typing span:nth-child(2) { animation-delay: -0.16s; }

@keyframes docs-assistant-typing {
    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
}

.docs-assistant-citations {
    margin-top: 8px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 3px solid #007bff;
}

.docs-assistant-modal--dark .docs-assistant-citations {
    background: #333;
}

.docs-assistant-citations-title {
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #6c757d;
}

.docs-assistant-citation {
    margin-bottom: 8px;
    font-size: 12px;
}

.docs-assistant-citation:last-child {
    margin-bottom: 0;
}

.docs-assistant-citation-title {
    font-weight: 600;
    margin-bottom: 2px;
}

.docs-assistant-citation-snippet {
    color: #6c757d;
    line-height: 1.3;
}

.docs-assistant-input-container {
    padding: 16px;
    border-top: 1px solid #e9ecef;
    display: flex;
    gap: 8px;
    align-items: flex-end;
}

.docs-assistant-modal--dark .docs-assistant-input-container {
    border-top-color: #333;
}

.docs-assistant-input {
    flex: 1;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 12px;
    font-size: 14px;
    resize: none;
    min-height: 44px;
    max-height: 120px;
    outline: none;
    transition: border-color 0.2s;
}

.docs-assistant-input:focus {
    border-color: #007bff;
}

.docs-assistant-modal--dark .docs-assistant-input {
    background: #333;
    border-color: #555;
    color: white;
}

.docs-assistant-send {
    background: #007bff;
    border: none;
    border-radius: 8px;
    color: white;
    cursor: pointer;
    padding: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s;
}

.docs-assistant-send:hover:not(:disabled) {
    background: #0056b3;
}

.docs-assistant-send:disabled {
    background: #6c757d;
    cursor: not-allowed;
}

.docs-assistant-footer {
    padding: 8px 16px;
    border-top: 1px solid #e9ecef;
    text-align: center;
}

.docs-assistant-modal--dark .docs-assistant-footer {
    border-top-color: #333;
}

.docs-assistant-footer small {
    color: #6c757d;
    font-size: 11px;
}
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = widgetStyles;
document.head.appendChild(styleSheet);

// Global initialization
window.DocsAssistantWidget = DocsAssistantWidget;

// Auto-initialize if data attributes are present
document.addEventListener('DOMContentLoaded', () => {
    const scriptElement = document.querySelector('script[data-docs-assistant]');
    if (scriptElement) {
        const config = {
            apiUrl: scriptElement.getAttribute('data-api-url'),
            apiKey: scriptElement.getAttribute('data-api-key'),
            projectSlug: scriptElement.getAttribute('data-project-slug'),
            position: scriptElement.getAttribute('data-position'),
            theme: scriptElement.getAttribute('data-theme'),
            debug: scriptElement.hasAttribute('data-debug')
        };
        
        if (config.apiKey) {
            window.docsAssistant = new DocsAssistantWidget(config);
        }
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DocsAssistantWidget;
}
