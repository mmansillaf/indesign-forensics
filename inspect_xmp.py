import re
import xml.etree.ElementTree as ET
from pathlib import Path

target = Path("/home/usuario/Descargas/pycode/indesign_forensics/target.indd")
data = target.read_bytes()

# 1. Extract XMP Packet
xmp_start = data.find(b"<?xpacket begin")
xmp_end = data.find(b"<?xpacket end", xmp_start)
if xmp_start != -1 and xmp_end != -1:
    close_bracket = data.find(b">", xmp_end) + 1
    xmp_raw = data[xmp_start:close_bracket]
    print(f"[+] XMP packet found! Length: {len(xmp_raw)} bytes (Offset: {xmp_start} to {close_bracket})")
    
    # Save raw XMP
    xmp_file = Path("/home/usuario/Descargas/pycode/indesign_forensics/extracted_metadata.xmp")
    xmp_file.write_bytes(xmp_raw)
    print(f"[+] Saved raw XMP to {xmp_file}")

    # Inspect XML tags
    try:
        # Strip xpacket header for standard XML parser
        xml_clean = re.sub(rb"<\?xpacket.*?\?>", b"", xmp_raw).strip()
        root = ET.fromstring(xml_clean)
        print("[+] XML parse successful. Root tag:", root.tag)
        
        # Search for fonts, swatches, pages
        xml_str = xml_clean.decode("utf-8", errors="ignore")
        fonts = re.findall(r'<stFnt:fontName>(.*?)</stFnt:fontName>', xml_str)
        print(f"[+] Fonts detected ({len(fonts)}):", set(fonts))
        
        # Check page count or format
        pages = re.findall(r'<xmpTPg:NPages>(.*?)</xmpTPg:NPages>', xml_str)
        print(f"[+] Pages reported in XMP:", pages)
        
        # Check thumbnails
        thumbs = re.findall(r'<xmpGImg:format>(.*?)</xmpGImg:format>', xml_str)
        print(f"[+] Thumbnail formats:", thumbs)
        
        widths = re.findall(r'<xmpGImg:width>(.*?)</xmpGImg:width>', xml_str)
        heights = re.findall(r'<xmpGImg:height>(.*?)</xmpGImg:height>', xml_str)
        print(f"[+] Thumbnail dimensions (WxH):", list(zip(widths, heights)))

    except Exception as e:
        print("[-] XML parse error:", e)
else:
    print("[-] XMP packet not found")
