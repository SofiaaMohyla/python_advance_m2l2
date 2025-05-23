import requests


response = requests.post("http://127.0.0.1:8000/users/", json=
{"name": 'Vova', "email": "some_email@gmsil.com", "city":"Lviv"})

print(response.status_code)
print(response.json())