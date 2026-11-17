import re
import base64
from pathlib import Path

xmp_file = Path("/home/usuario/Descargas/pycode/indesign_forensics/extracted_metadata.xmp")
text = xmp_file.read_text(encoding="utf-8", errors="ignore")
out_dir = Path("/home/usuario/Descargas/pycode/indesign_forensics/extracted_images")
out_dir.mkdir(exist_ok=True)

# 1. Extract from XMP <xmpGImg:image>
images_b64 = re.findall(r"<xmpGImg:image>(.*?)</xmpGImg:image>", text, re.DOTALL)
print(f"[+] Found {len(images_b64)} Base64 images in XMP.")

for i, raw_b64 in enumerate(images_b64):
    clean = raw_b64.replace("\n", "").replace("\r", "").replace("&#xA;", "").strip()
    try:
        data = base64.b64decode(clean)
        out_path = out_dir / f"xmp_thumb_{i+1}.jpg"
        out_path.write_bytes(data)
        print(f"  -> Wrote {out_path} ({len(data)} bytes)")
    except Exception as e:
        print(f"  [-] Failed to decode image #{i+1}: {e}")

# 2. Extract raw JPEGs by carving binary markers FF D8 FF ... FF D9
indd_data = Path("/home/usuario/Descargas/pycode/indesign_forensics/target.indd").read_bytes()
jpeg_starts = [m.start() for m in re.finditer(rb"\xff\xd8\xff", indd_data)]
print(f"\n[+] Found {len(jpeg_starts)} raw JPEG SOI markers in binary file.")

for i, start in enumerate(jpeg_starts):
    # Find next EOI marker
    end = indd_data.find(rb"\xff\xd9", start)
    if end != -1:
        end += 2
        raw_jpg = indd_data[start:end]
        out_path = out_dir / f"carved_raw_{i+1}.jpg"
        out_path.write_bytes(raw_jpg)
        print(f"  -> Carved {out_path} ({len(raw_jpg)} bytes, offset 0x{start:X}-0x{end:X})")
