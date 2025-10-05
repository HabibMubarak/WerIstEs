from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException
import os, json, random

def _parse_request_body(req):
    raw = getattr(req, 'body', None)
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode('utf-8')
    if isinstance(raw, str):
        return json.loads(raw)
    return {}

def main(context):
    # Appwrite Client
    client = Client()\
        .set_endpoint(os.environ["APPWRITE_FUNCTION_API_ENDPOINT"])\
        .set_project(os.environ["APPWRITE_FUNCTION_PROJECT_ID"])\
        .set_key(os.environ["APPWRITE_API_KEY"])
    
    databases = Databases(client)
    db_id = os.environ["MY_DB_ID"]
    col_id = os.environ["MY_COLLECTION_ID"]

    try:
        body = _parse_request_body(context.req)
        room_id = body.get("roomId")
        user_id = body.get("userId")
        character = body.get("character")  # {"name": "...", "img": "..."}

        if not all([room_id, user_id, character]):
            return context.res.json({"error": "roomId, userId oder character fehlen"}, 400)

        # Raum abrufen
        room = databases.get_document(db_id, col_id, room_id)
        if not room:
            return context.res.json({"error": "Room nicht gefunden"}, 404)

        # character_data sicher initialisieren
        char_data = room.get("character_data") or {}
        char_data[user_id] = character

        # Prüfen, ob beide Spieler gewählt haben
        players = room.get("players", [])
        ready_players = [p for p in players if p in char_data]
        both_ready = len(ready_players) >= 2

        # Random-Charaktere generieren
        all_possible_chars = [{"name": f"Random{i}", "img": f"url{i}.png"} for i in range(100)]
        chosen_names = [c["name"] for c in char_data.values()]
        available_chars = [c for c in all_possible_chars if c["name"] not in chosen_names]

        random_count = 22
        player_chars = [c for k, c in char_data.items() if k in players]
        if len({c["name"] for c in player_chars}) < len(player_chars):
            random_count = 23

        random_chars = random.sample(available_chars, random_count)
        char_data["random"] = random_chars

        # Update Daten
        update_data = {"character_data": char_data}
        if both_ready:
            update_data["state"] = "ready"

        updated = databases.update_document(db_id, col_id, room_id, update_data)
        return context.res.json({"room": updated, "both_ready": both_ready})

    except AppwriteException as e:
        return context.res.json({"error": str(e)}, 500)
    except Exception as e:
        return context.res.json({"error": str(e)}, 500)
