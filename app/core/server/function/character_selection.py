from appwrite.client import Client
from appwrite.services.databases import Databases
import os, json, random

def _parse_request_body(req):
    raw = getattr(req, 'body', None)
    if not raw:
        return {}
    try:
        return json.loads(raw if isinstance(raw, str) else raw.decode("utf-8"))
    except Exception:
        return {}

def main(context):
    client = (
        Client()
        .set_endpoint(os.environ["APPWRITE_FUNCTION_API_ENDPOINT"])
        .set_project(os.environ["APPWRITE_FUNCTION_PROJECT_ID"])
        .set_key(os.environ["APPWRITE_API_KEY"])
    )

    databases = Databases(client)
    db_id = os.environ["MY_DB_ID"]
    col_id = os.environ["MY_COLLECTION_ID"]

    body = _parse_request_body(context.req)
    room_id = body.get("roomId")
    user_id = body.get("userId")
    character = body.get("character")

    if not room_id or not user_id or not character:
        return context.res.json({"error": "roomId, userId oder character fehlen"}, 400)

    try:
        # Hole das Raum-Dokument
        room = databases.get_document(database_id=db_id, collection_id=col_id, document_id=room_id)
        character_data = room.get("character_data") or {}

        # Füge/aktualisiere den Charakter des Spielers hinzu
        character_data[user_id] = character

        updates = {"character_data": character_data}

        # Wenn beide Spieler einen Charakter haben
        players = room.get("players", [])
        if len(character_data) >= 2 and all(p in character_data for p in players):
            # 22 zufällige Charaktere hinzufügen
            random_chars = [
                {"name": f"NPC-{i+1}", "img": f"npc_{i+1}.png"}
                for i in range(22)
            ]
            updates["character_data"]["random_generated"] = random_chars
            updates["state"] = "ready"

        updated = databases.update_document(
            database_id=db_id,
            collection_id=col_id,
            document_id=room_id,
            data=updates
        )

        return context.res.json({"success": True, "updated_room": updated})

    except Exception as e:
        return context.res.json({"error": str(e)}, 500)
