# -*- coding: utf-8 -*-
"""
Override auth_oauth login to fix redirect_uri scheme behind reverse proxy.

ACA terminates TLS and forwards HTTP to the container. Odoo's proxy_mode
requires X-Forwarded-Host to apply ProxyFix, but ACA may not send it
consistently. This override uses web.base.url instead of url_root to
build the OAuth redirect_uri, ensuring https:// is always used.
"""
import json
import logging

import werkzeug.urls

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.auth_oauth.controllers.main import OAuthLogin

    class OAuthLoginHttpsFix(OAuthLogin):

        def list_providers(self):
            providers = super().list_providers()
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
            if not base_url.startswith('https://'):
                return providers

            for provider in providers:
                auth_link = provider.get('auth_link', '')
                if not auth_link:
                    continue

                # Replace http:// redirect_uri with https:// from web.base.url
                http_redirect = 'redirect_uri=http%3A%2F%2F'
                https_redirect = 'redirect_uri=https%3A%2F%2F'
                if http_redirect in auth_link:
                    auth_link = auth_link.replace(http_redirect, https_redirect)

                # Also fix the state parameter which embeds the redirect URL
                try:
                    parts = auth_link.split('state=', 1)
                    if len(parts) == 2:
                        state_and_rest = parts[1].split('&', 1)
                        state_encoded = state_and_rest[0]
                        state_json = werkzeug.urls.url_unquote(state_encoded)
                        state_obj = json.loads(state_json)
                        if 'r' in state_obj and 'http://' in state_obj['r']:
                            state_obj['r'] = state_obj['r'].replace('http://', 'https://')
                            new_state = werkzeug.urls.url_quote(json.dumps(state_obj))
                            auth_link = parts[0] + 'state=' + new_state
                            if len(state_and_rest) > 1:
                                auth_link += '&' + state_and_rest[1]
                except Exception:
                    _logger.debug('Could not fix OAuth state parameter', exc_info=True)

                provider['auth_link'] = auth_link

            return providers

except ImportError:
    # auth_oauth not installed
    pass
