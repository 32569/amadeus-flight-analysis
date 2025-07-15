import os
from datetime import datetime, timedelta
import pandas as pd
from amadeus import Client, ResponseError

# 1) Sukuriame Amadeus klientą iš ENV
amadeus = Client(
    client_id=os.environ["AMADEUS_CLIENT_ID"],
    client_secret=os.environ["AMADEUS_CLIENT_SECRET"]
)

# 2) Parametrai
origin = "IST"
dest = "ISB"
target_date = datetime.strptime("2025-09-04", "%Y-%m-%d")
offset = 3

# 3) Sudarome datų sąrašą
dates = [(target_date + timedelta(days=i)).strftime("%Y-%m-%d")
         for i in range(-offset, offset+1)]

# 4) Renkame duomenis
records = []
for date in dates:
    try:
        resp = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=dest,
            departureDate=date,
            adults=1,
            max=50
        )
        for offer in resp.data:
            records.append({
                "date": date,
                "origin": origin,
                "destination": dest,
                "price": offer["price"]["total"],
                "carrier": offer.get("validatingAirlineCodes", [None])[0],
                "offer_id": offer["id"]
            })
        print(f"[{date}] gauta {len(resp.data)} įrašų")
    except ResponseError as e:
        print(f"[{date}] klaida: {e}")

# 5) Į CSV
df = pd.DataFrame(records)
out = f"flights_{origin}_{dest}_{dates[0]}_to_{dates[-1]}.csv"
df.to_csv(out, index=False)
print("Išsaugota į:", out)
