import os
from datetime import datetime, timezone
import pandas as pd
from amadeus import Client, ResponseError

# 1) Inicializuojame Amadeus klientą per ENV kintamuosius
amadeus = Client(
    client_id=os.environ["AMADEUS_CLIENT_ID"],
    client_secret=os.environ["AMADEUS_CLIENT_SECRET"]
)

# 2) Parametrai – tik viena data
origin = "IST"
dest = "ISB"
departure_date = "2025-09-04"

# 3) Paruošiame esamą CSV arba naują tuščią DataFrame
output_file = "flights_data.csv"
if os.path.exists(output_file):
    df_existing = pd.read_csv(output_file)
else:
    df_existing = pd.DataFrame(columns=[
        "date_checked",
        "departure_date",
        "from",
        "to",
        "price",
        "currency",
        "airline",
        "departure_time",
        "arrival_time",
        "offer_id"
    ])

# 4) Data, kada renkame (UTC-aware)
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# 5) Užklausiam skrydžių pasiūlymus
new_records = []
try:
    resp = amadeus.shopping.flight_offers_search.get(
        originLocationCode=origin,
        destinationLocationCode=dest,
        departureDate=departure_date,
        adults=1,
        max=50
    )
    # 6) Surūšiuojam pagal kainą (float) ir paimam max 3 pigiausius
    offers = resp.data
    offers_sorted = sorted(
        offers,
        key=lambda o: float(o["price"]["total"])
    )[:3]

    for offer in offers_sorted:
        seg
