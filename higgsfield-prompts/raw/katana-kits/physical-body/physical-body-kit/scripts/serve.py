"""Local HTTP server for the compositor.

GET  resolves first in the job's web dir (footage frames, masks, tracks, edl.json, config.json),
     then in the skill's engine dir (index.html, *.js, stickers/).
POST /frame/<name>  -> <job>/web/frames/<name>   (rendered frames)
POST /shot/<name>   -> <job>/web/shots/<name>    (contact sheets / stills)
POST /track/<name>  -> <job>/web/track/<name>    (face tracks)
POST /audio         -> <job>/web/audio.wav       (sfx render)
POST /log           -> appended to <job>/web/log.txt
GET  /__root        -> the job web dir (lets the driver verify it talks to the right server)

usage: python3 serve.py <job_web_dir> <engine_dir> <port>
Binds 127.0.0.1 only.
"""
import http.server
import os
import re
import socketserver
import sys

JOB = os.path.abspath(sys.argv[1])
ENGINE = os.path.abspath(sys.argv[2])
PORT = int(sys.argv[3])
NAME_OK = re.compile(r'^[A-Za-z0-9_.-]{1,80}$')
POST_DIRS = {'frame': 'frames', 'shot': 'shots', 'track': 'track'}
for d in POST_DIRS.values():
    os.makedirs(os.path.join(JOB, d), exist_ok=True)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=JOB, **k)

    def translate_path(self, path):
        p = super().translate_path(path)  # resolved inside JOB
        if os.path.exists(p):
            return p
        rel = os.path.relpath(p, JOB)
        q = os.path.abspath(os.path.join(ENGINE, rel))
        return q if q.startswith(ENGINE + os.sep) or q == ENGINE else p

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_GET(self):
        if self.path.split('?')[0] == '/__root':
            body = JOB.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(n)
        parts = self.path.split('?')[0].strip('/').split('/')
        target = None
        if len(parts) == 2 and parts[0] in POST_DIRS and NAME_OK.match(parts[1]):
            target = os.path.join(JOB, POST_DIRS[parts[0]], parts[1])
        elif parts == ['audio']:
            target = os.path.join(JOB, 'audio.wav')
        elif parts == ['log']:
            with open(os.path.join(JOB, 'log.txt'), 'a') as f:
                f.write(data.decode('utf-8', 'replace') + '\n')
        if target:
            tmp = target + '.part'
            with open(tmp, 'wb') as f:
                f.write(data)
            os.replace(tmp, target)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'ok')

    def log_message(self, *a):
        pass


socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer.daemon_threads = True
with socketserver.ThreadingTCPServer(('127.0.0.1', PORT), Handler) as srv:
    srv.serve_forever()
