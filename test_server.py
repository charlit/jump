import json
import os
import tempfile
import threading
import urllib.error
import urllib.request

os.environ['JUMP_DB'] = os.path.join(tempfile.mkdtemp(), 'scores.json')
import server  # noqa: E402

srv = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{srv.server_address[1]}'


def call(path, body=None):
    req = urllib.request.Request(URL + path, json.dumps(body).encode() if body else None,
                                 {'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None


code, polux = call('/api/register', {'name': ' Polux '})
assert code == 200 and polux['name'] == 'Polux'
assert call('/api/register', {'name': 'polux'})[0] == 409            # name taken, case-insensitive
assert call('/api/register', {'name': '   '})[0] == 400
assert call('/api/scores', {'name': 'Polux', 'token': 'bad', 'score': 5})[0] == 403
assert call('/api/scores', {'name': 'Polux', 'token': polux['token'], 'score': -1})[0] == 400
code, board = call('/api/scores', {'name': 'Polux', 'token': polux['token'], 'score': 1200, 'pet': 'dog'})
assert code == 200 and board == [{'name': 'Polux', 'score': 1200, 'pet': 'dog'}]
call('/api/scores', {'name': 'Polux', 'token': polux['token'], 'score': 300})  # lower score kept out
_, rose = call('/api/register', {'name': 'Rose'})
call('/api/scores', {'name': 'Rose', 'token': rose['token'], 'score': 5000})
code, board = call('/api/scores')
assert [p['name'] for p in board] == ['Rose', 'Polux'] and board[1]['score'] == 1200
assert 'token' not in json.dumps(board)
assert call('/data/scores.json')[0] == 404                             # tokens never served
print('ok')
