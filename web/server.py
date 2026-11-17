#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.parse
import subprocess
import shutil
import re
import os
import zipfile
from pathlib import Path
from PIL import Image

PORT = 8088
BASE_DIR = Path("/home/usuario/Descargas/pycode/indesign_forensics")
WEB_DIR = BASE_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
TARGET_INDD = BASE_DIR / "target.indd"
INDD_BIN = BASE_DIR / "indd"
EXTRACT_BIN = BASE_DIR / "extract_previews_bin"

class InddHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            self.send_json({"status": "ready", "file": TARGET_INDD.name, "size": TARGET_INDD.stat().st_size})
        elif path == "/api/document_info":
            self.handle_doc_info()
        elif path == "/api/pages":
            self.handle_pages()
        elif path == "/api/stories":
            self.handle_stories()
        elif path == "/api/assets":
            self.handle_assets()
        elif path.startswith("/api/images/"):
            self.handle_image_serve(path[len("/api/images/"):])
        elif path == "/api/download/idml":
            self.handle_file_download(BASE_DIR / "Sin_titulo-1_InDesign2023.idml", "application/vnd.adobe.indesign-idml-package")
        elif path == "/api/download/package":
            self.handle_file_download(BASE_DIR / "Sin_titulo-1_Paquete_InDesign2023.zip", "application/zip")
        elif path == "/api/download/report":
            self.handle_file_download(BASE_DIR / "document_report.json", "application/json")
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/upload":
            self.handle_upload()
        elif path == "/api/stories/update":
            self.handle_story_update()
        elif path == "/api/rebuild_package":
            self.handle_rebuild_package()
        else:
            self.send_error(404, "Endpoint not found")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def handle_doc_info(self):
        report_file = BASE_DIR / "document_report.json"
        if not report_file.exists():
            subprocess.run(["python3", str(BASE_DIR / "inspect_stories.py")], check=True)
        report = json.loads(report_file.read_text(encoding="utf-8"))

        # indd info summary
        info_out = subprocess.check_output([str(INDD_BIN), "info", str(TARGET_INDD)], text=True)
        
        data = {
            "file_name": TARGET_INDD.name,
            "size_bytes": TARGET_INDD.stat().st_size,
            "raw_info": info_out.strip(),
            "spreads_count": len(report.get("spreads", [])),
            "stories_count": len(report.get("stories", [])),
            "fonts": report.get("fonts", []),
            "version": "InDesign 19.3 (2024)",
            "format": "Adobe InDesign Document (Binary OODB B-Tree)"
        }
        self.send_json(data)

    def handle_pages(self):
        # 4 page thumbnails extracted from XMP + previews
        thumbs_dir = BASE_DIR / "extracted_images"
        pages = []
        for i in range(1, 7):
            thumb_name = f"page_thumbnail_{i}.jpg" if (thumbs_dir / f"page_thumbnail_{i}.jpg").exists() else "page_thumbnail_1.jpg"
            pages.append({
                "page_num": i,
                "name": f"Page / Artboard {i}",
                "thumbnail_url": f"/api/images/{thumb_name}",
                "dimensions": "361 × 512 pt (Portrait)"
            })
        self.send_json({"pages": pages})

    def handle_stories(self):
        report_file = BASE_DIR / "document_report.json"
        if not report_file.exists():
            subprocess.run(["python3", str(BASE_DIR / "inspect_stories.py")], check=True)
        report = json.loads(report_file.read_text(encoding="utf-8"))
        self.send_json({"stories": report.get("stories", [])})

    def handle_assets(self):
        links_dir = BASE_DIR / "Links"
        assets = []
        for p in sorted(links_dir.glob("*")):
            if p.is_file():
                assets.append({
                    "name": p.name,
                    "size_bytes": p.stat().st_size,
                    "url": f"/api/images/{p.name}",
                    "type": "JPEG" if p.suffix.lower() in [".jpg", ".jpeg"] else "PNG"
                })
        self.send_json({"assets": assets})

    def handle_image_serve(self, filename):
        filename = urllib.parse.unquote(filename)
        # Search in Links/ then extracted_images/
        target_path = BASE_DIR / "Links" / filename
        if not target_path.exists():
            target_path = BASE_DIR / "extracted_images" / filename
        if not target_path.exists():
            target_path = BASE_DIR / "extracted_previews" / filename

        if not target_path.exists() or not target_path.is_file():
            self.send_error(404, "Image not found")
            return

        mime = "image/jpeg"
        if target_path.suffix.lower() == ".png":
            mime = "image/png"
        elif target_path.suffix.lower() in [".tif", ".tiff"]:
            mime = "image/tiff"

        raw = target_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(raw)

    def handle_file_download(self, file_path, content_type):
        if not file_path.exists():
            self.send_error(404, "File not ready")
            return
        raw = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", f'attachment; filename="{file_path.name}"')
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def handle_story_update(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        payload = json.loads(body)
        story_file = payload.get("story_file")
        new_text = payload.get("new_text")

        # Mutate in converted.idml
        idml_path = BASE_DIR / "Sin_titulo-1_InDesign2023.idml"
        temp_dir = BASE_DIR / "_temp_api_mutate"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)

        with zipfile.ZipFile(idml_path, "r") as z:
            z.extractall(temp_dir)

        target_story = temp_dir / story_file
        if target_story.exists():
            xml_text = target_story.read_text(encoding="utf-8")
            # Replace Content elements
            pattern = re.compile(r'<Content>(.*?)</Content>', re.DOTALL)
            m = pattern.search(xml_text)
            if m:
                replaced = pattern.sub(f'<Content>{new_text}</Content>', xml_text, count=1)
                target_story.write_text(replaced, encoding="utf-8")
            
            # Re-pack IDML
            with zipfile.ZipFile(idml_path, "w", zipfile.ZIP_DEFLATED) as z_out:
                mimetype = temp_dir / "mimetype"
                if mimetype.exists():
                    z_out.write(mimetype, "mimetype", compress_type=zipfile.ZIP_STORED)
                for f in temp_dir.rglob("*"):
                    if f.is_file() and f.name != "mimetype":
                        z_out.write(f, f.relative_to(temp_dir))
            
            # Update package zip
            subprocess.run(["python3", str(BASE_DIR / "package_for_indesign_and_photopea.py")], check=True)
            self.send_json({"success": True, "message": f"Story {story_file} updated successfully"})
        else:
            self.send_json({"success": False, "error": f"Story {story_file} not found in IDML"}, status=400)
        
        shutil.rmtree(temp_dir, ignore_errors=True)

    def handle_upload(self):
        length = int(self.headers.get("Content-Length", 0))
        file_bytes = self.rfile.read(length)
        if not file_bytes.startswith(b"\x06\x06\xed\xf5\xd8\x1d\x46\xe5"):
            self.send_json({"success": False, "error": "No es un archivo INDD válido (GUID inválido)"}, status=400)
            return
        
        TARGET_INDD.write_bytes(file_bytes)
        # Re-run pipeline
        subprocess.run([str(INDD_BIN), "convert", str(TARGET_INDD), str(BASE_DIR / "converted.idml")], check=True)
        subprocess.run([str(EXTRACT_BIN)], check=True)
        subprocess.run(["python3", str(BASE_DIR / "package_for_indesign_and_photopea.py")], check=True)
        subprocess.run(["python3", str(BASE_DIR / "inspect_stories.py")], check=True)
        self.send_json({"success": True, "message": "Documento cargado y procesado exitosamente"})

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), InddHandler) as httpd:
        print(f"[+] INDD Studio Server running at http://127.0.0.1:{PORT}/")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
