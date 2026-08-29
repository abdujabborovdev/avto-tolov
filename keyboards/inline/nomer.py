from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup

number_ols = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Raqamni olish✅',callback_data='nomer_ol')
    ]
])
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

COUNTRY_NAMES = {
    "CO": "Kolumbiya 🇨🇴", "US": "Amerika 🇺🇸", "IN": "Hindiston 🇮🇳", "BD": "Bangladesh 🇧🇩",
    "IR": "Eron 🇮🇷", "ID": "Indoneziya 🇮🇩", "PK": "Pokiston 🇵🇰", "CL": "Chili 🇨🇱",
    "KE": "Keniya 🇰🇪", "AO": "Angola 🇦🇴", "NP": "Nepal 🇳🇵", "AF": "Afg'oniston 🇦🇫",
    "ZW": "Zimbabve 🇿🇼", "MG": "Madagaskar 🇲🇬", "SD": "Sudan 🇸🇩", "TZ": "Tanzaniya 🇹🇿",
    "DZ": "Jazoir 🇩🇿", "JM": "Yamayka 🇯🇲", "LK": "Shri-Lanka 🇱🇰", "PL": "Polsha 🇵🇱",
    "SZ": "Esvatini 🇸🇿", "UG": "Uganda 🇺🇬", "BF": "Burkina-Faso 🇧🇫", "MR": "Mavritaniya 🇲🇷",
    "PR": "Puerto-Riko 🇵🇷", "AR": "Argentina 🇦🇷", "CU": "Kuba 🇨🇺", "MX": "Meksika 🇲🇽",
    "NI": "Nikaragua 🇳🇮", "JE": "Jersi 🇯🇪", "BW": "Botsvana 🇧🇼",
    "CG": "Kongo 🇨🇬", "MU": "Mavrikiy 🇲🇺", "GN": "Gvineya 🇬🇳", "MA": "Marokash 🇲🇦",
    "DO": "Dominikan Respublikasi 🇩🇴", "TJ": "Tojikiston 🇹🇯", "VN": "Vyetnam 🇻🇳", "MQ": "Martinika 🇲🇶",
    "BR": "Braziliya 🇧🇷", "HN": "Gonduras 🇭🇳", "SV": "Salvador 🇸🇻", "GB": "Buyuk Britaniya 🇬🇧",
    "GG": "Gernsi 🇬🇬", "NA": "Namibiya 🇳🇦", "SO": "Somali 🇸🇴", "GW": "Gvineya-Bisau 🇬🇼",
    "ML": "Mali 🇲🇱", "TM": "Turkmaniston 🇹🇲", "IL": "Isroil 🇮🇱",
    "SY": "Suriya 🇸🇾", "UY": "Urugvay 🇺🇾", "HT": "Gaiti 🇭🇹", "GT": "Gvatemala 🇬🇹",
    "CV": "Kabo-Verde 🇨🇻", "SN": "Senegal 🇸🇳", "GM": "Gambiya 🇬🇲", "VI": "Virgin orollari (AQSh) 🇻🇮",
    "VE": "Venesuela 🇻🇪", "EE": "Estoniya 🇪🇪", "DJ": "Jibuti 🇩🇯", "LR": "Liberiya 🇱🇷",
    "TN": "Tunis 🇹🇳", "KN": "Sent-Kits va Nevis 🇰🇳", "TT": "Trinidad va Tobago 🇹🇹", "GU": "Guam 🇬🇺",
    "GD": "Grenada 🇬🇩", "PF": "Fransuz Polineziyasi 🇵🇫", "TO": "Tonga 🇹🇴", "MY": "Malayziya 🇲🇾",
    "GY": "Gayana 🇬🇾", "KM": "Comoros 🇰🇲", "AG": "Antigua va Barbuda 🇦🇬", "BS": "Bagama orollari 🇧🇸",
    "SA": "Saudiya Arabistoni 🇸🇦", "LB": "Livan 🇱🇧", "CN": "Xitoy 🇨🇳", "KH": "Kambodja 🇰🇭",
    "SB": "Solomon orollari 🇸🇧", "PE": "Peru 🇵🇪", "TD": "Chad 🇹🇩", "PS": "Falastin 🇵🇸",
    "TR": "Turkiya 🇹🇷", "LA": "Laos 🇱🇦", "HK": "Gonkong 🇭🇰", "FM": "Mikroneziya 🇫🇲",
    "KI": "Kiribati 🇰🇮", "WS": "Samoa 🇼🇸", "FJ": "Fiji 🇫🇯", "VU": "Vanuatu 🇻🇺",
    "TL": "Sharqiy Timor 🇹🇱", "CW": "Kurasao 🇨🇼", "PY": "Paragvay 🇵🇾", "IT": "Italiya 🇮🇹",
    "MK": "Shimoliy Makedoniya 🇲🇰", "ME": "Chernogoriya 🇲🇪", "FI": "Finlandiya 🇫🇮", "GL": "Grenlandiya 🇬🇱",
    "ER": "Eritreya 🇪🇷", "MW": "Malavi 🇲🇼", "RE": "Reunion 🇷🇪", "YT": "Mayotta 🇾🇹",
    "SC": "Seyshel orollari 🇸🇨", "GA": "Gabon 🇬🇦", "GQ": "Ekvatorial Gvineya 🇬🇶", "ST": "San-Tome va Prinsipi 🇸🇹",
    "CI": "Kot-d'Ivuar 🇨🇮", "LY": "Liviya 🇱🇾", "VC": "Sent-Vinsent va Grenadin 🇻🇨", "DM": "Dominika 🇩🇲",
    "LC": "Sent-Lusiya 🇱🇨", "SX": "Sint-Marten 🇸🇽", "BM": "Bermuda orollari 🇧🇲", "IM": "Men oroli 🇮🇲",
    "TC": "Turks va Kaykos 🇹🇨", "KG": "Qirg'iziston 🇰🇬", "JO": "Iordaniya 🇯🇴", "KZ": "Qozog'iston 🇰🇿",
    "GP": "Gvadelupa 🇬🇵", "BZ": "Beliz 🇧🇿", "DE": "Germaniya 🇩🇪", "BA": "Bosniya va Gersegovina 🇧🇦",
    "AM": "Armaniston 🇦🇲", "FR": "Fransiya 🇫🇷", "MN": "Mongoliya 🇲🇳", "AL": "Albaniya 🇦🇱",
    "AW": "Aruba 🇦🇼", "SS": "Janubiy Sudan 🇸🇸", "BE": "Belgiya 🇧🇪", "AZ": "Ozarbayjon 🇦🇿",
    "MD": "Moldova 🇲🇩", "ES": "Ispaniya 🇪🇸", "BT": "Butan 🇧🇹", "MV": "Maldiv orollari 🇲🇻",
    "NC": "Yangi Kaledoniya 🇳🇨", "GF": "Gviana (Fransuz) 🇬🇫", "BO": "Boliviya 🇧🇴", "PM": "Sen-Pyer va Mikelon 🇵🇲",
    "CZ": "Chexiya 🇨🇿", "HR": "Xorvatiya 🇭🇷", "LU": "Lyuksemburg 🇱🇺", "GR": "Gretsiya 🇬🇷",
    "AS": "Amerika Samoasi 🇦🇸", "KY": "Kayman orollari 🇰🇾", "VG": "Britaniya Virgin orollari 🇻🇬", "OM": "Omon 🇴🇲",
    "KW": "Kuvayt 🇰🇼", "AU": "Avstraliya 🇦🇺", "LT": "Litva 🇱🇹", "NL": "Niderlandiya 🇳🇱",
    "MO": "Makao 🇲🇴", "JP": "Yaponiya 🇯🇵", "DK": "Daniya 🇩🇰", "NZ": "Yangi Zelandiya 🇳🇿",
    "WF": "Uollis va Futuna 🇼🇫", "NR": "Nauru 🇳🇷", "NO": "Norvegiya 🇳🇴", "UA": " Ukraina 🇺🇦",
    "MT": "Malta 🇲🇹", "AE": "Birlashgan A.A 🇦🇪", "QA": "Qatar 🇶🇦", "KR": "Janubiy Koreya 🇰🇷",
    "BH": "Bahrayn 🇧🇭", "NU": "Niue 🇳🇺", "BN": "Bruney 🇧🇳", "SG": "Singapur 🇸🇬",
    "GI": "Gibraltar 🇬🇮"
}


