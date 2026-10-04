"""Serve this example's final artifacts on localhost; optional for review."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8766)
    args=parser.parse_args()
    folder=Path(__file__).resolve().parent.parent/'成品'
    if not folder.is_dir():raise SystemExit('Build the final example before starting preview.')
    handler=partial(SimpleHTTPRequestHandler,directory=str(folder))
    with ThreadingHTTPServer(('127.0.0.1',args.port),handler) as server:
        print(f'Preview: http://127.0.0.1:{server.server_port}/',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass

if __name__=='__main__':main()
