import zipfile
import shutil
from pathlib import Path

source_idml = Path("/home/usuario/Descargas/pycode/indesign_forensics/converted.idml")
target_idml = Path("/home/usuario/Descargas/pycode/indesign_forensics/modified.idml")
temp_dir = Path("/home/usuario/Descargas/pycode/indesign_forensics/_temp_idml")

if temp_dir.exists():
    shutil.rmtree(temp_dir)
temp_dir.mkdir(parents=True)

# 1. Unzip IDML
with zipfile.ZipFile(source_idml, "r") as z:
    z.extractall(temp_dir)

# 2. Mutate target story (Stories/Story_ub8f.xml has 'The Unraveled Tour')
story_path = temp_dir / "Stories" / "Story_ub8f.xml"
if story_path.exists():
    content = story_path.read_text(encoding="utf-8")
    original = "The Unraveled Tour"
    replacement = "The Unraveled Tour (MODIFIED EDITION 2026)"
    if original in content:
        mutated = content.replace(original, replacement)
        story_path.write_text(mutated, encoding="utf-8")
        print(f"[+] Successfully mutated {story_path.name}: replaced '{original}' -> '{replacement}'")
    else:
        print(f"[-] '{original}' not found in {story_path.name}")

# 3. Re-pack IDML
with zipfile.ZipFile(target_idml, "w", zipfile.ZIP_DEFLATED) as z_out:
    # 'mimetype' must be first and uncompressed per IDML spec
    mimetype_file = temp_dir / "mimetype"
    if mimetype_file.exists():
        z_out.write(mimetype_file, "mimetype", compress_type=zipfile.ZIP_STORED)
    
    for f in temp_dir.rglob("*"):
        if f.is_file() and f.name != "mimetype":
            arcname = f.relative_to(temp_dir)
            z_out.write(f, arcname)

# Cleanup
shutil.rmtree(temp_dir)
print(f"[+] Re-packed modified document into: {target_idml} ({target_idml.stat().st_size} bytes)")
