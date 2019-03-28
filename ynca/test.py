#!/usr/bin/env python

import requests

print "it's testing ..."

r = requests.post('http://192.168.2.70:5001/face/image/matchN', data = {'data':"xx"} )