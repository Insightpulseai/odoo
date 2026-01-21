import sys

# In 'odoo-bin shell', 'env' is already present in the local scope.
# But we wrap in a function to be clean, accepting 'env' as arg or relying on global.


def audit_email(env):
    target_email = "jgtolentino.rn@gmail.com"
    print(f"\n--- AUDIT START: {target_email} ---\n")

    # 1. OUTGOING (SMTP)
    print(">>> 1. OUTGOING (SMTP)")
    # Search by smtp_user exactly
    outgoing_servers = env["ir.mail_server"].search([("smtp_user", "=", target_email)])

    if not outgoing_servers:
        print(f"RESULT: NOT CONFIGURED (No ir.mail_server found for {target_email})")
    else:
        for srv in outgoing_servers:
            print(
                f"RECORD: ID={srv.id} Host={srv.smtp_host} Port={srv.smtp_port} User={srv.smtp_user} Encryption={srv.smtp_encryption} Active={srv.active}"
            )

            # Check Auth Method info (blind check)
            if (
                hasattr(srv, "google_gmail_access_token")
                and srv.google_gmail_access_token
            ):
                print("AUTH MODE: OAuth2 (Access Token present)")
            elif srv.smtp_pass:
                print("AUTH MODE: Password/App Password (Password field set)")
            else:
                print("AUTH MODE: Unknown/Missing Credentials")

            # Test Connection
            print("TESTING CONNECTION...")
            try:
                # test_smtp_connection returns None on success, raises error on failure
                srv.test_smtp_connection()
                print("TEST RESULT: PASS (Connection established)")
            except Exception as e:
                print(f"TEST RESULT: FAIL ({str(e)})")

    # 2. INCOMING (IMAP/POP)
    print("\n>>> 2. INCOMING (FETCHMAIL)")
    # fetchmail.server 'user' field holds the login
    incoming_servers = env["fetchmail.server"].search([("user", "=", target_email)])

    if not incoming_servers:
        print(f"RESULT: NOT CONFIGURED (No fetchmail.server found for {target_email})")
    else:
        for srv in incoming_servers:
            server_type = srv.server_type  # imap/pop
            is_ssl = srv.is_ssl
            print(
                f"RECORD: ID={srv.id} Host={srv.server} Port={srv.port} Type={server_type} SSL={is_ssl} User={srv.user} Active={srv.active}"
            )

            # Test Login
            print("TESTING LOGIN...")
            try:
                # button_confirm_login raises error if failed
                srv.button_confirm_login()
                print("TEST RESULT: PASS (Login successful)")
            except Exception as e:
                print(f"TEST RESULT: FAIL ({str(e)})")

    # 3. ALIAS CONFIG
    print("\n>>> 3. ALIAS / DOMAIN CHECK")
    alias_domain = env["ir.config_parameter"].sudo().get_param("mail.catchall.domain")
    print(f"mail.catchall.domain: {alias_domain}")

    # 4. SYSTEM PARAMETERS (OAUTH)
    print("\n>>> 4. OAUTH / GOOGLE PARAMS")
    keys = [
        "google_gmail_client_id",
        "google_gmail_client_secret",
        "google_redirect_uri",
    ]
    for k in keys:
        val = env["ir.config_parameter"].sudo().get_param(k)
        state = "SET" if val else "NOT SET"
        # Show partial if set
        preview = (val[:5] + "...") if val else "None"
        print(f"Param {k}: {state} ({preview})")


if __name__ == "__main__":
    # When running via 'odoo-bin shell < audit_email_config.py', the script executes in context.
    # 'env' is available globally in the shell console.
    if "env" in globals():
        audit_email(env)
    else:
        print("ERROR: This script must be run inside 'odoo-bin shell'.")
