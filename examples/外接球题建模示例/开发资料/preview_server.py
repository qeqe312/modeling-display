"""Preview retained deliverables on loopback; runtime files stay under .运行时."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import os

DEV = Path(__file__).resolve().parent
RUNTIME = DEV / '.运行时'
RUNTIME.mkdir(exist_ok=True)
parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=0)
args = parser.parse_args()
server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(SimpleHTTPRequestHandler, directory=str(DEV.parent / '成品')))
(RUNTIME / 'preview-server.json').write_text(json.dumps({'pid':os.getpid(),'port':server.server_port}), encoding='utf-8')
server.serve_forever()
