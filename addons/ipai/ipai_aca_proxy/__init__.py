"""
Azure Container Apps proxy header bridge.

ACA's Envoy ingress sends:
  - X-Forwarded-Proto (http or https)
  - X-Forwarded-For (client IP)

ACA does NOT send:
  - X-Forwarded-Host

Odoo's ProxyFix guard (odoo/http.py Root.__call__) checks:
    if config['proxy_mode'] and environ.get('HTTP_X_FORWARDED_HOST'):
        ProxyFix(...)

Without X-Forwarded-Host, ProxyFix never activates, so
X-Forwarded-Proto is ignored and the WSGI scheme stays 'http'.

This module monkey-patches Root.__call__ to copy HTTP_HOST into
HTTP_X_FORWARDED_HOST when the forwarded-proto header is present
but forwarded-host is missing. This satisfies Odoo's guard condition
and allows ProxyFix to set the correct scheme from X-Forwarded-Proto.
"""
import logging

_logger = logging.getLogger(__name__)


def _aca_proxy_post_load():
    """Called by Odoo after this server-wide module is loaded."""
    import odoo.http  # noqa: delay import until post_load

    Application = odoo.http.Application
    _original_call = Application.__call__

    def _patched_call(self, environ, start_response):
        # When ACA sends X-Forwarded-Proto but not X-Forwarded-Host,
        # inject X-Forwarded-Host from the Host header so that Odoo's
        # ProxyFix guard at http.py:2778 activates correctly.
        if (environ.get('HTTP_X_FORWARDED_PROTO')
                and not environ.get('HTTP_X_FORWARDED_HOST')
                and environ.get('HTTP_HOST')):
            environ['HTTP_X_FORWARDED_HOST'] = environ['HTTP_HOST']
        return _original_call(self, environ, start_response)

    Application.__call__ = _patched_call
    _logger.info(
        "ipai_aca_proxy: patched Application.__call__ to inject "
        "X-Forwarded-Host from Host header for ACA compatibility"
    )
