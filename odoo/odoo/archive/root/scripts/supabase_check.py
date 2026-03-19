import requests
import json

token = "sbp_9aa105cc134904b74bea64212607cca42cf2d36d"
project_ref = "spdtwktxdalcfigzeqrz"

sql = """
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'ops'
ORDER BY table_name, ordinal_position;
"""

url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
payload = {"query": sql}

print(f"Checking existing ops schema in {project_ref}...")
response = requests.post(url, headers=headers, json=payload)

if response.status_code == 201 or response.status_code == 200:
    print(json.dumps(response.json(), indent=2))
else:
    print(f"Error {response.status_code}: {response.text}")
