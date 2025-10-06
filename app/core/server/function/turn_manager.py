from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException
import os, json

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
        doc_id = body.get("roomId")
        question = body.get("question")
        answer = body.get("answer")

        if not doc_id:
            return context.res.json({"error": "roomId fehlt"}, 400)

        room = databases.get_document(database_id=db_id, collection_id=col_id, document_id=doc_id)
        players = room.get("players", [])
        current_turn = room.get("current_turn")
        room_question = room.get("question", "")
        room_answer = room.get("answer", "")

        if len(players) != 2:
            return context.res.json({"error": "Spiel nicht voll besetzt"}, 400)

        # Spieler stellt Frage
        if question and current_turn in players:
            databases.update_document(
                database_id=db_id,
                collection_id=col_id,
                document_id=doc_id,
                data={"question": question, "answer": ""}
            )
            return context.res.json({"status": "question_set"})

        # Spieler gibt Antwort
        if answer and room_question:
            next_player = players[0] if current_turn == players[1] else players[1]
            databases.update_document(
                database_id=db_id,
                collection_id=col_id,
                document_id=doc_id,
                data={
                    "answer": answer,
                    "current_turn": next_player,
                    "question": "",
                }
            )
            return context.res.json({"status": "turn_switched", "next_turn": next_player})

        return context.res.json({"status": "ok"})

    except AppwriteException as err:
        return context.res.json({"error": str(err)}, 500)
