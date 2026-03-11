import xmlrpc.client
import ssl

url = "https://erp.insightpulseai.com"
db = "odoo_core"  # Trying likely candidate
username = "admin"
password = "UbQbX75Wi+P3R+bItzO/NapptGbL4n/9MvIDVw71Oww="  # As found in .env.production

# Ignore SSL verification context if needed (though prod should be valid)
context = ssl._create_unverified_context()

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", context=context)

print(f"Connecting to {url}...")
try:
    version = common.version()
    print("Server Version:", version)

    # Try filtering dbs? No, verify login.
    uid = common.authenticate(db, username, password, {})
    if uid:
        print(f"SUCCESS: Authenticated as UID {uid} on DB {db}")
    else:
        print(f"FAIL: Authentication failed for {username} on {db}")

except Exception as e:
    print(f"ERROR: {e}")
