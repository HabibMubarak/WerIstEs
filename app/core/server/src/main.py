from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException
import os, json, random

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
        body = json.loads(context.req.body or "{}")
        user_id = body.get("userId")
        if not user_id:
            return context.res.json({"error": "userId fehlt"}, 400)

        # Suche nach offenem Raum (1 Spieler, state=waiting)
        open_rooms = databases.list_documents(
            database_id=db_id,
            collection_id=col_id,
            queries=['equal("state", "waiting")']
        )

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
            # Neuer Raum
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
