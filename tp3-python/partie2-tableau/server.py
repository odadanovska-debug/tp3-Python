# serveur du tableau interactif
# - api http : POST /draw pour demander une forme, POST /clear pour tout effacer
# - websocket /ws : les pages web des tableaux s'y connectent
# à chaque forme reçue, on la renvoie à tous les tableaux connectés
# lancer avec : python server.py   puis ouvrir http://localhost:8000

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI()

tableaux = []     # les pages web connectées
historique = []   # toutes les formes déjà dessinées (pour les nouveaux tableaux)

# les champs obligatoires pour chaque forme (voir la doc du sujet)
CHAMPS = {
    "point": ["x", "y"],
    "line": ["x1", "y1", "x2", "y2"],
    "circle": ["x", "y", "radius"],
    "rectangle": ["x", "y", "width", "height"],
    "square": ["x", "y", "cote"],
}


def verifier_forme(forme: dict) -> str | None:
    # renvoie un message d'erreur, ou None si la forme est correcte
    shape = forme.get("shape")
    if shape not in CHAMPS:
        return f"forme inconnue : {shape} (formes possibles : {', '.join(CHAMPS)})"

    for champ in CHAMPS[shape]:
        if not isinstance(forme.get(champ), (int, float)):
            return f"le champ '{champ}' est manquant ou n'est pas un nombre"

    couleur = forme.get("color")
    if not isinstance(couleur, list) or len(couleur) != 3:
        return "la couleur doit être [r, g, b]"
    for valeur in couleur:
        if not isinstance(valeur, int) or not 0 <= valeur <= 255:
            return "chaque valeur de couleur doit être un entier entre 0 et 255"

    return None


async def envoyer_a_tous(message: dict) -> None:
    # on envoie le message à chaque tableau
    # si un tableau a été fermé entre temps, on le retire de la liste
    for tableau in tableaux.copy():
        try:
            await tableau.send_json(message)
        except Exception:
            tableaux.remove(tableau)


# ---------- la page web ----------

@app.get("/")
def page():
    return FileResponse("index.html")


# ---------- api http ----------

@app.post("/draw")
async def draw(forme: dict):
    erreur = verifier_forme(forme)
    if erreur:
        raise HTTPException(status_code=400, detail=erreur)  # 400 = mauvaise requête

    historique.append(forme)
    await envoyer_a_tous(forme)
    print("forme reçue :", forme)
    return {"status": "ok", "tableaux": len(tableaux)}


@app.post("/clear")
async def clear():
    historique.clear()
    await envoyer_a_tous({"shape": "clear"})
    print("tableau effacé")
    return {"status": "ok"}


# ---------- websocket ----------

@app.websocket("/ws")
async def websocket_tableau(websocket: WebSocket):
    await websocket.accept()
    tableaux.append(websocket)
    print(f"un tableau se connecte ({len(tableaux)} ouverts)")

    # le nouveau tableau reçoit tout ce qui a déjà été dessiné
    for forme in historique:
        await websocket.send_json(forme)
    await envoyer_a_tous({"shape": "info", "tableaux": len(tableaux)})

    try:
        # bonus : on peut aussi dessiner à la souris depuis la page
        # la page envoie des lignes, on les partage avec les autres tableaux
        while True:
            forme = await websocket.receive_json()
            if verifier_forme(forme) is None:
                historique.append(forme)
                await envoyer_a_tous(forme)
    except WebSocketDisconnect:
        if websocket in tableaux:
            tableaux.remove(websocket)
        print(f"un tableau se ferme ({len(tableaux)} ouverts)")
        await envoyer_a_tous({"shape": "info", "tableaux": len(tableaux)})


if __name__ == "__main__":
    print("tableau dispo sur http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
