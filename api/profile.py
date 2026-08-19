import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import instaloader
from insta_spy import get_profile_data


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        username = query.get("username", [""])[0]

        try:
            data = get_profile_data(username)
            status = 200
            payload = {"ok": True, "data": data}
        except ValueError as exc:
            status = 400
            payload = {"ok": False, "error": str(exc)}
        except instaloader.exceptions.ProfileNotExistsException:
            status = 404
            payload = {"ok": False, "error": "El perfil no existe o Instagram no lo hizo visible."}
        except instaloader.exceptions.ConnectionException as exc:
            status = 503
            payload = {
                "ok": False,
                "error": "Instagram rechazó o limitó temporalmente la consulta.",
                "detail": str(exc)[:300],
            }
        except Exception as exc:
            status = 500
            payload = {"ok": False, "error": "Error inesperado", "detail": str(exc)[:300]}

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
