import requests
import json
import time
import sys

def set_projectId(project):
  if project == "ecom-react":
    projectId = "6faaa3bc-53e5-400a-a536-7d46e408d344"
  elif project == "poky":
    projectId = "bf1b49eb-0378-4bb6-8f86-24eea9c1dde3"
  else:
    print("NOT A VALID PROJECT NAME")
    sys.exit(-1)
  return projectId


def get_ids(projectId, version_name, sessionToken, server):

    url = server + "/api/projects/" + projectId + "/versions"
    payload={}
    headers = {
      'Authorization': f'Bearer {sessionToken}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    content = json.loads(response.text)
    print(content)
    for item in content['items']:
        versionName = item['versionName']
        if version_name == versionName:
            print("There is a version")
            versionId = item["_meta"]['href']
            versionId = versionId.rsplit('/', 1)[-1]
            print(versionId)
    return versionId

def get_session_token(token):
  print("session token is being run")
  url = server + "/api/tokens/authenticate"
  print(url)
  payload={}
  headers = {
    'Content-Type': 'application/json',
    'Authorization': f'token {token}'
  }
  
  response = requests.request("POST", url, headers=headers, data=payload)
  sessionToken = json.loads(response.text)
  sessionToken = sessionToken['bearerToken']
  print(sessionToken)
  return sessionToken
   
try:
    print("Starting the generation")
    projectName = str(sys.argv[1])
    projectName = projectName.lower()
    versionName = str(sys.argv[2])
    versionName = versionName.lower()
    token = str(sys.argv[3])
    server = str(sys.argv[4])

    sessionToken = get_session_token(token)
    projectId = set_projectId(projectName)
    versionId = get_ids(projectId, versionName, sessionToken, server)
    

except:
  print("error")

url = server + "/api/versions/" + versionId + "/license-reports"
payload = json.dumps({
  "reportFormat": "TEXT",
  "reportType": "VERSION_LICENSE"
})
headers = {
  'Authorization': f'Bearer {sessionToken}',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
values_url = server + "/api/projects/" + projectId + "/versions/" + versionId + "/reports"


time.sleep(150)
values = requests.request("GET", values_url, headers=headers, data=payload)
print("Waiting for report generation .......")
values = json.loads(values.text)

print("Getting content url .......")
content_url = values['items'][1]['_meta']['links'][0]['href']
print("Getting the content for LICENSE.txt .........")

content = requests.request("GET", content_url, headers=headers, data=payload)

content_text = json.loads(content.text)
lic_text = content_text['reportContent'][0]['fileContent']


with open('LICENSE.txt', 'w') as f:
    print(lic_text, file=f)