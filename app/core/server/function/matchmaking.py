from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException
import os, json, random


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
        # Note: Appwrite query strings must not include spaces inside the parentheses
        try:
            open_rooms = databases.list_documents(
                database_id=db_id,
                collection_id=col_id,
                queries=['equal("state","waiting")']
            )
        except Exception as e:
            context.log(f"[matchmaking] list_documents error: {e}")
            return context.res.json({"error": f"Invalid query or DB error: {e}"}, 500)

        if open_rooms["total"] > 0:
            room = open_rooms["documents"][0]
            doc_id = room["$id"]
            players = room["players"] + [user_id]

            # Spiel starten, erster Spieler beginnt zufällig
            start_player = random.choice(players)

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
            return context.res.json({"joined": True, "room": updated})

        else:
            # Neuer Raum anlegen
            created = databases.create_document(
                database_id=db_id,
                collection_id=col_id,
                document_id="unique()",
                data={
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
