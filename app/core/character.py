import sqlite3
import requests
import json
from time import sleep
import os

class Character:
    def __init__(self):
        self.db_path = r"app/assets/characters/anime_characters.db"
        self._setup_database()

    
    def _setup_database(self):
        """Erstellt die Tabelle, falls sie noch nicht existiert."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anime TEXT NOT NULL,
            name TEXT NOT NULL,
            image_url TEXT NOT NULL
        )
        """)
        conn.commit()
        conn.close()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def save_character(self, anime, name, image_url):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO characters (anime, name, image_url) VALUES (?, ?, ?)",
                       (anime, name, image_url))
        conn.commit()
        conn.close()

    def update_image_url(self, name, image_url):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE characters SET image_url=? WHERE name=?", (image_url, name))
        conn.commit()
        conn.close()

    def get_all_characters(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT anime, name, image_url FROM characters")
        rows = cursor.fetchall()
        conn.close()
        return [{"Anime": r[0], "Character": r[1], "Image_URL": r[2]} for r in rows]

    def get_anime_names(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT anime FROM characters")
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def get_number_of_animes(self):
        return len(self.get_anime_names())

    def get_characters_by_anime(self, anime_name):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM characters WHERE anime=?", (anime_name,))
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def get_number_of_characters_in_anime(self, anime_name):
        return len(self.get_characters_by_anime(anime_name))

    def get_random_characters_with_images(self, n=5):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT name, image_url FROM characters ORDER BY RANDOM() LIMIT ?", (n,))
        rows = cursor.fetchall()
        conn.close()
        return [{"Character": r[0], "Image_URL": r[1]} for r in rows]

    def get_image_url_for_character(self, character_name):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT image_url FROM characters WHERE name=?", (character_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "https://via.placeholder.com"

    def get_anime_details(self, lang="de"):
        path = f"app/assets/characters/anime_details_{lang}.json"
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Datei nicht gefunden: {path}")
            return []

    def get_anime_character_details(self):
        characters = self.get_all_characters()
        for entry in characters:
            name = entry["Character"]
            search_url = f"https://api.jikan.moe/v4/characters?q={name}"
            response = requests.get(search_url)
            data = response.json()

            try:
                char_id = data["data"][0]["mal_id"]
            except (IndexError, KeyError):
                print(f"Kein Character gefunden für {name}")
                self.update_image_url(name, "https://via.placeholder.com")
                continue

            pic_url = f"https://api.jikan.moe/v4/characters/{char_id}/pictures"
            response = requests.get(pic_url)
            data = response.json()

            try:
                img_url = data["data"][0]["jpg"]["image_url"]
            except (IndexError, KeyError):
                print(f"Kein Bild gefunden für {name}")
                img_url = "https://via.placeholder.com"

            self.update_image_url(name, img_url)
            sleep(5)  # API schonen

        print("Datenbank erfolgreich aktualisiert!")

    def add_character(self, character_name):
        search_url = f"https://api.jikan.moe/v4/characters?q={character_name}&limit=5"
        response = requests.get(search_url)
        data = response.json()

        try:
            char_id = None
            top_character = None
            for entry in data["data"]:
                if entry["name"].lower() == character_name.lower():
                    top_character = entry
                    char_id = entry["mal_id"]
                    break
            if char_id is None:
                raise IndexError
        except (IndexError, KeyError):
            print(f"Kein Character gefunden für {character_name}")
            return

        anime_list_url = f"https://api.jikan.moe/v4/characters/{char_id}/anime"
        anime_data = requests.get(anime_list_url).json()

        try:
            anime_name = anime_data["data"][0]["anime"]["title"]
        except (IndexError, KeyError):
            print(f"Kein Anime gefunden für {character_name}")
            return

        self.save_character(anime_name, character_name, "https://via.placeholder.com")
        print(f"Character {character_name} aus {anime_name} hinzugefügt.")
        sleep(2)
