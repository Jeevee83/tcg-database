import json
import os

# Lista dei set da correggere
SETS_TO_FIX = ["fossil", "team-rocket", "gym-heroes", "gym-challenge"]

def fix_all_data():
    for set_id in SETS_TO_FIX:
        path = f"data/{set_id}/database.json"
        if not os.path.exists(path):
            print(f"⚠️ Saltato {set_id}: file non trovato.")
            continue

        with open(path, "r", encoding="utf-8") as f:
            cards = json.load(f)

        for card in cards:
            # Prendiamo il numero della carta (es: 1/62 -> 1)
            num = int(card["number"].split("/")[0])
            
            # 1. LOGICA CATEGORIE (Pokemon / Trainer / Energy)
            # Metodo onesto: cerchiamo parole chiave nel nome o usiamo i range ufficiali
            name = card["name"].lower()
            
            if "energy" in name:
                card["category"] = "Energy"
            elif any(x in name for x in ["trainer", "ball", "search", "pokedex", "oak", "bill", "removal", "potion", "doll", "scoop", "maintenance"]):
                card["category"] = "Trainer"
            else:
                # Per i Gym Set, i trainer iniziano dopo un certo numero.
                # Se non è energia o un trainer noto, è un Pokémon.
                card["category"] = "Pokémon"

            # 2. LOGICA RARITÀ (Per i set dove Serebii ha fallito)
            if card["rarity"] == "N/A":
                # Assegnazione generica basata sulla posizione (approssimativa per Gen1)
                if num <= 16: card["rarity"] = "Rare Holo"
                elif num <= 32: card["rarity"] = "Rare"
            
            # Pulizia nome artista
            card["illustrator"] = card["illustrator"].replace("Illustration:", "").strip()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(cards, f, indent=4, ensure_ascii=False)
        print(f"✅ Database {set_id} consolidato!")

if __name__ == "__main__":
    fix_all_data()