"""
Kleine, robuste Matchmaking-Function

Diese Version akzeptiert `context.req.body` als dict, JSON-string, bytes oder None
und verhindert so den TypeError: json.loads(...) on a dict.

Return: JSON mit status und evtl. room-id (Platzhalter).
"""
import json
import uuid


def _parse_body(raw):
    """Sicheres Parsen des Request-Body.
    Akzeptiert dict, str, bytes, bytearray oder None.
    Liefert immer ein dict zurück.
    """
    if isinstance(raw, dict):
        return raw
    if raw is None:
        return {}
    # falls bytes -> decode
    if isinstance(raw, (bytes, bytearray)):
        try:
            raw = raw.decode('utf-8')
        except Exception:
            return {}
    # falls jetzt ein string
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except Exception:
            # nicht-parsbares String, gebe es als Feld zurück
            return {"raw": raw}
    # Fallback: versuche, es als str zu parsen
    try:
        return json.loads(str(raw))
    except Exception:
        return {"raw": str(raw)}


def main(context):
    try:
        raw = getattr(context.req, 'body', None)
        body = _parse_body(raw)

        # Debug-Logging (erschien in Function-Logs)
        context.log(f"[matchmaking] raw type={type(raw)} parsed_keys={list(body.keys())}")

        # Einfaches Verhalten: check userId und gib eine room id zurück
        user_id = body.get('userId') or body.get('user_id') or body.get('userid')
        if not user_id:
            return context.res.json({"ok": False, "error": "missing userId"}, 400)

        # Platzhalter: echte Matchmaking-Logik kommt hierhin
        room_id = str(uuid.uuid4())[:8]

        return context.res.json({"ok": True, "userId": user_id, "room": room_id})

    except Exception as e:
        context.log(f"[matchmaking] exception: {e}")
        return context.res.json({"ok": False, "error": str(e)}, 500)
