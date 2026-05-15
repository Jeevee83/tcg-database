import json
import os
import httpx
import asyncio

SETS_MAP = {
    "base-set": "base1",
    "jungle": "base2",
    "fossil": "base3",
    "team-rocket": "base4",
    "gym-heroes": "gym1",
    "gym-challenge": "gym2"
}

async def enrich_all():
    async with httpx.AsyncClient() as client:
        for local_id, api_id in SETS_MAP.items():
            path = f"data/{local_id}/database.json"
            if not os.path.exists(path): continue
            
            print(f"🧹 Pulizia e Arricchimento certificato per {local_id.upper()}...")
            
            try:
                # Scarichiamo TUTTE le carte del set specifico dall'API ufficiale
                resp = await client.get(f"https://api.pokemontcg.io/v2/cards?q=set.id:{api_id}", timeout=60.0)
                api_cards = resp.json().get('data', [])
                
                # Creiamo un dizionario veloce { "numero": dati_api }
                api_map = { c["number"]: c for c in api_cards }
                
                with open(path, "r", encoding="utf-8") as f:
                    local_database = json.load(f)

                for local_card in local_database:
                    num_solo = local_card["number"].split("/")[0]
                    
                    # Cerchiamo il match solo per numero dentro il set corretto
                    match = api_map.get(num_solo)

                    if match:
                        # Sovrascrittura totale per eliminare errori precedenti
                        local_card["hp"] = match.get("hp", "N/A")
                        local_card["illustrator"] = match.get("artist", "N/A")
                        local_card["rarity"] = match.get("rarity", "N/A")
                        local_card["category"] = match.get("supertype", "N/A")
                        
                        # Reset e aggiornamento dati tecnici
                        local_card["attacks"] = match.get("attacks", [])
                        local_card["rules"] = match.get("rules", [])
                        local_card["types"] = match.get("types", [])
                        
                        # Debolezza
                        if match.get("weaknesses"):
                            w = match["weaknesses"][0]
                            local_card["weakness"] = f"{w['type']} {w['value']}"
                        else: local_card["weakness"] = "N/A"

                        # Resistenza
                        if match.get("resistances"):
                            r = match["resistances"][0]
                            local_card["resistance"] = f"{r['type']} {r['value']}"
                        else: local_card["resistance"] = "N/A"

                        # Ritirata
                        local_card["retreat"] = str(match.get("convertedRetreatCost", 0))

                with open(path, "w", encoding="utf-8") as f:
                    json.dump(local_database, f, indent=4, ensure_ascii=False)
                print(f"✅ {local_id.upper()} aggiornato con successo.")

            except Exception as e:
                print(f"❌ Errore su {local_id}: {e}")

if __name__ == "__main__":
    asyncio.run(enrich_all())