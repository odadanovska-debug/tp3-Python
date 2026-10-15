# serveur des records (back-end)
# - garde tous les scores dans records.json
# - envoie le top 5 à chaque joueur connecté, en temps réel
# lancer avec : python server.py

import asyncio
import json
import os
from datetime import datetime

import websockets

FICHIER_RECORDS = "records.json"
TAILLE_TOP = 5

joueurs = set()  # toutes les fenêtres de jeu connectées


def charger_records() -> list[dict]:
    if not os.path.exists(FICHIER_RECORDS):
        return []
    with open(FICHIER_RECORDS, "r", encoding="utf-8") as f:
        return json.load(f)


def sauver_records(records: list[dict]) -> None:
    with open(FICHIER_RECORDS, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def top(records: list[dict]) -> list[dict]:
    # les meilleurs scores, du plus grand au plus petit
    tries = sorted(records, key=lambda r: r["score"], reverse=True)
    return tries[:TAILLE_TOP]


async def gerer_joueur(websocket):
    joueurs.add(websocket)
    print(f"un joueur se connecte ({len(joueurs)} en ligne)")
    try:
        # dès qu'il arrive, on lui envoie le top actuel
        await websocket.send(json.dumps({"top": top(charger_records())}))

        # puis on attend les scores qu'il envoie
        async for message in websocket:
            try:
                data = json.loads(message)
                pseudo = str(data["pseudo"])[:12]
                score = int(data["score"])
            except (json.JSONDecodeError, KeyError, ValueError):
                print("message ignoré (format incorrect) :", message)
                continue

            records = charger_records()
            nouveau = {"pseudo": pseudo, "score": score,
                       "date": datetime.now().isoformat(timespec="seconds")}
            records.append(nouveau)
            sauver_records(records)
            print(f"score reçu : {pseudo} -> {score}")

            # est-ce que ce score entre dans le top ?
            nouveau_top = top(records)
            entre_dans_le_top = nouveau in nouveau_top

            # on prévient tout le monde en même temps
            websockets.broadcast(joueurs, json.dumps({
                "top": nouveau_top,
                "nouveau": pseudo if entre_dans_le_top else None,
            }))
    except websockets.ConnectionClosed:
        pass  # le joueur a fermé sa fenêtre
    finally:
        joueurs.discard(websocket)
        print(f"un joueur part ({len(joueurs)} en ligne)")


async def main():
    async with websockets.serve(gerer_joueur, "localhost", 8765):
        print("serveur des records lancé sur ws://localhost:8765")
        await asyncio.Future()  # tourne pour toujours


if __name__ == "__main__":
    asyncio.run(main())
