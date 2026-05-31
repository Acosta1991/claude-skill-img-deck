#!/usr/bin/env python3
"""Editor local de white frames que GUARDA sobre el MISMO archivo.

Sirve `white-frames.html` por HTTP en localhost. El botón "Guardar" del editor
hace un PUT a este servidor y el archivo se sobrescribe en disco — sin descargar
nada y sin diálogos. Funciona en CUALQUIER navegador, incluido Safari y Firefox,
que no soportan la File System Access API y por eso al guardar con `file://`
solo pueden descargar una copia.

Uso:
    python3 scripts/edit_server.py decks/<nombre>/white-frames.html

Luego abre en tu navegador la URL que imprime (p.ej. http://127.0.0.1:8765).
Edita, pulsa "Guardar" y el archivo se sobrescribe. Ctrl+C para detener.

Solo usa la librería estándar de Python (sin dependencias).
"""
import argparse
import http.server
import os
import socketserver
import sys


def main():
    ap = argparse.ArgumentParser(description="Editor local de white frames (guarda sobre el mismo archivo).")
    ap.add_argument("file", help="ruta al white-frames.html a editar/guardar")
    ap.add_argument("--port", type=int, default=8765, help="puerto inicial (default 8765)")
    ap.add_argument("--host", default="127.0.0.1", help="host (default 127.0.0.1)")
    args = ap.parse_args()

    path = os.path.abspath(args.file)
    if not os.path.isfile(path):
        print('{"ok": false, "error": "no existe el archivo: %s"}' % path)
        sys.exit(1)

    class Handler(http.server.BaseHTTPRequestHandler):
        def _send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if body:
                self.wfile.write(body)

        def do_GET(self):
            if self.path.split("?")[0] in ("/", "/index.html", "/white-frames.html"):
                with open(path, "rb") as f:
                    data = f.read()
                self._send(200, data, "text/html; charset=utf-8")
            else:
                self._send(404, b"not found")

        def do_PUT(self):
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length)
            tmp = path + ".tmp"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, path)  # escritura atómica
            self._send(200, b'{"ok": true}', "application/json")

        # Permitir guardar también con POST (por si el navegador lo prefiere).
        do_POST = do_PUT

        def log_message(self, *a):
            pass  # silenciar el log por petición

    # Busca un puerto libre a partir del indicado.
    httpd = None
    port = args.port
    for _ in range(50):
        try:
            socketserver.TCPServer.allow_reuse_address = True
            httpd = socketserver.TCPServer((args.host, port), Handler)
            break
        except OSError:
            port += 1
    if httpd is None:
        print('{"ok": false, "error": "no se encontró un puerto libre"}')
        sys.exit(1)

    url = "http://%s:%d/" % (args.host, port)
    print("Editor de white frames sirviendo: %s" % path)
    print("Abre en tu navegador:  %s" % url)
    print("Edita y pulsa 'Guardar' para sobrescribir el archivo. Ctrl+C para detener.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
