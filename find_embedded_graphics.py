from pathlib import Path
import re

indd_data = Path("/home/usuario/Descargas/pycode/indesign_forensics/target.indd").read_bytes()

# 1. JPEG markers: \xff\xd8\xff
jpeg_matches = list(re.finditer(rb"\xff\xd8\xff", indd_data))
print(f"[+] Total JPEG SOI markers (FF D8 FF) in INDD: {len(jpeg_matches)}")
for i, m in enumerate(jpeg_matches):
    start = m.start()
    end = indd_data.find(rb"\xff\xd9", start)
    if end != -1:
        end += 2
        print(f"  JPEG #{i+1}: offset 0x{start:06X} - 0x{end:06X} (size: {end-start} bytes)")
    else:
        print(f"  JPEG #{i+1}: offset 0x{start:06X} (no EOI found)")

# 2. PNG markers: \x89PNG\r\n\x1a\n
png_matches = list(re.finditer(rb"\x89PNG\r\n\x1a\n", indd_data))
print(f"\n[+] Total PNG markers in INDD: {len(png_matches)}")

# 3. Check what objects in indd-utils represent images or proxies
