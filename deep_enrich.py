import json
import os
import httpx
import asyncio
import re

SETS_MAP = {
    "base-set": "base1",
    "jungle": "base2",
    "fossil": "base3",
    "team-rocket": "base4",
    "gym-heroes": "gym1",
    "gym-challenge": "gym2"
}

def normalize(text):
    """Semplifica il nome per il confronto (es: 'Dark Alakazam' -> 'darkalakazam')"""
    return re.sub(r'[^a-z0-9]', '', text.lower())

async def enrich_all():
    async with httpx.AsyncClient() as client:
        for local_id, api_id in SETS_MAP.items():
            path = f"data/{local_id}/database.json"
            if not os.path.exists(path): continue
            
            print(f"🧬 Arricchimento di precisione per {local_id.upper()}...")
            
            try:
                # Scarichiamo i dati del set specifico
                resp = await client.get(f"https://api.pokemontcg.io/v2/cards?q=set.id:{api_id}", timeout=60.0)
                api_data = resp.json().get('data', [])
                
                with open(path, "r", encoding="utf-8") as f:
                    local_cards = json.load(f)

                for local_card in local_cards:
                    num_solo = local_card["number"].split("/")[0]
                    local_name_norm = normalize(local_card["name"])
                    
                    # CERCA IL MATCH PERFETTO: Numero + Nome
                    match = next((c for c in api_data if c["number"] == num_solo and normalize(c["name"]) == local_name_norm), None)
                    
                    # Se non trova il nome esatto (es. Nidoran), prova solo per numero nel set corretto
                    if not match:
                        match = next((c for c in api_data if c["number"] == num_solo), None)

                    if match:
                        # RESET DATI (Per pulire gli errori precedenti)
                        local_card["hp"] = "N/A"
                        local_card["attacks"] = []
                        local_card["rules"] = []
                        local_card["weakness"] = "N/A"
                        local_card["resistance"] = "N/A"
                        local_card["retreat"] = "0"

                        # ASSEGNAZIONE SOLO SE PERTINENTE
                        if local_card["category"] == "Pokémon":
                            local_card["hp"] = match.get("hp", "N/A")
                            local_card["types"] = match.get("types", ["N/A"])
                            local_card["attacks"] = match.get("attacks", [])
                            
                            if match.get("weaknesses"):
                                w = match["weaknesses"][0]
                                local_card["weakness"] = f"{w['type']} {w['value']}"
                            
                            if match.get("resistances"):
                                r = match["resistances"][0]
                                local_card["resistance"] = f"{r['type']} {r['value']}"
                            
                            local_card["retreat"] = str(match.get("convertedRetreatCost", 0))
                        
                        else:
                            # È un Trainer o Energy: prendiamo solo le regole (rules)
                            local_card["rules"] = match.get("rules", [])

                with open(path, "w", encoding="utf-8") as f:
                    json.dump(local_cards, f, indent=4, ensure_ascii=False)
                print(f"✅ {local_id.upper()} sincronizzato correttamente.")

            except Exception as e:
                print(f"❌ Errore su {local_id}: {e}")

if __name__ == "__main__":
    asyncio.run(enrich_all())