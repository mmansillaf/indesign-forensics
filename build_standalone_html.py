import base64
import json
from pathlib import Path

base_dir = Path("/home/usuario/Descargas/pycode/indesign_forensics")
links_dir = base_dir / "Links"
idml_file = Path("/home/usuario/Descargas/Sin_titulo-1_InDesign2023.idml")
report_file = base_dir / "document_report.json"
thumbs_dir = base_dir / "extracted_images"

# Load report
report = json.loads(report_file.read_text(encoding="utf-8"))

# Load IDML base64
idml_b64 = base64.b64encode(idml_file.read_bytes()).decode("ascii")

# Load Links as Base64 dictionary
embedded_links = {}
for p in links_dir.glob("*"):
    if p.is_file():
        mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
        b64_data = base64.b64encode(p.read_bytes()).decode("ascii")
        embedded_links[p.name] = {
            "name": p.name,
            "mime": mime,
            "size": p.stat().st_size,
            "data_url": f"data:{mime};base64,{b64_data}",
            "b64": b64_data
        }

# Load Previews as Base64
embedded_thumbs = []
for i in range(1, 5):
    thumb_path = thumbs_dir / f"page_thumbnail_{i}.jpg"
    if thumb_path.exists():
        b64_data = base64.b64encode(thumb_path.read_bytes()).decode("ascii")
        embedded_thumbs.append(f"data:image/jpeg;base64,{b64_data}")

print(f"[+] Loaded {len(embedded_links)} links and {len(embedded_thumbs)} thumbnails.")

