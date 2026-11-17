from pathlib import Path
import base64
import re

xmp_data = Path("/home/usuario/Descargas/pycode/indesign_forensics/extracted_metadata.xmp").read_bytes()
out_dir = Path("/home/usuario/Descargas/pycode/indesign_forensics/extracted_images")
out_dir.mkdir(exist_ok=True)

matches = list(re.finditer(rb"<xmpGImg:image>", xmp_data))
print(f"[+] Found {len(matches)} thumbnails in XMP")

for idx, m in enumerate(matches):
    start = m.end()
    end = xmp_data.find(rb"</xmpGImg:image>", start)
    chunk = xmp_data[start:end]
    
    # Replace entities and whitespace
    clean = chunk.replace(b"&#xA;", b"").replace(b"&#xD;", b"")
    clean = re.sub(rb"\s+", b"", clean)
    
    # Pad if necessary
    missing_padding = len(clean) % 4
    if missing_padding:
        clean += b"=" * (4 - missing_padding)
        
    try:
        decoded = base64.b64decode(clean)
        out_path = out_dir / f"page_thumbnail_{idx+1}.jpg"
        out_path.write_bytes(decoded)
        print(f"[+] Page thumbnail #{idx+1} decoded successfully: {len(decoded)} bytes -> {out_path}")
    except Exception as e:
        print(f"[-] Thumb #{idx+1} decode error: {e}")
