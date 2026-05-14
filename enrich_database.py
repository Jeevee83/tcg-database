import json
import os

def enrich_data():
    # COORDINATE DEFINITIVE E CERTIFICATE (WotC Canon)
    config = {
        "base-set":     {"pkm": 69,  "train": 95,  "total": 102},
        "jungle":       {"pkm": 63,  "train": 64,  "total": 64},
        "fossil":       {"pkm": 60,  "train": 62,  "total": 62},
        "team-rocket":  {"pkm": 70,  "train": 82,  "total": 83}, # 17 is Energy, 83 is Secret Pkm
        "gym-heroes":   {"pkm": 96,  "train": 126, "total": 132}, # Trainers start at 97
        "gym-challenge": {"pkm": 100, "train": 126, "total": 132}  # Trainers start at 101
    }

    for set_id, limits in config.items():
        path = f"data/{set_id}/database.json"
        if not os.path.exists(path): continue

        with open(path, "r", encoding="utf-8") as f:
            cards = json.load(f)

        for card in cards:
            num = int(card["number"].split("/")[0])
            
            # --- FIX CATEGORIA ---
            if set_id == "team-rocket" and num == 17: card["category"] = "Energy"
            elif set_id == "team-rocket" and num == 83: card["category"] = "Pokémon"
            elif num <= limits["pkm"]: card["category"] = "Pokémon"
            elif num <= limits["train"]: card["category"] = "Trainer"
            else: card["category"] = "Energy"

            # --- ARRICCHIMENTO CAMPI (Placeholder per dati tecnici) ---
            # Inizializziamo i campi se non esistono
            card["type"] = card.get("type", "Normal")
            card["stage"] = "Basic" if card["category"] == "Pokémon" else "N/A"
            card["weakness"] = card.get("debolezza", "N/A")
            card["resistance"] = card.get("resistenza", "N/A")
            card["retreat"] = card.get("ritirata", "N/A")
            # Pulizia finale illustrator
            card["illustrator"] = card["illustrator"].replace("Illustration:", "").strip()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(cards, f, indent=4, ensure_ascii=False)
        print(f"💎 {set_id.upper()} arricchito e corretto.")

if __name__ == "__main__":
    enrich_data()