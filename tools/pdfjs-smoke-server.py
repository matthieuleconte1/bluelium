#!/usr/bin/env python3
"""Serveur de verification PDF.js, local uniquement, sans dependance.

python3 tools/pdfjs-smoke-server.py [port, defaut 8765]
Ouvrir http://127.0.0.1:8765 dans le navigateur compile.
Le PDF contient deux pages, un champ de formulaire et une annotation texte.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys


def sample_pdf(padding=0):
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R /AcroForm 8 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R 9 0 R] /Count 2 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R /Annots [6 0 R 7 0 R] >>',
        b'<< /Length 160 >>\nstream\nBT /F1 24 Tf 50 770 Td (Bluelium - PDF.js) Tj /F1 12 Tf 0 -35 Td (Recherche : instrument) Tj 0 -35 Td (Formulaire : nom) Tj ET\nendstream',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
        b'<< /Type /Annot /Subtype /Widget /FT /Tx /T (Nom) /Rect [50 660 300 690] /V (Exemple) /DA (/F1 12 Tf 0 g) /P 3 0 R /F 4 >>',
        b'<< /Type /Annot /Subtype /Text /Rect [350 700 375 725] /Contents (Annotation de verification Bluelium) /T (Bluelium) /Name /Comment /C [0.2 0.3 0.8] >>',
        b'<< /Fields [6 0 R] /NeedAppearances true /DR << /Font << /F1 5 0 R >> >> /DA (/F1 12 Tf 0 g) >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 10 0 R >>',
        b'<< /Length 88 >>\nstream\nBT /F1 24 Tf 50 770 Td (Deuxieme page) Tj /F1 12 Tf 0 -35 Td (instrument) Tj ET\nendstream',
    ]
    if padding:
        objects[3] = objects[3].replace(b'\nendstream', b'\n%' + b'x' * padding + b'\nendstream')
    # Longueurs exactes, pour tester le lecteur sans reparation du PDF.
    for i in (3, 9):
        content = objects[i].split(b'\nstream\n')[1].split(b'\nendstream')[0] + b'\n'
        objects[i] = b'<< /Length %d >>\nstream\n' % len(content) + content + b'endstream'
    result = bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n')
    offsets = [0]
    for n, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result += b'%d 0 obj\n' % n + obj + b'\nendobj\n'
    xref = len(result)
    result += b'xref\n0 %d\n0000000000 65535 f \n' % len(offsets)
    for offset in offsets[1:]:
        result += b'%010d 00000 n \n' % offset
    result += b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(offsets), xref)
    return bytes(result)


PDF = sample_pdf()
LARGE_PDF = sample_pdf(2 * 1024 * 1024)
PAGE = '''<!doctype html><meta charset="utf-8"><title>Vérification PDF Bluelium</title>
<h1>Vérification PDF Bluelium</h1>
<p><a href="/sample.pdf">PDF web</a> · <a href="/attachment.pdf">PDF téléchargé</a> ·
<a href="/redirect.pdf">Redirection</a> · <a href="/truncated.pdf">Flux interrompu</a></p>
<form method="post" action="/post.pdf"><input name="test" value="PDF POST"><button>PDF via POST (un GET échoue)</button></form>
<p><a href="/sample.pdf#page=2">Ouvrir à la page 2</a></p>
<iframe title="PDF intégré" src="/sample.pdf" width="800" height="500"></iframe>'''.encode()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length', 0)))
        self.send_pdf()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(PAGE)))
            self.end_headers()
            self.wfile.write(PAGE)
        elif self.path == '/auto-post':
            body = b'<form method="post" action="/post.pdf"><input name="test" value="PDF POST"></form><script>document.forms[0].submit()</script>'
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith('/post.pdf'):
            self.send_error(405, 'POST obligatoire')
        elif self.path.startswith('/redirect.pdf'):
            self.send_response(302)
            self.send_header('Location', '/sample.pdf')
            self.end_headers()
        else:
            self.send_pdf()

    def send_pdf(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/pdf')
        payload = LARGE_PDF if self.path.startswith('/large.pdf') else PDF
        extra = 1000 if self.path.startswith('/truncated.pdf') else 0
        self.send_header('Content-Length', str(len(payload) + extra))
        if self.path.startswith('/attachment.pdf'):
            self.send_header('Content-Disposition', 'attachment; filename="bluelium-test.pdf"')
        self.end_headers()
        self.wfile.write(payload)
        self.close_connection = True


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    Path('/tmp/bluelium-test.pdf').write_bytes(PDF)
    print(f'http://127.0.0.1:{port} — PDF local : /tmp/bluelium-test.pdf', flush=True)
    HTTPServer(('127.0.0.1', port), Handler).serve_forever()
