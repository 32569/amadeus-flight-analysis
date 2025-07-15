import os
import pandas as pd
from datetime import datetime, timezone
from amadeus import Client, ResponseError

def main():
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

    # 5) Užklausiam skrydžių pasiūlymus ir imame 3 pigiausius
    new_records = []
    try:
        resp = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=dest,
            departureDate=departure_date,
            adults=1,
            max=50
        )
        # Rūšiuojame pagal kainą ir paimame 3 pigiausius
        offers_sorted = sorted(
            resp.data,
            key=lambda o: float(o["price"]["total"])
        )[:3]

        for offer in offers_sorted:
            seg = offer["itineraries"][0]["segments"][0]
            new_records.append({
                "date_checked":    today,
                "departure_date":  departure_date,
                "from":            origin,
                "to":              dest,
                "price":           offer["price"]["total"],
                "currency":        offer["price"]["currency"],
                "airline":         seg["carrierCode"],
                "departure_time":  seg["departure"]["at"],
                "arrival_time":    seg["arrival"]["at"],
                "offer_id":        offer["id"]
            })
        print(f"[{today}] Surinkta {len(new_records)} pigiausi pasiūlymai už {departure_date}")
    except ResponseError as e:
        print(f"[ERROR] Klaida užklausoje: {e}")

    # 6) Sudedame su senais, išmetame dubliukus ir įrašom atgal
    df_new = pd.DataFrame(new_records)
    df_all = pd.concat([df_existing, df_new], ignore_index=True)
    df_all.drop_duplicates(
        subset=["date_checked", "departure_date", "offer_id"],
        inplace=True
    )

    df_all.to_csv(output_file, index=False)
    print(f"Išsaugota {len(new_records)} naujų eilučių į {output_file}")

if __name__ == "__main__":
    main()
