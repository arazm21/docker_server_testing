# import certifi

# print(certifi.where())

# import requests

# url = 'https://example.com/api/endpoint'
# response = requests.get(url)
# print(response.status_code)
import requests

url = "https://wttr.in/Tbilisi?format=j1"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)