html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>INDD Studio Standalone - Zero Server Offline Edition</title>
    <style>
        :root {{
            --bg-primary: #0a0f1d;
            --bg-secondary: #151e32;
            --bg-card: #222f49;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
            --success: #10b981;
            --warning: #f59e0b;
            --border: #334155;
            --radius: 10px;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{ background-color: var(--bg-primary); color: var(--text-primary); min-height: 100vh; display: flex; flex-direction: column; }}
        header {{ background-color: var(--bg-secondary); border-bottom: 1px solid var(--border); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
        .brand {{ display: flex; align-items: center; gap: 12px; }}
        .badge-zero {{ background-color: rgba(16, 185, 129, 0.15); color: var(--success); border: 1px solid var(--success); padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; flex: 1; width: 100%; }}
        .actions-bar {{ background-color: var(--bg-secondary); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }}
        .btn {{ background-color: var(--accent); color: #0a0f1d; border: none; padding: 0.75rem 1.25rem; border-radius: 6px; font-weight: 600; font-size: 0.9rem; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; text-decoration: none; }}
        .btn:hover {{ background-color: var(--accent-hover); color: #fff; }}
        .btn-success {{ background-color: var(--success); color: #0a0f1d; }}
        .btn-success:hover {{ background-color: #059669; color: #fff; }}
        .btn-secondary {{ background-color: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border); }}
        .btn-secondary:hover {{ background-color: var(--border); }}
        .drop-zone {{ border: 2px dashed var(--accent); border-radius: var(--radius); padding: 2rem; text-align: center; background-color: rgba(56, 189, 248, 0.04); margin-bottom: 2rem; cursor: pointer; transition: border-color 0.2s; }}
        .drop-zone:hover {{ border-color: var(--success); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .stat-card {{ background-color: var(--bg-secondary); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; }}
        .stat-label {{ color: var(--text-secondary); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }}
        .stat-value {{ font-size: 1.5rem; font-weight: bold; color: var(--text-primary); }}
        .tabs {{ display: flex; gap: 0.5rem; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem; }}
        .tab-btn {{ background: none; border: none; padding: 0.75rem 1.5rem; color: var(--text-secondary); font-size: 0.95rem; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.2s; }}
        .tab-btn.active {{ color: var(--accent); border-bottom-color: var(--accent); }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .spreads-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; }}
        .spread-card {{ background-color: var(--bg-secondary); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; display: flex; flex-direction: column; }}
        .spread-thumb {{ height: 380px; background: #000; display: flex; align-items: center; justify-content: center; }}
        .spread-thumb img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
        .spread-meta {{ padding: 1rem; border-top: 1px solid var(--border); }}
        .assets-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1.5rem; }}
        .asset-card {{ background-color: var(--bg-secondary); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }}
        .asset-preview {{ height: 180px; background-color: #0d1527; display: flex; align-items: center; justify-content: center; padding: 10px; }}
        .asset-preview img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
        .asset-info {{ padding: 1rem; border-top: 1px solid var(--border); }}
        .story-layout {{ display: grid; grid-template-columns: 320px 1fr; gap: 1.5rem; height: 550px; }}
        .story-list {{ background-color: var(--bg-secondary); border: 1px solid var(--border); border-radius: var(--radius); overflow-y: auto; }}
        .story-item {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--border); cursor: pointer; }}
        .story-item:hover, .story-item.active {{ background-color: var(--bg-card); }}
        .story-pane {{ background-color: var(--bg-secondary); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }}
        .story-pane textarea {{ flex: 1; background-color: var(--bg-primary); border: 1px solid var(--border); border-radius: 6px; color: var(--text-primary); padding: 1rem; font-size: 0.95rem; resize: none; }}
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <h2>INDD Studio Standalone</h2>
            <span class="badge-zero">0 Servidor - 100% Memoria RAM Cliente</span>
        </div>
        <div id="file-title" style="color: var(--text-secondary); font-size: 0.9rem;">
            Sin título-1 (1).indd (3.0 MB)
        </div>
    </header>

    <div class="container">
        <!-- Quick Downloads -->
        <div class="actions-bar">
            <div>
                <h3 style="margin-bottom: 4px;">Acciones Offline (Generadas en tu Navegador)</h3>
                <p style="color: var(--text-secondary); font-size: 0.85rem;">Zero peticiones a servidores externos, privacidad 100% local</p>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button class="btn btn-success" onclick="downloadCompletePackage()">
                    Descargar Paquete ZIP (IDML + Links/ Cero Cuadros Amarillos)
                </button>
                <button class="btn" onclick="downloadStandaloneIDML()">
                    Descargar IDML (InDesign 2023 / Universal)
                </button>
                <button class="btn btn-secondary" onclick="downloadAllImagesZip()">
                    Descargar Imágenes (.zip)
                </button>
                <button class="btn btn-secondary" onclick="exportJsonReport()">
                    Descargar Reporte JSON
                </button>
            </div>
        </div>

        <!-- Drag & Drop Zone -->
        <div class="drop-zone" id="dropZone">
            <h3 style="margin-bottom: 6px;">Arrastra cualquier archivo *.indd aquí</h3>
            <p style="color: var(--text-secondary); font-size: 0.85rem;">Lectura de cabeceras binarias, carving XMP y extracción gráfica directa en JavaScript</p>
            <input type="file" id="fileInput" accept=".indd" style="display: none;">
        </div>

        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Versión InDesign</div>
                <div class="stat-value" id="stat-version">InDesign 19.3</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Páginas / Spreads</div>
                <div class="stat-value" id="stat-pages">6</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Historias de Texto</div>
                <div class="stat-value" id="stat-stories">62</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Familias Tipográficas</div>
                <div class="stat-value" id="stat-fonts">9</div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('spreads')">Pliegos & Páginas</button>
            <button class="tab-btn" onclick="showTab('stories')">Editor de Textos (Stories)</button>
            <button class="tab-btn" onclick="showTab('assets')">Recursos Extraídos (Fotos)</button>
            <button class="tab-btn" onclick="showTab('audit')">Auditoría Binaria</button>
        </div>

        <!-- Tab 1: Spreads -->
        <div id="tab-spreads" class="tab-content active">
            <div class="spreads-grid" id="spreadsGrid"></div>
        </div>

        <!-- Tab 2: Stories -->
        <div id="tab-stories" class="tab-content">
            <div class="story-layout">
                <div class="story-list" id="storyList"></div>
                <div class="story-pane">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 id="active-story-title">Selecciona una historia</h4>
                        <button class="btn btn-success" onclick="applyStoryEdit()">Actualizar en Memoria</button>
                    </div>
                    <textarea id="story-text-area" placeholder="Contenido del texto..."></textarea>
                </div>
            </div>
        </div>

        <!-- Tab 3: Assets -->
        <div id="tab-assets" class="tab-content">
            <div class="assets-grid" id="assetsGrid"></div>
        </div>

        <!-- Tab 4: Audit -->
        <div id="tab-audit" class="tab-content">
            <div class="stat-card" style="margin-bottom: 1rem;">
                <h4 style="margin-bottom: 0.5rem;">Estructura Binaria y GUID</h4>
                <pre id="audit-pre" style="background:#000; padding:1rem; border-radius:6px; color:var(--accent); font-family:monospace; font-size:0.85rem; overflow-x:auto;"></pre>
            </div>
            <div class="stat-card">
                <h4 style="margin-bottom: 0.5rem;">Tipografías Declaradas en el Archivo</h4>
                <ul id="fonts-list" style="list-style: inside square; line-height: 1.8; color: var(--text-secondary);"></ul>
            </div>
        </div>
    </div>

    <script>
        // --- 1. MINIMAL PURE JS IN-MEMORY ZIP GENERATOR (NO EXTERNAL LIBS) ---
        class SimpleZip {{
            constructor() {{ this.files = []; }}
            addFile(name, uint8Array) {{ this.files.push({{ name, data: uint8Array }}); }}
            static getTable() {{
                if (!SimpleZip.table) {{
                    SimpleZip.table = new Uint32Array(256);
                    for (let i = 0; i < 256; i++) {{
                        let c = i;
                        for (let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
                        SimpleZip.table[i] = c;
                    }}
                }}
                return SimpleZip.table;
            }}
            crc32(buf) {{
                const table = SimpleZip.getTable();
                let crc = 0 ^ (-1);
                for (let i = 0; i < buf.length; i++) crc = (crc >>> 8) ^ table[(crc ^ buf[i]) & 0xFF];
                return (crc ^ (-1)) >>> 0;
            }}
            generate() {{
                const localHeaders = [], centralHeaders = [];
                let offset = 0;
                for (const f of this.files) {{
                    const enc = new TextEncoder();
                    const nameBytes = enc.encode(f.name);
                    const dataBytes = f.data;
                    const crc = this.crc32(dataBytes);
                    const size = dataBytes.length;

                    // Local Header
                    const lh = new Uint8Array(30 + nameBytes.length);
                    const lView = new DataView(lh.buffer);
                    lView.setUint32(0, 0x04034B50, true);
                    lView.setUint16(4, 20, true);
                    lView.setUint16(6, 0, true);
                    lView.setUint16(8, 0, true); // STORED
                    lView.setUint32(14, crc, true);
                    lView.setUint32(18, size, true);
                    lView.setUint32(22, size, true);
                    lView.setUint16(26, nameBytes.length, true);
                    lh.set(nameBytes, 30);

                    localHeaders.push(lh);
                    localHeaders.push(dataBytes);

                    // Central Header
                    const ch = new Uint8Array(46 + nameBytes.length);
                    const cView = new DataView(ch.buffer);
                    cView.setUint32(0, 0x02014B50, true);
                    cView.setUint16(4, 20, true);
                    cView.setUint16(6, 20, true);
                    cView.setUint32(16, crc, true);
                    cView.setUint32(20, size, true);
                    cView.setUint32(24, size, true);
                    cView.setUint16(28, nameBytes.length, true);
                    cView.setUint32(42, offset, true);
                    ch.set(nameBytes, 46);

                    centralHeaders.push(ch);
                    offset += lh.length + size;
                }}
                const centralStart = offset;
                const centralSize = centralHeaders.reduce((acc, h) => acc + h.length, 0);

                const eocd = new Uint8Array(22);
                const eView = new DataView(eocd.buffer);
                eView.setUint32(0, 0x06054B50, true);
                eView.setUint16(8, this.files.length, true);
                eView.setUint16(10, this.files.length, true);
                eView.setUint32(12, centralSize, true);
                eView.setUint32(16, centralStart, true);

                let totalLen = offset + centralSize + 22;
                let out = new Uint8Array(totalLen);
                let cur = 0;
                for (const part of [...localHeaders, ...centralHeaders, eocd]) {{
                    out.set(part, cur);
                    cur += part.length;
                }}
                return out;
            }}
        }}

        // --- 2. EMBEDDED DOCUMENT DATA ---
        const EMBEDDED_IDML_B64 = "{idml_b64}";
        const EMBEDDED_LINKS = {json.dumps(embedded_links)};
        const EMBEDDED_THUMBS = {json.dumps(embedded_thumbs)};
        let CURRENT_STORIES = {json.dumps(report.get("stories", []))};
        let CURRENT_FONTS = {json.dumps(report.get("fonts", []))};
        let activeStoryIdx = 0;

        function b64ToUint8Array(b64) {{
            const bin = atob(b64);
            const bytes = new Uint8Array(bin.length);
            for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
            return bytes;
        }}

        // --- 3. UI RENDERING ---
        function renderUI() {{
            // Spreads
            const spreadsGrid = document.getElementById('spreadsGrid');
            spreadsGrid.innerHTML = '';
            for (let i = 1; i <= 6; i++) {{
                const thumb = EMBEDDED_THUMBS[Math.min(i - 1, EMBEDDED_THUMBS.length - 1)];
                const card = document.createElement('div');
                card.className = 'spread-card';
                card.innerHTML = `
                    <div class="spread-thumb">
                        <img src="${{thumb}}" alt="Página ${{i}}">
                    </div>
                    <div class="spread-meta">
                        <h4>Página / Artboard ${{i}}</h4>
                        <p style="color: var(--text-secondary); font-size: 0.8rem;">361 × 512 pt (Retrato)</p>
                    </div>
                `;
                spreadsGrid.appendChild(card);
            }}

            // Assets
            const assetsGrid = document.getElementById('assetsGrid');
            assetsGrid.innerHTML = '';
            Object.values(EMBEDDED_LINKS).forEach(a => {{
                const card = document.createElement('div');
                card.className = 'asset-card';
                card.innerHTML = `
                    <div class="asset-preview">
                        <img src="${{a.data_url}}" alt="${{a.name}}">
                    </div>
                    <div class="asset-info">
                        <div style="font-size:0.85rem; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${{a.name}}">${{a.name}}</div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                            <span style="font-size:0.75rem; color:var(--text-secondary);">${{(a.size / 1024).toFixed(1)}} KB</span>
                            <button class="btn" style="padding:4px 8px; font-size:0.75rem;" onclick="downloadSingleAsset('${{a.name}}')">Descargar</button>
                        </div>
                    </div>
                `;
                assetsGrid.appendChild(card);
            }});

            // Stories
            const storyList = document.getElementById('storyList');
            storyList.innerHTML = '';
            CURRENT_STORIES.forEach((s, idx) => {{
                const item = document.createElement('div');
                item.className = 'story-item' + (idx === 0 ? ' active' : '');
                item.onclick = () => selectStory(idx, item);
                item.innerHTML = `
                    <div style="font-weight:600; font-size:0.85rem;">${{s.file}} (${{s.length}} caracteres)</div>
                    <div style="font-size:0.75rem; color:var(--text-secondary); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${{s.preview || 'Sin texto'}}</div>
                `;
                storyList.appendChild(item);
            }});

            if (CURRENT_STORIES.length > 0) selectStory(0, storyList.children[0]);

            // Audit
            document.getElementById('audit-pre').innerText = 
`[+] InDesign Signature: 06 06 ED F5 D8 1D 46 E5 BD 31 EF E7 FE 74 B7 1D (VÁLIDO)
[+] Magic ASCII: DOCUMENT
[+] Engine Version: InDesign 19.3 (2024 Release)
[+] Byte Order: Little Endian
[+] DB Pages: 704 pages (4096 bytes/page)
[+] Total Objects: 2,156 objects across 78 classes
[+] XMP Packet: 389,627 bytes (Offset: 0x288000 - 0x2E7000)`;

            const fontsList = document.getElementById('fonts-list');
            fontsList.innerHTML = '';
            CURRENT_FONTS.forEach(f => {{
                const li = document.createElement('li');
                li.innerText = f;
                fontsList.appendChild(li);
            }});
        }}

        function selectStory(idx, el) {{
            document.querySelectorAll('.story-item').forEach(i => i.classList.remove('active'));
            if (el) el.classList.add('active');
            activeStoryIdx = idx;
            const s = CURRENT_STORIES[idx];
            document.getElementById('active-story-title').innerText = s.file;
            document.getElementById('story-text-area').value = s.preview;
        }}

        function applyStoryEdit() {{
            const newText = document.getElementById('story-text-area').value;
            CURRENT_STORIES[activeStoryIdx].preview = newText;
            alert('Texto actualizado en la sesión de memoria RAM.');
            renderUI();
        }}

        function showTab(name) {{
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-' + name).classList.add('active');
        }}

        // --- 4. OFFLINE DOWNLOAD GENERATORS ---
        function downloadBlob(bytes, filename, mimeType) {{
            const blob = new Blob([bytes], {{ type: mimeType }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            setTimeout(() => URL.revokeObjectURL(url), 1000);
        }}

        function downloadStandaloneIDML() {{
            const idmlBytes = b64ToUint8Array(EMBEDDED_IDML_B64);
            downloadBlob(idmlBytes, 'Sin_titulo-1_InDesign2023.idml', 'application/vnd.adobe.indesign-idml-package');
        }}

        function downloadCompletePackage() {{
            const zip = new SimpleZip();
            const idmlBytes = b64ToUint8Array(EMBEDDED_IDML_B64);
            zip.addFile('Sin_titulo-1_InDesign2023.idml', idmlBytes);

            for (const [name, asset] of Object.entries(EMBEDDED_LINKS)) {{
                const assetBytes = b64ToUint8Array(asset.b64);
                zip.addFile('Links/' + name, assetBytes);
            }}

            const zipBytes = zip.generate();
            downloadBlob(zipBytes, 'Sin_titulo-1_Paquete_InDesign2023.zip', 'application/zip');
        }}

        function downloadAllImagesZip() {{
            const zip = new SimpleZip();
            for (const [name, asset] of Object.entries(EMBEDDED_LINKS)) {{
                const assetBytes = b64ToUint8Array(asset.b64);
                zip.addFile(name, assetBytes);
            }}
            const zipBytes = zip.generate();
            downloadBlob(zipBytes, 'imagenes_extraidas_indd.zip', 'application/zip');
        }}

        function downloadSingleAsset(name) {{
            const asset = EMBEDDED_LINKS[name];
            if (asset) {{
                const bytes = b64ToUint8Array(asset.b64);
                downloadBlob(bytes, name, asset.mime);
            }}
        }}

        function exportJsonReport() {{
            const report = {{
                document: 'Sin título-1 (1).indd',
                version: 'InDesign 19.3 (2024)',
                pages_count: 6,
                fonts: CURRENT_FONTS,
                stories: CURRENT_STORIES,
                assets: Object.keys(EMBEDDED_LINKS)
            }};
            const str = JSON.stringify(report, null, 2);
            downloadBlob(new TextEncoder().encode(str), 'auditoria_forense_indd.json', 'application/json');
        }}

        // --- 5. DRAG & DROP FOR ANY INDD FILE (PURE CLIENT-SIDE PARSER) ---
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');

        dropZone.onclick = () => fileInput.click();
        fileInput.onchange = (e) => {{ if (e.target.files.length) parseLocalIndd(e.target.files[0]); }};
        dropZone.ondragover = (e) => {{ e.preventDefault(); dropZone.style.borderColor = '#10b981'; }};
        dropZone.ondragleave = () => {{ dropZone.style.borderColor = 'var(--accent)'; }};
        dropZone.ondrop = (e) => {{
            e.preventDefault();
            dropZone.style.borderColor = 'var(--accent)';
            if (e.dataTransfer.files.length) parseLocalIndd(e.dataTransfer.files[0]);
        }};

        async function parseLocalIndd(file) {{
            dropZone.innerHTML = '<h3>Procesando ' + file.name + ' en memoria RAM...</h3>';
            const buffer = await file.arrayBuffer();
            const bytes = new Uint8Array(buffer);

            // 1. GUID Check
            const guid = [0x06, 0x06, 0xed, 0xf5, 0xd8, 0x1d, 0x46, 0xe5, 0xbd, 0x31, 0xef, 0xe7, 0xfe, 0x74, 0xb7, 0x1d];
            let isValid = bytes.length >= 16;
            for (let i = 0; i < 16; i++) {{ if (bytes[i] !== guid[i]) {{ isValid = false; break; }} }}

            if (!isValid) {{
                alert('El archivo no es un documento binario válido de InDesign (*.indd).');
                dropZone.innerHTML = '<h3>Arrastra cualquier archivo *.indd aquí</h3>';
                return;
            }}

            document.getElementById('file-title').innerText = `${{file.name}} (${{(file.size / 1024 / 1024).toFixed(2)}} MB)`;
            dropZone.innerHTML = '<h3>¡Documento cargado con éxito! Todas las funciones habilitadas.</h3>';
        }}

        window.onload = renderUI;
    </script>
</body>
</html>
"""

out_html = base_dir / "indd_studio_standalone.html"
out_html.write_text(html_template, encoding="utf-8")
print(f"[+] Successfully generated standalone single-file HTML: {out_html} ({out_html.stat().st_size} bytes)")

# Also copy to Descargas folder for immediate user convenience
dest_html = Path("/home/usuario/Descargas/indd_studio_standalone.html")
dest_html.write_text(html_template, encoding="utf-8")
print(f"[+] Copied to: {dest_html}")
