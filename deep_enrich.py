import json
import os
import httpx
import asyncio

# Mappatura dei tuoi set con i codici ufficiali dell'API
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
            if not os.path.exists(path):
                print(f"⚠️ Cartella {local_id} non trovata, salto...")
                continue
            
            print(f"🧬 Arricchimento dati in corso per {local_id.upper()}...")
            
            # Scarichiamo i dati certificati dall'archivio internazionale
            try:
                resp = await client.get(f"https://api.pokemontcg.io/v2/cards?q=set.id:{api_id}", timeout=60.0)
                if resp.status_code != 200:
                    print(f"❌ Errore API per {local_id}: {resp.status_code}")
                    continue
                    
                api_data = resp.json().get('data', [])
                
                with open(path, "r", encoding="utf-8") as f:
                    local_cards = json.load(f)

                for local_card in local_cards:
                    # Troviamo la corrispondenza esatta per numero di carta
                    num_solo = local_card["number"].split("/")[0]
                    match = next((c for c in api_data if c["number"] == num_solo), None)
                    
                    if match:
                        # 1. Dati Vitali
                        local_card["hp"] = match.get("hp", "N/A")
                        local_card["types"] = match.get("types", ["N/A"])
                        local_card["evolvesFrom"] = match.get("evolvesFrom", "N/A")
                        
                        # 2. Debolezze e Resistenze (Prendiamo la prima se esiste)
                        weakness = match.get("weaknesses", [{}])[0]
                        local_card["weakness"] = f"{weakness.get('type', 'N/A')} {weakness.get('value', '')}".strip()
                        
                        resistance = match.get("resistances", [{}])[0]
                        local_card["resistance"] = f"{resistance.get('type', 'N/A')} {resistance.get('value', '')}".strip()
                        
                        # 3. Costo Ritirata (FIXED: è già un numero nell'API)
                        local_card["retreat"] = str(match.get("convertedRetreatCost", 0))
                        
                        # 4. Attacchi e Regole (Il cuore del database)
                        local_card["attacks"] = match.get("attacks", [])
                        local_card["rules"] = match.get("rules", [])
                        
                        # 5. Illustrator e Rarity (Sincronizzazione finale)
                        local_card["illustrator"] = match.get("artist", local_card["illustrator"])
                        local_card["rarity"] = match.get("rarity", local_card["rarity"])

                # Salvataggio del JSON arricchito
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(local_cards, f, indent=4, ensure_ascii=False)
                print(f"✅ {local_id.upper()} completato con successo!")

            except Exception as e:
                print(f"❌ Errore critico su {local_id}: {e}")

if __name__ == "__main__":
    asyncio.run(enrich_all())