#!/usr/bin/env python3
"""
Monta una lista de imágenes (slides) en un único PDF, una imagen por página.

Usa Pillow. Cada página del PDF toma el tamaño de su imagen, así que las
slides deben tener todas la misma relación de aspecto (p.ej. 16:9) para un
resultado uniforme.

Uso:
  # Por carpeta (ordena alfabéticamente: usa nombres tipo slide-01, slide-02...)
  python3 build_pdf.py --dir slides/ --out presentacion.pdf

  # Por lista explícita y ordenada
  python3 build_pdf.py --out presentacion.pdf slide-01.png slide-02.png ...

Salida (stdout JSON):
  {"ok": true, "out": "presentacion.pdf", "pages": 12}
"""
import argparse
import glob
import json
import os
import sys

from PIL import Image


def collect(dir_path, files):
    paths = []
    if dir_path:
        for ext in ("png", "jpg", "jpeg", "webp"):
            paths += glob.glob(os.path.join(dir_path, f"*.{ext}"))
            paths += glob.glob(os.path.join(dir_path, f"*.{ext.upper()}"))
        paths = sorted(set(paths))
    paths += list(files or [])
    return paths


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", help="Carpeta con imágenes (orden alfabético)")
    p.add_argument("--out", required=True, help="Ruta del PDF de salida")
    p.add_argument("--dpi", type=int, default=150)
    p.add_argument("files", nargs="*", help="Imágenes en orden explícito")
    args = p.parse_args()

    paths = collect(args.dir, args.files)
    if not paths:
        print(json.dumps({"ok": False, "error": "No se encontraron imágenes"}))
        sys.exit(1)

    pages = []
    for path in paths:
        img = Image.open(path)
        if img.mode in ("RGBA", "P", "LA"):
            bg = Image.new("RGB", img.size, "white")
            bg.paste(img, mask=img.convert("RGBA").split()[-1])
            img = bg
        else:
            img = img.convert("RGB")
        pages.append(img)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    first, rest = pages[0], pages[1:]
    first.save(args.out, "PDF", resolution=float(args.dpi),
               save_all=True, append_images=rest)
    print(json.dumps({"ok": True, "out": args.out, "pages": len(pages),
                      "order": [os.path.basename(x) for x in paths]}))


if __name__ == "__main__":
    main()
