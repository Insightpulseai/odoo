from odoo import http
from odoo.addons.auth_oauth.controllers.main import OAuthLogin


class OAuthLoginHttpsFix(OAuthLogin):
    """
    Thin override to force HTTPS callback generation for OAuth providers
    when Odoo is deployed behind Azure reverse proxies / ACA ingress.

    Goal:
    - keep the override narrow
    - avoid patching core files in the image
    - preserve default auth_oauth behavior except redirect URI scheme normalization

    Exit condition:
    - remove this addon once Azure Front Door / forwarded-proto edge contract
      produces correct HTTPS callback URLs natively
    """

    def list_providers(self):
        providers = super().list_providers()

        for provider in providers:
            auth_link = provider.get("auth_link")
            if isinstance(auth_link, str):
                provider["auth_link"] = auth_link.replace(
                    "redirect_uri=http%3A%2F%2F",
                    "redirect_uri=https%3A%2F%2F",
                    1,
                )
        return providers
