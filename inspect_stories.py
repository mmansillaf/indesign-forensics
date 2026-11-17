import zipfile
import xml.etree.ElementTree as ET
import json
from pathlib import Path

idml_path = Path("/home/usuario/Descargas/pycode/indesign_forensics/converted.idml")
report = {
    "spreads": [],
    "stories": [],
    "fonts": [],
    "colors": []
}

with zipfile.ZipFile(idml_path, "r") as z:
    # 1. Fonts
    if "Resources/Fonts.xml" in z.namelist():
        fonts_xml = ET.fromstring(z.read("Resources/Fonts.xml"))
        for font in fonts_xml.iter("FontFamily"):
            name = font.attrib.get("Name")
            if name:
                report["fonts"].append(name)
                
    # 2. Spreads
    spread_files = sorted([n for n in z.namelist() if n.startswith("Spreads/Spread_")])
    for s_file in spread_files:
        spread_xml = ET.fromstring(z.read(s_file))
        spread_elem = spread_xml.find(".//Spread")
        pages = [p.attrib.get("Self", "Unknown") for p in spread_xml.iter("Page")]
        text_frames = len(list(spread_xml.iter("TextFrame")))
        rectangles = len(list(spread_xml.iter("Rectangle")))
        ovals = len(list(spread_xml.iter("Oval")))
        report["spreads"].append({
            "file": s_file,
            "pages": pages,
            "text_frames": text_frames,
            "rectangles": rectangles,
            "ovals": ovals
        })
        
    # 3. Stories
    story_files = sorted([n for n in z.namelist() if n.startswith("Stories/Story_")])
    for s_file in story_files:
        story_xml = ET.fromstring(z.read(s_file))
        texts = [c.text for c in story_xml.iter("Content") if c.text]
        full_text = "".join(texts).strip()
        if full_text:
            report["stories"].append({
                "file": s_file,
                "length": len(full_text),
                "preview": full_text[:120]
            })

report_file = Path("/home/usuario/Descargas/pycode/indesign_forensics/document_report.json")
report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(f"[+] Forensic audit report generated successfully: {report_file}")
print(f"  Spreads: {len(report['spreads'])}")
print(f"  Fonts: {len(report['fonts'])}")
print(f"  Stories with text: {len(report['stories'])}")
