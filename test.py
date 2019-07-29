import requests
import time
import json

USERNAME = 'devnetuser'
PASSWORD = 'Cisco123!'
HOST = 'sandboxdnac2.cisco.com'

USERNAME = 'wrog'
PASSWORD = 'SwedenR0x'
HOST = 'dnac.csapo.se'

def get_token():
    login_url = "https://{0}/api/system/v1/auth/token".format(HOST)
    result = requests.post(
                url=login_url, auth=requests.auth.HTTPBasicAuth(
                    USERNAME, PASSWORD), verify=False)
    token = result.json()["Token"]
    return token

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1Y2U3MTJiMDhlZTY2MjAyZmEyZWI4ZjgiLCJhdXRoU291cmNlIjoiaW50ZXJuYWwiLCJ0ZW5hbnROYW1lIjoiVE5UMCIsInJvbGVzIjpbIjViNmNmZGZmNDMwOTkwMDA4OWYwZmYzNyJdLCJ0ZW5hbnRJZCI6IjViNmNmZGZjNDMwOTkwMDA4OWYwZmYzMCIsImV4cCI6MTU2Mzc5MjUzNiwidXNlcm5hbWUiOiJkZXZuZXR1c2VyIn0.mcnnaiKazgkJW4FrFPqwOS98dzoUp8s8js1HNrSGgdM"
#CSAPO 12:22
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1ZDFiMjIzZDg4MzkxMDAwMWFmMmVkOGMiLCJhdXRoU291cmNlIjoiZXh0ZXJuYWwiLCJ0ZW5hbnROYW1lIjoiVE5UMCIsInJvbGVzIjpbIjVhOGQxNGJjOTQ5ZjJkYTg2NDFiYTNkZSJdLCJ0ZW5hbnRJZCI6IjVhOGQxNGYwYWU3ODhlMDA4ZWMxNGVjYiIsImV4cCI6MTU2Mzc5NDUzNiwidXNlcm5hbWUiOiJ3cm9nIn0.6kmNZGl8HxWUa853i703cZV3uQPrEWV4Qg6aqPFx-JY"
EPOCH_TIME = int(time.time())*1000
# TOKEN = get_token()
# print(token)

POST_HEADERS = {
            'X-auth-token': TOKEN,
            'Content-Type': 'application/json'
        }

def _create_url(url):
        return "https://{host}{url}".format(host=HOST, url=url)

def _post_url(url, payload):
    url = _create_url(url)
    #print("Sending get request to {url}".format(url=url))
    payload = json.dumps(payload)
    return requests.post(
        url=url,
        headers=POST_HEADERS,
        data=payload,
        verify=False)

def get_hosts():
    payload = {
        "typeList": {
            "type": "SITE",
            "startTime": EPOCH_TIME - 300000,  # 5 mins
            "endTime": EPOCH_TIME,
            "timeAPITime": EPOCH_TIME
        },
        "option": "CLIENT",
        "selectedTypeIdList": [
            "__global__"
        ]
    }

    r = _post_url(
            '/api/assurance/v1/host/dash/healthdetail', payload=payload)
    return r.json().get('response')

def  count_hosts():
    sites = get_hosts()
    for site in sites:
        print(site)

count_hosts()
