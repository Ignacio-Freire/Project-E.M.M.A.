import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

json_key = json.load(open('')) #Insert json with key
scope = ['https://spreadsheets.google.com/feeds']
credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
gc = gspread.authorize(credentials)

sht = gc.open_by_key('1uVvqxtRWIBN8foiBLPFNVzRog-97ZXRlX7KpNA47GlM').sheet1

sht.update_acell('B16', 'Te cambio todo')
print(sht.acell('A1'))
