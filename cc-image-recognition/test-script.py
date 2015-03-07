import requests
import subprocess
import re
import time

#server = subprocess.Popen(['python', 'card-rec-server.py', 'train.jpg', 'train.tsv'])

def query(filepath):
    base_url = "http://127.0.0.1:5000/"
    with open(filepath, 'rb') as file:
        r = requests.post(base_url, files={'image': file})
        return r.text

#pattern = re.compile("\{.*?\}")
#while not query("test3.jpg").match(pattern): sleep(1)
#time.sleep(5)

print query("test3.jpg")
print query("test4.jpg")
print query("test5.jpg")
print query("test6.jpg")
print query("test7.jpg")

