import socket
import threading
import uuid

game_rooms = {}  # room_id: {"players": [p1, p2], "chars": {p1: None, p2: None}}
lock = threading.Lock()


def print_game_rooms():
    print("[AKTUELLE RÄUME]")
    for room_id, room in game_rooms.items():
        p1_status = "✔" if room["players"][0] else "✖"
        p2_status = "✔" if room["players"][1] else "✖"
        c1 = room["chars"].get(room["players"][0])
        c2 = room["chars"].get(room["players"][1])
        print(f"Room {room_id}: Spieler1={p1_status} ({c1}), Spieler2={p2_status} ({c2})")
    print("-" * 30)


def broadcast_player_count():
    count = sum(1 for room in game_rooms.values() for p in room["players"] if p)
    for room in game_rooms.values():
        for p in room["players"]:
            if p:
                try:
                    p.sendall(f"PLAYER_COUNT {count}\n".encode("utf-8"))
                except:
                    pass


def handle_client(conn, addr):
    global game_rooms
    print(f"[VERBUNDEN] {addr}")

    with lock:
        room_to_join = None
        for room_id, room in game_rooms.items():
            if room["players"][1] is None:
                room_to_join = room_id
                break

        if room_to_join:
            # Spieler tritt bei
            game_rooms[room_to_join]["players"][1] = conn
            game_rooms[room_to_join]["chars"][conn] = None
            p1, p2 = game_rooms[room_to_join]["players"]
            print(f"[ROOM GEFÜLLT] Room {room_to_join} - {p1.getpeername()} vs {p2.getpeername()}")
            print_game_rooms()

            # SOFORT Spiel starten, ohne auf Char-Auswahl zu warten
            try:
                for p in (p1, p2):
                    if p:
                        p.sendall(
                            f"START_GAME {room_to_join}\n".encode("utf-8")
                        )
                print(f"[GAME START] Room {room_to_join} → Clients erhalten START_GAME")
            except Exception as e:
                print("[ERROR] Konnte START_GAME nicht senden:", e)

            # Session-Thread starten (für Nachrichten/Chars)
            threading.Thread(target=game_session, args=(room_to_join, p1, p2), daemon=True).start()

        else:
            # Neuer Raum
            room_id = str(uuid.uuid4())[:8]
            game_rooms[room_id] = {
                "players": [conn, None],
                "chars": {conn: None}
            }
            print(f"[NEUER RAUM] Room {room_id} erstellt für {addr}")
            broadcast_player_count()
            print_game_rooms()



def game_session(room_id, player1, player2):
    players = [player1, player2]
    try:
        while True:
            for p in players:
                if not p:
                    continue
                msg = p.recv(1024).decode("utf-8").strip()
                if not msg:
                    raise ConnectionError

                if msg.startswith("CHAR_SELECTED"):
                    # CHAR_SELECTED room_id name
                    _, rid, char = msg.split(maxsplit=2)
                    if rid == room_id:
                        with lock:
                            game_rooms[room_id]["chars"][p] = char
                            print(f"[CHAR_SELECTED] {p.getpeername()} → {char}")
                            print_game_rooms()

                            chars = list(game_rooms[room_id]["chars"].values())
                            if None not in chars and len(chars) == 2:
                                c1, c2 = chars
                                for other in players:
                                    if other:
                                        other.sendall(
                                            f"START_GAME {room_id} {c1} {c2}\n".encode("utf-8")
                                        )
                                print(f"[GAME START] Room {room_id} mit {c1} vs {c2}")

                else:
                    # normale Nachrichten (z. B. Züge) weiterleiten
                    for other in players:
                        if other and other != p:
                            other.sendall(msg.encode("utf-8"))

    except:
        print(f"[GAME ENDE] Room {room_id}")
        for p in players:
            try:
                p.close()
            except:
                pass
        with lock:
            if room_id in game_rooms:
                del game_rooms[room_id]
            print_game_rooms()


def start_server(host="0.0.0.0", port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[SERVER START] {host}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
