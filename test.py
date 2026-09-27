from data.config import SHOP_ID, SHOP_KEY
import requests
payload = {
        "method": "check",
        "order": '0d0ba0hwaw',
    "shop_key": SHOP_KEY,
    "amount": 1000,
    }
a=requests.get( "https://checkcard.uz/api",
                params=payload,
        )



print(a.json())