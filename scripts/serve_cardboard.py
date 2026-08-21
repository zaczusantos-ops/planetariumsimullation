"""
Servidor local HTTPS Multi-Threaded com suporte completo a Range Requests (HTTP 206) para streaming de vídeo VR no celular.
"""

import http.server
import socketserver
import os
import socket
import ssl
import re

PORT = 8088

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class VideoStreamHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()

    def do_GET(self):
        path = self.translate_path(self.path)
        if os.path.isfile(path) and path.endswith('.mp4'):
            self.serve_video_range(path)
        else:
            super().do_GET()

    def serve_video_range(self, path):
        file_size = os.path.getsize(path)
        range_header = self.headers.get('Range', None)
        
        if not range_header:
            self.send_response(200)
            self.send_header('Content-Type', 'video/mp4')
            self.send_header('Content-Length', str(file_size))
            self.end_headers()
            with open(path, 'rb') as f:
                self.copyfile(f, self.wfile)
            return

        # Parse Range header (ex: bytes=0-1048576)
        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if not match:
            self.send_error(416, "Requested Range Not Satisfiable")
            return

        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else file_size - 1
        end = min(end, file_size - 1)
        length = end - start + 1

        self.send_response(206)
        self.send_header('Content-Type', 'video/mp4')
        self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
        self.send_header('Content-Length', str(length))
        self.end_headers()

        with open(path, 'rb') as f:
            f.seek(start)
            remaining = length
            chunk_size = 64 * 1024
            while remaining > 0:
                chunk = f.read(min(remaining, chunk_size))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (ConnectionResetError, BrokenPipeError):
                    break
                remaining -= len(chunk)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)
    
    local_ip = get_local_ip()
    url = f"https://{local_ip}:{PORT}/web_vr/"
    
    print("\n" + "=" * 60)
    print("[OK] SERVIDOR HTTPS MULTI-THREADED ATIVO COM STREAMING 206!")
    print("=" * 60)
    print(f"\nNo seu celular, acesse:\n\n-->  {url}  <--\n")
    print("=" * 60 + "\n")

    httpd = ThreadedHTTPServer(("", PORT), VideoStreamHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=os.path.join(base_dir, 'cert.pem'), keyfile=os.path.join(base_dir, 'key.pem'))
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
