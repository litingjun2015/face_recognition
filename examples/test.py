
import requests 

print "testing..."

url = 'http://192.168.2.70:5001/face/image/matchN'

files = {'file': open('./pics/litingjun.jpg', 'rb')}
r = requests.post(url, files=files)
print r.text