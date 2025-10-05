import random

# Simulierter Serverzustand
rooms = []  # Liste aller Räume
MAX_PLAYERS = 2
QUESTIONS = [
    "Was ist die Hauptstadt von Frankreich?",
    "2 + 2 = ?",
    "Nenne ein Tier, das fliegen kann."
]

def matchmaking(user_id):
    global rooms

    # Prüfen, ob Spieler schon in einem Raum ist
    for room in rooms:
        if user_id in room["players"]:
            return room

    # Suche nach wartendem Raum
    waiting_room = next((r for r in rooms if r["state"] == "waiting" and len(r["players"]) < MAX_PLAYERS), None)

    if waiting_room:
        waiting_room["players"].append(user_id)
        waiting_room["state"] = "started"
        waiting_room["current_turn"] = random.choice(waiting_room["players"])
        waiting_room["question_index"] = 0
        return waiting_room
    else:
        # Neuer Raum für Spieler
        room_id = f"room_{len(rooms)+1}"
        new_room = {
            "roomId": room_id,
            "players": [user_id],
            "state": "waiting",
            "current_turn": None,
            "question_index": 0
        }
        rooms.append(new_room)
        return new_room

def play_turn(room):
    if room["state"] != "started":
        return
    q_index = room["question_index"]
    if q_index >= len(QUESTIONS):
        room["state"] = "ended"
        print(f"\nRaum {room['roomId']} beendet. Spieler:", room["players"])
        return

    current_player = room["current_turn"]
    question = QUESTIONS[q_index]
    print(f"\nRaum {room['roomId']} - {current_player} ist am Zug")
    print("Frage:", question)

    # Simulierte Antwort
    answer = f"{current_player}_antwort_{q_index+1}"
    print("Antwort:", answer)

    # Nächster Spieler
    next_player = [p for p in room["players"] if p != current_player][0]
    room["current_turn"] = next_player
    room["question_index"] += 1

# Simulierte Spieler
players = ["player1", "player2", "player3", "player4"]

# Matchmaking
for p in players:
    room = matchmaking(p)
    print(f"\n=== Spieler: {p} tritt bei ===")
    print("Raum-ID:", room["roomId"])
    print("Spieler im Raum:", room["players"])
    print("State:", room["state"])
    print("Current Turn:", room.get("current_turn"))

# Spielrunde simulieren
print("\n--- Spielsimulation ---")
active_rooms = [r for r in rooms if r["state"] == "started"]
while active_rooms:
    for room in list(active_rooms):  # Kopie für sicheres Iterieren
        play_turn(room)
        if room["state"] == "ended":
            active_rooms.remove(room)
