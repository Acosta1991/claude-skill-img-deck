#!/usr/bin/env python3
"""
Renderiza cada .slide de un white-frame HTML a un PNG de 1280x720 usando
Playwright (Chromium). Útil para previsualizar los wireframes y para usarlos
como blueprint visual al redactar los prompts de cada slide.

Requiere: pip install playwright && playwright install chromium
(Playwright ya está instalado en este entorno.)

Uso:
  python3 render_frame.py --html white-frames.html --outdir frames/
  -> frames/frame-01.png, frame-02.png, ...

Salida (stdout JSON):
  {"ok": true, "count": 3, "files": [...]}
"""
import argparse
import json
import os
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--html", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--height", type=int, default=720)
    args = p.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(json.dumps({"ok": False, "error": "Playwright no instalado. Ejecuta: pip install playwright && playwright install chromium"}))
        sys.exit(1)

    os.makedirs(args.outdir, exist_ok=True)
    html_path = "file://" + os.path.abspath(args.html)
    files = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": args.width, "height": args.height},
                                device_scale_factor=2)
        page.goto(html_path)
        slides = page.query_selector_all(".slide")
        for i, slide in enumerate(slides, 1):
            out = os.path.join(args.outdir, f"frame-{i:02d}.png")
            slide.screenshot(path=out)
            files.append(out)
        browser.close()

    print(json.dumps({"ok": True, "count": len(files), "files": files}))


if __name__ == "__main__":
    main()