def generate_countries_keyboard(country_data, page: int = 0):

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    PER_PAGE = 10
    start = page * PER_PAGE
    end = start + PER_PAGE

    page_data = country_data[start:end]
    row = []

    for id_, country_code, price in page_data:
        country_name = COUNTRY_NAMES.get(country_code, country_code)
        button_text = f"{country_name} | {price} so'm"

        row.append(InlineKeyboardButton(text=button_text, callback_data=f"country:{country_code}"))

        if len(row) == 2:
            keyboard.inline_keyboard.append(row)
            row = []

    if row:
        keyboard.inline_keyboard.append(row)

    nav_buttons = []

    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"countries_page:{page - 1}"))

    if end < len(country_data):
        nav_buttons.append(InlineKeyboardButton(text="Oldinga ➡️", callback_data=f"countries_page:{page + 1}"))

    if nav_buttons:
        keyboard.inline_keyboard.append(nav_buttons)

    return keyboard

def buy_number(country:str,price:int,tg_id:int):
    keyboards= InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Tasdiqlash ✅',callback_data=f"buy_number:{country}:{price}:{tg_id}")
        ]
    ])
    return keyboards

def check_number(order_id:str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
         InlineKeyboardButton(text='📲SMS olish',callback_data=f"check_number:{order_id}")
        ]
    ])
    return keyboard