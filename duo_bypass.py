import pyotp
import requests
import base64
import sys

if len(sys.argv) < 2:
    print("Usage: python duo_bypass.py <url to duo qr>")
    exit()

qr_url = sys.argv[1]
hostb64 = qr_url.split('-')[1]
host = base64.b64decode(hostb64 + '='*(-len(hostb64) % 4), )
host = host.decode('ascii')
code = qr_url.split('-')[0].replace('duo://', '')

url = f'https://{host}/push/v2/activation/{code}')
response = requests.post(url).json()
print(response)

secret = base64.b32encode(response['response']['hotp_secret'].encode())

hotp = pyotp.HOTP(secret)
for _ in range(10):
    print(hotp.at(_))