import os
from datetime import datetime, timedelta, timezone
import pandas as pd
from amadeus import Client, ResponseError

# 1) Amadeus client iš ENV kintamųjų
amadeus = Client(
    client_id=os.environ["AMADEUS_CLIENT_ID"],
    client_secret=os.environ["AMADEUS_CLIENT_SECRET"]
)

# 2) Parametrai
origin = "IST"
dest = "ISB"
target_date = datetime.strptime("2025-09-04", "%Y-%m-%d")
offset = 3

# 3) Datų sąrašas
dates = [
    (target_date + timedelta(days=i)).strftime("%Y-%m-%d")
    for i in range(-offset, offset + 1)
]

# 4) Esamas CSV (arba šablonas naujam)
output_file = "flights_data.csv"
if os.path.exists(output_file):
    df_existing = pd.read_csv(output_file)
else:
    df_existing = pd.DataFrame(columns=[
        "date_checked","departure_date","from","to",
        "price","currency","airline","departure_time","arrival_time","offer_id"
    ])

# 5) Surenkame duomenis
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
new_records = []

for dep_date in dates:
    try:
        resp = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=dest,
            departureDate=dep_date,
            adults=1,
            max=50
        )
        for offer in resp.data:
            seg = offer["itineraries"][0]["segments"][0]
            new_records.append({
                "date_checked": today,
                "departure_date": dep_date,
                "from": origin,
                "to": dest,
                "price": offer["price"]["total"],
                "currency": offer["price"]["currency"],
                "airline": seg["carrierCode"],
                "departure_time": seg["departure"]["at"],
                "arrival_time": seg["arrival"]["at"],
                "offer_id": offer["id"]
            })
    except ResponseError as e:
        print(f"[{dep_date}] Klaida: {e}")

# 6) Lyginame, sukuriame galutinį DataFrame
df_new = pd.DataFrame(new_records)
df_all = pd.concat([df_existing, df_new], ignore_index=True)
df_all.drop_duplicates(subset=["date_checked","departure_date","offer_id"], inplace=True)

# 7) Išsaugome CSV
df_all.to_csv(output_file, index=False)
print(f"Išsaugota {len(df_new)} naujų eilučių į {output_file}")
