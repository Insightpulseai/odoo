from odoo import http
from odoo.http import request
import os


class OdooOpsShell(http.Controller):
    @http.route("/odooops", type="http", auth="user", website=True)
    def shell(self, **kw):
        # QWeb shell with iframe/proxy to Next.js dashboard
        nextjs_url = os.getenv("NEXTJS_DASHBOARD_URL", "http://localhost:3000")
        return request.render("ipai_odooops_shell.shell", {
            "nextjs_url": nextjs_url,
        })

    @http.route("/odooops/healthz", type="http", auth="public")
    def healthz(self, **kw):
        return request.make_response("ok", [("Content-Type", "text/plain")])
