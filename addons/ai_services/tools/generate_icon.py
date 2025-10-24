"""Generate a small PNG icon file for the ai_services module.

Run this script from the module root (or from workspace root). It writes
`static/description/icon.png` using an embedded base64 PNG. This is a
1x1 transparent PNG which Odoo will scale for display; you can replace it
with a better image later.
"""
import os
import base64

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE_DIR, 'static', 'description')
os.makedirs(OUT_DIR, exist_ok=True)

# 1x1 transparent PNG (base64)
PNG_B64 = (
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII='
)

out_path = os.path.join(OUT_DIR, 'icon.png')
with open(out_path, 'wb') as f:
    f.write(base64.b64decode(PNG_B64))

print('Wrote', out_path)
