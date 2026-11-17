# INDD Forensic Studio & Offline Converter

Suite forense de ingeniería inversa, visor y conversor universal para documentos nativos de **Adobe InDesign (`*.indd`)**, 100% offline y sin necesidad de licencias propietarias ni Adobe Cloud.

## 🚀 Capacidades Principales

1. **Visor Multi-Página Offline:**
   - Decodificación y renderizado de pliegos (*Spreads*) y páginas mediante boundary stitching de paquetes XMP y streams JPEG/TIFF.
2. **Conversor Universal a IDML:**
   - Motor nativo compilado en Rust (`storytold/indd-utils`) que transpila estructuras binarias OODB B-Tree a paquetes IDML en **<350 ms**.
   - Compatible nativamente con **InDesign 2023 (v18.x)**, CS4–CC 2026, Affinity Publisher, Scribus y Photopea.
3. **Reparador Anti-Cuadros Amarillos (Asset Linker):**
   - Extrae los proxies gráficos cacheados en el binario `.indd`.
   - Revincula automáticamente los Spreads XML hacia la carpeta `Links/` para evitar enlaces rotos.
4. **Editor de Textos (Story Editor):**
   - Inspección y modificación en memoria de historias de texto sin alterar la integridad de la base de datos binaria.
5. **Doble Modalidad de Ejecución:**
   - **Standalone Single-File:** [`indd_studio_standalone.html`](indd_studio_standalone.html) funciona con doble clic en cualquier navegador (`file://`), sin servidor ni Python.
   - **Local Studio Server:** [`web/server.py`](web/server.py) interfaz REST ultrarrápida en `http://127.0.0.1:8088/`.

## 📦 Estructura del Proyecto

* `indd`: Binario compilado en Rust para Linux x86_64.
* `indd_studio_standalone.html`: Aplicación SPA completa en un único archivo HTML autocontenido (0 servidor).
* `web/`: Frontend interactivo y servidor HTTP local (`server.py`).
* `start_studio.sh`: Script de inicio rápido del servidor local.
* `package_for_indesign_and_photopea.py`: Empaquetador de IDML + carpeta `Links/`.
* `test_web_api.sh`: Suite de validación automatizada de endpoints y entrega de assets.

## 🛠️ Uso Rápido

### Opción 1: Sin Servidor (Doble Clic)
Abra directamente en su navegador:
```bash
google-chrome indd_studio_standalone.html
```

### Opción 2: Servidor Local
```bash
./start_studio.sh
# Visite http://127.0.0.1:8088/
```

## 🔒 Auditoría de Seguridad & Privacidad
* **Zero Telemetría:** Ningún dato o archivo sale de su equipo.
* **Procesamiento en RAM:** Los documentos `.indd` y sus activos se manipulan localmente.
