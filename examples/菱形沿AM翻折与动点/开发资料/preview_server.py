"""Local preview of this example; offline HTML can also be opened directly."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote
root=Path(__file__).resolve().parent.parent/'成品'
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(root)))
print(f'http://127.0.0.1:{server.server_port}/'+quote('菱形沿AM翻折与动点.html'),flush=True)
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:server.server_close()
