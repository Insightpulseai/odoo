
import xmlrpc.client
import ssl

url = "https://erp.insightpulseai.net"
username = "admin"
password = "UbQbX75Wi+P3R+bItzO/NapptGbL4n/9MvIDVw71Oww=" 
context = ssl._create_unverified_context()
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=context)

dbs = ["odoo", "production", "ipai", "odoo18", "odoo-prod", "odoo_production"]

print(f"Target: {url}")
for db in dbs:
    try:
        uid = common.authenticate(db, username, password, {})
        if uid:
            print(f"SUCCESS: DB='{db}' UID={uid}")
            break
        else:
            print(f"FAIL: DB='{db}'")
    except Exception as e:
        print(f"ERROR: DB='{db}' - {e}")
