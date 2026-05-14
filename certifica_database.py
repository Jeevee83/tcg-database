import json
import os

def certifica_dati():
    sets_config = {
        "base-set": {"total": 102, "pkm_max": 69, "trainer_max": 95},
        "jungle": {"total": 64, "pkm_max": 63, "trainer_max": 64},
        "fossil": {"total": 62, "pkm_max": 60, "trainer_max": 62},
        "team-rocket": {"total": 83, "pkm_max": 70, "trainer_max": 82},
        "gym-heroes": {"total": 132, "pkm_max": 99, "trainer_max": 126},
        "gym-challenge": {"total": 132, "pkm_max": 100, "trainer_max": 126}
    }

    for set_id, limits in sets_config.items():
        path = f"data/{set_id}/database.json"
        if not os.path.exists(path): continue

        with open(path, "r", encoding="utf-8") as f:
            cards = json.load(f)

        for card in cards:
            num = int(card["number"].split("/")[0])
            
            # 1. CATEGORIA CERTIFICATA
            if set_id == "team-rocket" and num == 17:
                card["category"] = "Energy" # Rainbow Energy Holo
            elif num <= limits["pkm_max"]:
                card["category"] = "Pokémon"
            elif num <= limits["trainer_max"]:
                card["category"] = "Trainer"
            else:
                card["category"] = "Energy"

            # 2. RARITÀ CERTIFICATA (Standard WotC)
            if set_id in ["base-set", "jungle", "fossil", "team-rocket"]:
                if num <= (16 if set_id != "team-rocket" else 17): card["rarity"] = "Rare Holo"
                elif num <= (22 if set_id == "base-set" else 32 if set_id == "jungle" else 30): card["rarity"] = "Rare"
            
            # Casi speciali per Dark Raichu (Rocket #83)
            if set_id == "team-rocket" and num == 83:
                card["category"] = "Pokémon"
                card["rarity"] = "Rare Holo (Secret)"

            # Correzione Gym Sets (Heroes & Challenge)
            if "gym-" in set_id:
                if num <= (19 if set_id == "gym-heroes" else 20): card["rarity"] = "Rare Holo"
                elif num <= 100: card["rarity"] = "Rare"
                elif num <= 126: card["rarity"] = "Uncommon"
                else: card["rarity"] = "Common"

            # 3. PULIZIA EXTRA
            card["name"] = card["name"].replace("Maintanence", "Maintenance")
            card["illustrator"] = card["illustrator"].replace("Illustration:", "").strip()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(cards, f, indent=4, ensure_ascii=False)
        print(f"✅ {set_id.upper()} certificato con successo!")

if __name__ == "__main__":
    certifica_dati()