"""Jump : sert index.html + tableau des scores partagé (stdlib uniquement)."""
import json
import os
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get('JUMP_DB', os.path.join(ROOT, 'data', 'scores.json'))
# ponytail: global lock + whole-file JSON rewrite, fine for a family leaderboard; SQLite if traffic grows
lock = threading.Lock()


def load():
    try:
        with open(DB, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def save(db):
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    tmp = DB + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False)
    os.replace(tmp, DB)


def top(db, n=20):
    rows = sorted((p for p in db.values() if p['score'] > 0), key=lambda p: -p['score'])[:n]
    return [{'name': p['name'], 'score': p['score'], 'pet': p['pet']} for p in rows]


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, ctype='application/json'):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', '/index.html'):
            with open(os.path.join(ROOT, 'index.html'), 'rb') as f:
                return self.send(200, f.read(), 'text/html; charset=utf-8')
        if path == '/api/scores':
            return self.send(200, top(load()))
        self.send(404, {'error': 'introuvable'})

    def do_POST(self):
        try:
            n = int(self.headers.get('Content-Length', 0))
            if not 0 < n <= 1000:
                raise ValueError
            d = json.loads(self.rfile.read(n))
            name = ' '.join(str(d.get('name', '')).split())[:12]
            score = int(d.get('score', 0))
            if not name or not 0 <= score < 10**7:
                raise ValueError
        except (ValueError, TypeError, AttributeError):
            return self.send(400, {'error': 'requête invalide'})
        pet = d.get('pet') if d.get('pet') in ('cat', 'dog') else 'cat'
        key = name.lower()
        with lock:
            db = load()
            if self.path == '/api/register':
                if key in db:
                    return self.send(409, {'error': 'pseudo déjà pris'})
                db[key] = {'name': name, 'token': secrets.token_hex(16), 'score': 0, 'pet': pet}
                save(db)
                return self.send(200, {'name': name, 'token': db[key]['token']})
            if self.path == '/api/scores':
                p = db.get(key)
                if not p or not secrets.compare_digest(str(d.get('token', '')), p['token']):
                    return self.send(403, {'error': 'joueur inconnu'})
                if score > p['score']:
                    p['score'], p['pet'] = score, pet
                    save(db)
                return self.send(200, top(db))
        self.send(404, {'error': 'introuvable'})


if __name__ == '__main__':
    ThreadingHTTPServer(('', int(os.environ.get('PORT', 8000))), Handler).serve_forever()
