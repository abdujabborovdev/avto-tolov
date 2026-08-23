import requests

URL = 'https://seensms.uz/api/v1'

r = requests.post(URL, data={
    'key':'TOwvqejSqTUCzmIrN8f6jCFC10Z5wIpR', 'action':'cancel',
    'order':734580
})
print(r.json())