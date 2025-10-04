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
        if not user_id:
            return context.res.json({"error": "userId fehlt"}, 400)

        if not db_id or not col_id:
            return context.res.json({"error": "DB_ID oder COLLECTION_ID nicht gesetzt"}, 500)

        # Alle Dokumente abfragen
        try:
            docs_list = databases.list_documents(database_id=db_id, collection_id=col_id).get("documents", [])
            context.log(f"[matchmaking] fetched {len(docs_list)} documents from collection")
        except Exception as e:
            context.log(f"[matchmaking] list_documents error: {e}")
            return context.res.json({"error": f"DB error: {e}"}, 500)

        # Suche nach wartenden Räumen mit <2 Spielern
        waiting_rooms = [d for d in docs_list if d.get("state") == "waiting" and len(d.get("players", [])) < 2]

        if waiting_rooms:
            # Nimm den ersten passenden Raum
            room = waiting_rooms[0]
            doc_id = room.get("$id") or room.get("roomId")
            players = list(room.get("players", []))

            if user_id not in players:
                players.append(user_id)

            # Spiel starten, wenn jetzt 2 Spieler da sind
            state = "started" if len(players) == 2 else "waiting"
            start_player = random.choice(players) if state == "started" else None

            # Alte überflüssige Räume löschen (nur 1 Spieler, nicht der aktuelle Raum)
            # Alte überflüssige Räume löschen (nur 1 Spieler, nicht der aktuelle Raum)
            if state == "started":
                for old_room in waiting_rooms:
                    # Lösche nur Räume mit genau 1 Spieler, die nicht der aktuelle Raum sind
                    if old_room.get("$id") != doc_id and len(old_room.get("players", [])) == 1:
                        try:
                            databases.delete_document(
                                database_id=db_id,
                                collection_id=col_id,
                                document_id=old_room.get("$id") or old_room.get("roomId")
                            )
                            context.log(f"[matchmaking] deleted old single-player room {old_room.get('roomId')}")
                        except Exception as e:
                            context.log(f"[matchmaking] failed to delete old room {old_room.get('roomId')}: {e}")


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
                return context.res.json({"joined": True, "room": updated})
            except Exception as e:
                context.log(f"[matchmaking] update_document error for {doc_id}: {e}")
                return context.res.json({"error": f"DB update error: {e}"}, 500)

        else:
            # Neuer Raum anlegen, falls kein wartender Raum existiert
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
            return context.res.json({"joined": False, "room": created})

    except AppwriteException as err:
        return context.res.json({"error": str(err)}, 500)
    except Exception as e:
        return context.res.json({"error": str(e)}, 500)
