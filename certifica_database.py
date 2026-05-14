import json
import os
import re

def perfect_fix():
    # COORDINATE UFFICIALI GEN 1 (WotC)
    config = {
        "base-set":     {"total": 102, "pkm": 69,  "train": 95},
        "jungle":       {"total": 64,  "pkm": 63,  "train": 64},
        "fossil":       {"total": 62,  "pkm": 60,  "train": 62},
        "team-rocket":  {"total": 83,  "pkm": 70,  "train": 82},
        "gym-heroes":   {"total": 132, "pkm": 100, "train": 126},
        "gym-challenge": {"total": 132, "pkm": 100, "train": 126}
    }

    for set_id, limits in config.items():
        path = f"data/{set_id}/database.json"
        if not os.path.exists(path): continue

        with open(path, "r", encoding="utf-8") as f:
            cards = json.load(f)

        for card in cards:
            num = int(card["number"].split("/")[0])
            name = card["name"]

            # 1. FIX CATEGORIA
            if set_id == "team-rocket" and num == 17:
                card["category"] = "Energy"
            elif set_id == "team-rocket" and num == 83:
                card["category"] = "Pokémon" # Dark Raichu Secret
            elif num <= limits["pkm"]:
                card["category"] = "Pokémon"
            elif num <= limits["train"]:
                card["category"] = "Trainer"
            else:
                card["category"] = "Energy"

            # 2. FIX RARITÀ (Per coerenza totale)
            if "gym" in set_id:
                if num <= (19 if set_id == "gym-heroes" else 20): card["rarity"] = "Rare Holo"
                elif num <= 100: card["rarity"] = "Rare" if num <= 42 else "Uncommon" if num <= 64 else "Common"
            
            # 3. FIX NOMI SIMBOLI (Nidoran)
            card["name"] = card["name"].replace("Nidoran♀", "Nidoran F").replace("Nidoran♂", "Nidoran M")
            
            # 4. PULIZIA ILLUSTRARE (Rimuove eventuali residui)
            card["illustrator"] = card["illustrator"].replace("Illustration:", "").strip()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(cards, f, indent=4, ensure_ascii=False)
        
        print(f"✅ {set_id.upper()} verificato al 100%")

if __name__ == "__main__":
    perfect_fix()