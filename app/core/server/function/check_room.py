from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException
import os, json

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

        if not room_id:
            return context.res.json({"error": "roomId fehlt"}, 400)

        # Raum abrufen
        room = databases.get_document(db_id, col_id, room_id)
        if not room:
            return context.res.json({"error": "Room nicht gefunden"}, 404)

        # Spieler + Character Daten
        char_data = room.get("character_data") or {}
        players = room.get("players") or []
        ready_players = [p for p in players if p in char_data]
        both_ready = len(ready_players) >= 2
        state = room.get("state", "waiting")

        return context.res.json({
            "roomId": room_id,
            "players": players,
            "character_data": char_data,
            "both_ready": both_ready,
            "state": state
        })

    except AppwriteException as e:
        return context.res.json({"error": str(e)}, 500)
    except Exception as e:
        return context.res.json({"error": str(e)}, 500)
