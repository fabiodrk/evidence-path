"""Double-click launcher that reopens an existing local Evidence Path instance."""
import json
import socket
import sys
import urllib.request
import webbrowser
import app

def main():
    for port in range(8780,8790):
        url=f'http://127.0.0.1:{port}'
        try:
            with urllib.request.urlopen(url+'/api/health',timeout=.5) as response:
                if json.load(response).get('product')=='evidence-path-local':
                    print('Opening the existing Evidence Path workspace at '+url,flush=True)
                    webbrowser.open(url)
                    return
        except (OSError,ValueError):pass
        with socket.socket() as sock:
            try:sock.bind(('127.0.0.1',port))
            except OSError:continue
        sys.argv=[sys.argv[0],'--port',str(port)]
        app.main()
        return
    raise SystemExit('Ports 8780–8789 are occupied. Run app.py --port with a different local port.')

if __name__=='__main__':main()
