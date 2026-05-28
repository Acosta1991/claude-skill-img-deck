#!/usr/bin/env python3
"""
Genera una imagen con kie.ai (modelo GPT Image 2) y la descarga a disco.

Solo usa la librería estándar de Python (urllib) — no requiere `requests`.

Uso:
  export KIE_API_KEY="tu_api_key"
  python3 kie_image.py \
      --prompt "Un poster cinematográfico ..." \
      --aspect-ratio 16:9 \
      --resolution 2K \
      --out salida.png

Flags:
  --prompt        (obligatorio) Texto de la imagen. Máx 20000 chars.
  --prompt-file   Lee el prompt desde un archivo (alternativa a --prompt).
  --aspect-ratio  auto,1:1,3:2,2:3,4:3,3:4,5:4,4:5,16:9,9:16,2:1,1:2,
                  3:1,1:3,21:9,9:21  (default 16:9)
  --resolution    1K,2K,4K  (default 2K). Nota: 1:1 no admite 4K; auto solo 1K.
  --model         default gpt-image-2-text-to-image
  --out           ruta del archivo PNG de salida (obligatorio)
  --timeout       segundos máximos de espera al poll (default 300)

Salida (stdout, JSON en la última línea):
  {"ok": true, "out": "salida.png", "task_id": "...", "url": "https://..."}
  {"ok": false, "error": "mensaje"}
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

API_BASE = "https://api.kie.ai/api/v1/jobs"
CREATE_URL = f"{API_BASE}/createTask"
RECORD_URL = f"{API_BASE}/recordInfo"


def load_dotenv():
    """Carga variables de un archivo .env si existe. Busca subiendo desde el
    directorio actual y desde la carpeta del script. No pisa variables ya
    definidas en el entorno. Sin dependencias externas."""
    seen = set()
    starts = [os.getcwd(), os.path.dirname(os.path.abspath(__file__))]
    for start in starts:
        d = start
        while True:
            candidate = os.path.join(d, ".env")
            if candidate not in seen and os.path.isfile(candidate):
                seen.add(candidate)
                with open(candidate, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, _, val = line.partition("=")
                        key = key.strip()
                        val = val.strip().strip('"').strip("'")
                        if key and val and key not in os.environ:
                            os.environ[key] = val
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent


def _http(url, method="GET", headers=None, body=None, timeout=60):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code} en {url}: {detail}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Error de red en {url}: {e.reason}") from None


def create_task(api_key, model, prompt, aspect_ratio, resolution):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    inp = {"prompt": prompt, "aspect_ratio": aspect_ratio}
    # 'auto' solo soporta 1K; no enviamos resolution si aspect=auto.
    if aspect_ratio != "auto":
        inp["resolution"] = resolution
    body = {"model": model, "input": inp}
    res = _http(CREATE_URL, "POST", headers, body, timeout=60)
    if res.get("code") not in (200, 0, None) and not res.get("data"):
        raise RuntimeError(f"createTask falló: {json.dumps(res)}")
    data = res.get("data") or {}
    task_id = data.get("taskId") or data.get("task_id") or res.get("taskId")
    if not task_id:
        raise RuntimeError(f"No se obtuvo taskId. Respuesta: {json.dumps(res)}")
    return task_id


def poll_task(api_key, task_id, timeout):
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{RECORD_URL}?taskId={task_id}"
    deadline = time.time() + timeout
    delay = 3
    while time.time() < deadline:
        res = _http(url, "GET", headers, None, timeout=60)
        data = res.get("data") or {}
        state = (data.get("state") or data.get("status") or "").lower()
        if state in ("success", "succeeded", "completed"):
            raw = data.get("resultJson") or data.get("result_json") or "{}"
            try:
                parsed = json.loads(raw) if isinstance(raw, str) else raw
            except json.JSONDecodeError:
                parsed = {}
            urls = parsed.get("resultUrls") or parsed.get("result_urls") or []
            if not urls:
                raise RuntimeError(f"success sin resultUrls: {json.dumps(data)}")
            return urls[0]
        if state in ("fail", "failed", "error"):
            msg = data.get("failMsg") or data.get("fail_msg") or "sin detalle"
            raise RuntimeError(f"La tarea falló: {msg}")
        # waiting / queuing / generating
        time.sleep(delay)
        delay = min(delay + 2, 10)
    raise RuntimeError(f"Timeout ({timeout}s) esperando la tarea {task_id}")


def download(url, out_path):
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    # El CDN de kie.ai devuelve 403 a peticiones sin User-Agent, así que
    # mandamos uno de navegador.
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        with open(out_path, "wb") as f:
            f.write(resp.read())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt")
    p.add_argument("--prompt-file")
    p.add_argument("--aspect-ratio", default="16:9")
    p.add_argument("--resolution", default="2K")
    p.add_argument("--model", default="gpt-image-2-text-to-image")
    p.add_argument("--out", required=True)
    p.add_argument("--timeout", type=int, default=300)
    args = p.parse_args()

    load_dotenv()
    api_key = os.environ.get("KIE_API_KEY")
    if not api_key:
        print(json.dumps({"ok": False, "error": "KIE_API_KEY no está definida (ni en el entorno ni en .env)"}))
        sys.exit(1)

    prompt = args.prompt
    if args.prompt_file:
        with open(args.prompt_file, encoding="utf-8") as f:
            prompt = f.read().strip()
    if not prompt:
        print(json.dumps({"ok": False, "error": "Falta --prompt o --prompt-file"}))
        sys.exit(1)

    try:
        task_id = create_task(api_key, args.model, prompt, args.aspect_ratio, args.resolution)
        print(f"[kie] tarea creada: {task_id}", file=sys.stderr)
        url = poll_task(api_key, task_id, args.timeout)
        print(f"[kie] lista: {url}", file=sys.stderr)
        download(url, args.out)
        print(json.dumps({"ok": True, "out": args.out, "task_id": task_id, "url": url}))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
