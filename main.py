import os
# Erzwinge ffpyplayer als Audio-Backend (wichtig für Android)
os.environ["KIVY_AUDIO"] = "ffpyplayer"

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy import platform
# Importiere ScreenManager-Setup aus deiner App
from app.ui import register_screens, PRIMARY_PALETTE, THEME_STYLE  # kümmert sich um das Hinzufügen der Screens
from kivy.core.audio import SoundLoader
from kivy.resources import resource_find
from pathlib import Path


if platform == "android":
    from android.permissions import request_permissions, Permission, check_permission  # pylint: disable=import-error # type: ignore
    request_permissions([Permission.READ_EXTERNAL_STORAGE,
                        Permission.WRITE_EXTERNAL_STORAGE,
                        Permission.CAMERA,
                        ])

class AnimeWerIstDasApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Hintergrundmusik-Verwaltung
        self.music_playlist = [
            "app/assets/sound/Who_Am_I_1.ogg",
            "app/assets/sound/background.ogg",
            "app/assets/sound/music.ogg",
        ]
        self.current_track_path = None
        self.current_sound = None
        self.muted = False
        self.volume = 0.7
        # Wenn True, spielt Musik weiter, wenn App in Hintergrund geht (sofern vom OS erlaubt)
        self.play_in_background = False

    def build(self):
        self.title = "Anime Wer ist das?"
        self.theme_cls.primary_palette = PRIMARY_PALETTE  # Palette bleibt nötig, z.B. für Buttons
        self.theme_cls.theme_style = THEME_STYLE

        sm = ScreenManager()
        register_screens(sm)  # Screens werden hier hinzugefügt
        return sm
    
    # ----------------------
    # Hintergrund-Audio
    # ----------------------
    def resolve_existing_audio_path(self):
        """Sucht den ersten existierenden Audiopfad aus der Playlist."""
        for candidate in self.music_playlist:
            resolved = resource_find(candidate) or (candidate if Path(candidate).exists() else None)
            if resolved:
                return resolved
        return None

    def init_background_audio(self):
        if self.current_sound:
            return
        path = self.resolve_existing_audio_path()
        if not path:
            print("[Audio] Kein Audiotrack gefunden (erwartet z.B. app/assets/sound/background.ogg)")
            return
        self.current_track_path = path
        self.current_sound = SoundLoader.load(path)
        if self.current_sound:
            # Lautstärke und Loop setzen
            self.current_sound.volume = 0 if self.muted else self.volume
            try:
                self.current_sound.loop = True
            except Exception:
                # Nicht jedes Backend unterstützt .loop als Attribut
                pass
        else:
            print(f"[Audio] Konnte Track nicht laden: {path}")

    def start_background_music(self):
        if not self.current_sound:
            self.init_background_audio()
        if self.current_sound:
            self.current_sound.volume = 0 if self.muted else self.volume
            self.current_sound.play()

    def pause_background_music(self):
        if self.current_sound:
            try:
                self.current_sound.stop()
            except Exception:
                pass

    def stop_background_music(self):
        if self.current_sound:
            try:
                self.current_sound.stop()
            except Exception:
                pass
            try:
                self.current_sound.unload()
            except Exception:
                pass
            self.current_sound = None

    def toggle_mute(self):
        self.muted = not self.muted
        if self.current_sound:
            self.current_sound.volume = 0 if self.muted else self.volume
        return self.muted

    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, float(volume)))
        if self.current_sound and not self.muted:
            self.current_sound.volume = self.volume

    def set_play_in_background(self, enabled: bool):
        self.play_in_background = bool(enabled)

    def is_music_playing(self):
        try:
            return self.current_sound is not None and getattr(self.current_sound, "state", "") == "play"
        except Exception:
            return False
    
    def on_enter(self):
        # Berechtigungen für Android anfragen
        if platform == "android":
            print("Berechtigungen werden angefragt...")
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.CAMERA,
                Permission.FLASHLIGHT,
            ])
            print("Berechtigungen wurden angefragt.")

    def on_start(self):
        # Musik automatisch starten (falls Datei vorhanden)
        self.start_background_music()

    def on_pause(self):
        # Standard: Musik anhalten, um Akku zu sparen.
        if not self.play_in_background:
            self.pause_background_music()
        # True zurückgeben ermöglicht das Pausieren der App
        return True

    def on_resume(self):
        # Beim Zurückkehren die Musik fortsetzen
        if not self.muted:
            self.start_background_music()

    def on_stop(self):
        # Aufräumen
        self.stop_background_music()

if __name__ == "__main__":
    AnimeWerIstDasApp().run()
