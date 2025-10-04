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

        # Validierung: DB-IDs sollten gesetzt sein
        if not db_id or not col_id:
            return context.res.json({"error": "DB_ID oder COLLECTION_ID nicht gesetzt"}, 500)

        # Suche nach offenem Raum (state = waiting)
        # Um mögliche SDK/Query-Inkompatibilitäten zu vermeiden, listen wir die
        # Dokumente und filtern lokal nach state == 'waiting'. Das ist robuster
        # und vermeidet Appwrite-Query-Syntax-Probleme.
        try:
            docs = databases.list_documents(database_id=db_id, collection_id=col_id)
            docs_list = docs.get("documents", [])
            context.log(f"[matchmaking] fetched {len(docs_list)} documents from collection")
        except Exception as e:
            context.log(f"[matchmaking] list_documents error: {e}")
            return context.res.json({"error": f"DB error: {e}"}, 500)

        # Finde erstes wartendes Zimmer
        room = next((d for d in docs_list if d.get("state") == "waiting"), None)
        if room:
            doc_id = room.get("$id") or room.get("roomId")
            players = list(room.get("players", []))

            # Wenn der Spieler schon im Raum ist, gib den Raum unverändert zurück
            if user_id in players:
                context.log(f"[matchmaking] user {user_id} already in room {doc_id}")
                return context.res.json({"joined": True, "room": room})

            # Spieler hinzufügen
            players.append(user_id)

            # Spiel starten, erster Spieler (nach Join) beginnt zufällig
            start_player = random.choice(players)

            try:
                updated = databases.update_document(
                    database_id=db_id,
                    collection_id=col_id,
                    document_id=doc_id,
                    data={
                        "players": players,
                        "state": "started",
                        "current_turn": start_player,
                        "question": "",
                        "answer": ""
                    }
                )
                context.log(f"[matchmaking] user {user_id} joined room {doc_id}; start_player={start_player}")
                
                # Prüfen, ob das Spiel beendet ist
                if updated.get("state") == "ended":
                    try:
                        databases.delete_document(database_id=db_id, collection_id=col_id, document_id=doc_id)
                        context.log(f"[matchmaking] room {doc_id} deleted after game ended")
                    except Exception as e:
                        context.log(f"[matchmaking] failed to delete room {doc_id}: {e}")

                
                
                return context.res.json({"joined": True, "room": updated})
            except Exception as e:
                context.log(f"[matchmaking] update_document error for {doc_id}: {e}")
                return context.res.json({"error": f"DB update error: {e}"}, 500)

        else:
            # Neuer Raum anlegen
            # Erzeuge eine eindeutige roomId und verwende sie als document_id
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
        # generischer Fehler
        return context.res.json({"error": str(e)}, 500)
