from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException
import os, json, random, uuid


def _parse_request_body(req):
    raw = getattr(req, 'body', None)
    if isinstance(raw, dict):
        return raw
    if raw is None:
        return {}
    if isinstance(raw, (bytes, bytearray)):
        try:
            raw = raw.decode('utf-8')
        except Exception:
            return {}
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except Exception:
            return {}
    try:
        return json.loads(str(raw))
    except Exception:
        return {}


def delete_room(databases, db_id, col_id, room_id, context):
    """Hilfsfunktion zum gezielten Löschen eines Raums"""
    try:
        databases.delete_document(
            database_id=db_id,
            collection_id=col_id,
            document_id=room_id
        )
        context.log(f"[matchmaking] manually deleted room {room_id}")
        return {"deleted": True, "roomId": room_id}
    except Exception as e:
        context.log(f"[matchmaking] failed to delete room {room_id}: {e}")
        return {"deleted": False, "error": str(e)}


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

    try:
        body = _parse_request_body(context.req)
        user_id = body.get("userId")
        action = body.get("action")
        room_id = body.get("roomId")

        if not db_id or not col_id:
            return context.res.json({"error": "DB_ID oder COLLECTION_ID nicht gesetzt"}, 500)

        # 🔹 NEU: Aktion "delete"
        if action == "delete":
            if not room_id:
                return context.res.json({"error": "roomId fehlt für delete"}, 400)
            result = delete_room(databases, db_id, col_id, room_id, context)
            return context.res.json(result, 200 if result["deleted"] else 500)

        # 🔹 Standard: Matchmaking-Logik
        if not user_id:
            return context.res.json({"error": "userId fehlt"}, 400)

        docs_list = databases.list_documents(database_id=db_id, collection_id=col_id).get("documents", [])
        context.log(f"[matchmaking] fetched {len(docs_list)} documents from collection")

        # Prüfen, ob der Spieler bereits in einem Raum ist
        existing_room = next((d for d in docs_list if user_id in d.get("players", [])), None)
        if existing_room:
            context.log(f"[matchmaking] user {user_id} already in a room {existing_room.get('roomId')}")
            return context.res.json({"joined": True, "room": existing_room})

        # Suche nach wartenden Räumen mit <2 Spielern
        waiting_room = next((d for d in docs_list if d.get("state") == "waiting" and len(d.get("players", [])) < 2), None)

        if waiting_room:
            doc_id = waiting_room.get("$id") or waiting_room.get("roomId")
            players = list(waiting_room.get("players", []))

            # Spieler hinzufügen
            players.append(user_id)
            state = "started"
            start_player = random.choice(players)

            try:
                updated = databases.update_document(
                    database_id=db_id,
                    collection_id=col_id,
                    document_id=doc_id,
                    data={
                        "players": players,
                        "state": state,
                        "current_turn": start_player,
                        "question": "",
                        "answer": ""
                    }
                )
                context.log(f"[matchmaking] user {user_id} joined room {doc_id}; start_player={start_player}")

                # Alte Einzelräume löschen
                for old_room in docs_list:
                    if old_room.get("$id") != doc_id and len(old_room.get("players", [])) == 1:
                        try:
                            databases.delete_document(database_id=db_id, collection_id=col_id, document_id=old_room.get("$id"))
                            context.log(f"[matchmaking] deleted old single-player room {old_room.get('roomId')}")
                        except Exception as e:
                            context.log(f"[matchmaking] failed to delete old room {old_room.get('roomId')}: {e}")

                return context.res.json({"joined": True, "room": updated})
            except Exception as e:
                context.log(f"[matchmaking] update_document error for {doc_id}: {e}")
                return context.res.json({"error": f"DB update error: {e}"}, 500)

        else:
            # Neuer Raum erstellen
            room_id = str(uuid.uuid4())[:8]
            created = databases.create_document(
                database_id=db_id,
                collection_id=col_id,
                document_id=room_id,
                data={
                    "roomId": room_id,
                    "players": [user_id],
                    "state": "waiting",
                    "current_turn": None,
                    "question": "",
                    "answer": ""
                }
            )
            context.log(f"[matchmaking] created new room {room_id} for user {user_id}")
            return context.res.json({"joined": False, "room": created})

    except AppwriteException as err:
        return context.res.json({"error": str(err)}, 500)
    except Exception as e:
        return context.res.json({"error": str(e)}, 500)
