import requests

reponse = requests.get("https://www.futuretools.io/")
print(reponse.text)