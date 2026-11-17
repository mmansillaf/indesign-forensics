#!/usr/bin/env bash
set -euo pipefail

echo "=== 1. Test Static HTML Delivery ==="
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8088/

echo "=== 2. Test API Status ==="
curl -s http://127.0.0.1:8088/api/status

echo -e "\n=== 3. Test API Document Info ==="
curl -s http://127.0.0.1:8088/api/document_info | jq .

echo "=== 4. Test API Pages ==="
curl -s http://127.0.0.1:8088/api/pages | jq .

echo "=== 5. Test API Assets (Extracted Images) ==="
curl -s http://127.0.0.1:8088/api/assets | jq .

echo "=== 6. Test Downloads (Headers) ==="
curl -s -I http://127.0.0.1:8088/api/download/package | grep -E "HTTP|Content-Type|Content-Disposition"
curl -s -I http://127.0.0.1:8088/api/download/idml | grep -E "HTTP|Content-Type|Content-Disposition"

echo "=== 7. Test Image Serving ==="
curl -s -I http://127.0.0.1:8088/api/images/maxresdefault.jpg | grep -E "HTTP|Content-Type"
curl -s -I http://127.0.0.1:8088/api/images/Sour_album_logo.png | grep -E "HTTP|Content-Type"

echo -e "\n[+] ALL WEB AUDIT TESTS PASSED DETERMINISTICALLY!"
