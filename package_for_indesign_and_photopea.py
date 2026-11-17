import zipfile
import shutil
import re
from pathlib import Path
from PIL import Image

base_dir = Path("/home/usuario/Descargas/pycode/indesign_forensics")
links_dir = base_dir / "Links"
links_dir.mkdir(exist_ok=True)

# 1. Map extracted previews to their exact link filenames
# Preview 0 (uad6) -> maxresdefault.jpg
# Preview 1 (uadb) -> Olivia-Rodrigo-high-school-musical-billboard-1548-1610490681.jpg
# Preview 2 (uae1) -> 1900x1900-000000-81-0-0.jpg
# Preview 3 (uafc, uaf5, uae6) -> 712U0PCvjES._UF1000,1000_QL80_.jpg
# Preview 4 (uaf0) -> 199dbd823afa64660d371c09d45ab892-removebg-preview.png
# Preview 5 (ubda) -> Sour_album_logo.png

prev_dir = base_dir / "extracted_previews"

shutil.copy(prev_dir / "preview_0_uad6.jpg", links_dir / "maxresdefault.jpg")
shutil.copy(prev_dir / "preview_1_uadb.jpg", links_dir / "Olivia-Rodrigo-high-school-musical-billboard-1548-1610490681.jpg")
shutil.copy(prev_dir / "preview_2_uae1.jpg", links_dir / "1900x1900-000000-81-0-0.jpg")
shutil.copy(prev_dir / "preview_3_uafc_uaf5_uae6.jpg", links_dir / "712U0PCvjES._UF1000,1000_QL80_.jpg")

# Convert TIFFs to PNGs
with Image.open(prev_dir / "preview_4_uaf0.bin") as img:
    img.save(links_dir / "199dbd823afa64660d371c09d45ab892-removebg-preview.png")

with Image.open(prev_dir / "preview_5_ubda.bin") as img:
    img.save(links_dir / "Sour_album_logo.png")

print(f"[+] Reconstructed links in {links_dir}:")
for f in links_dir.iterdir():
    print(f"  - {f.name} ({f.stat().st_size} bytes)")

# 2. Modify IDML Spreads to relink to relative path 'Links/...'
source_idml = base_dir / "converted.idml"
temp_extract = base_dir / "_temp_relink"
if temp_extract.exists():
    shutil.rmtree(temp_extract)
temp_extract.mkdir()

with zipfile.ZipFile(source_idml, "r") as z:
    z.extractall(temp_extract)

# Update LinkResourceURI in all Spreads
spreads_dir = temp_extract / "Spreads"
pattern = re.compile(r'LinkResourceURI="file:[^"]*?/([^"/]+)"')

for spread_file in spreads_dir.glob("*.xml"):
    xml_text = spread_file.read_text(encoding="utf-8")
    # Replace absolute Windows paths like 'file:D:/.../image.jpg' with 'file:Links/image.jpg'
    new_text = pattern.sub(r'LinkResourceURI="file:Links/\1"', xml_text)
    spread_file.write_text(new_text, encoding="utf-8")

# 3. Create standalone self-contained IDML
fixed_idml = base_dir / "Sin_titulo-1_InDesign2023.idml"
with zipfile.ZipFile(fixed_idml, "w", zipfile.ZIP_DEFLATED) as z_out:
    mimetype = temp_extract / "mimetype"
    if mimetype.exists():
        z_out.write(mimetype, "mimetype", compress_type=zipfile.ZIP_STORED)
    for f in temp_extract.rglob("*"):
        if f.is_file() and f.name != "mimetype":
            z_out.write(f, f.relative_to(temp_extract))

shutil.rmtree(temp_extract)
print(f"[+] Created fixed IDML: {fixed_idml} ({fixed_idml.stat().st_size} bytes)")

# 4. Create complete package ZIP (IDML + Links folder) for InDesign 2023 & Photopea
package_zip = base_dir / "Sin_titulo-1_Paquete_InDesign2023.zip"
with zipfile.ZipFile(package_zip, "w", zipfile.ZIP_DEFLATED) as p_out:
    p_out.write(fixed_idml, "Sin_titulo-1_InDesign2023.idml")
    for link_file in links_dir.glob("*"):
        p_out.write(link_file, f"Links/{link_file.name}")

print(f"[+] Created full InDesign 2023 package ZIP: {package_zip} ({package_zip.stat().st_size} bytes)")
