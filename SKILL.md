---
name: img-deck
description: Crea presentaciones como PDF de imágenes generadas con IA (kie.ai / GPT Image 2). Flujo guiado en 5 pasos — el usuario explica el contenido, se proponen white frames HTML editables, se aprueba un sistema de diseño en una sola imagen, y se generan todas las slides como imágenes y se montan en un PDF. Úsala cuando el usuario quiera crear una presentación, un deck, slides o un pitch con imágenes generadas por IA.
---

# img-deck — Presentaciones por IA en 5 pasos

Generas presentaciones donde **cada slide es una imagen completa** producida por
`gpt-image-2` de kie.ai, y las montas en un PDF. Los white frames HTML son el
blueprint editable de contenido y layout; el sistema de diseño da la identidad
visual coherente.

## Requisitos previos
- API key de https://kie.ai disponible en `KIE_API_KEY`. El script `kie_image.py`
  la lee del entorno **o de un archivo `.env`** en la raíz del proyecto
  (`KIE_API_KEY=...`). El `.env` se busca subiendo desde el cwd y desde la carpeta
  del script, así que basta tenerlo en la raíz `img_deck/`.
- Python 3 con Pillow (para el PDF) y Playwright (opcional, para previsualizar
  frames). Ambos ya disponibles en este entorno.

## Estructura de trabajo
Crea una carpeta por presentación, p.ej. `decks/<nombre>/` con:
```
decks/<nombre>/
  white-frames.html      # wireframes editables (paso 2)
  design-system.png      # imagen del sistema de diseño aprobada (paso 3)
  prompts/slide-01.txt   # prompt final por slide (paso 4)
  slides/slide-01.png    # imágenes finales (paso 4)
  <nombre>.pdf           # PDF montado (paso 5)
```

---

## PASO 1 — El usuario explica el contenido
Conversa para entender: tema, objetivo, audiencia, número aproximado de slides,
tono y cualquier dato/cifra/mensaje clave. Si falta algo esencial, pregunta.
Resume el contenido en un **outline** numerado de slides (título + idea de cada
una) y confírmalo con el usuario antes de seguir.

## PASO 2 — White frames HTML editables
Copia `templates/white-frame.html` a `decks/<nombre>/white-frames.html` y adáptalo:
una `<section class="slide">` por slide del outline, con el texto propuesto y
notas `[[entre corchetes]]` indicando qué frase va en cada zona y dónde van las
imágenes. Todo es editable (texto, tamaños, posición vía estilos inline).

La plantilla trae un **editor visual integrado**: el usuario abre el HTML en
**Chrome** (`open decks/<nombre>/white-frames.html`) y edita directamente sobre
las slides —clic para cambiar texto, ✛ para mover, ◢ para redimensionar, A+/A−
para el tamaño de letra, "+ Duplicar slide", "Borrar slide", "Borrar bloque"; con
"Vista limpia" oculta los controles para previsualizar y "✎ Volver a editar"
(botón flotante arriba a la derecha) regresa al modo edición— y pulsa **Guardar**
(usa la File System Access API de Chrome para sobrescribir el archivo; en otros
navegadores descarga el HTML para reemplazarlo a mano). Pídele que guarde sobre
`decks/<nombre>/white-frames.html` y, cuando lo haga, **vuelve a leer el archivo**
para extraer los textos/posiciones actualizados al redactar los prompts.

Para un preview en imagen (Chrome headless con perfil aislado):
`"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --user-data-dir="$(mktemp -d)" --hide-scrollbars --window-size=1344,3900 --screenshot=preview.png "file://.../white-frames.html"`
**Itera hasta que apruebe los white frames.** No avances sin su OK.

## PASO 3 — Sistema de diseño (una imagen, requiere aprobación)
Redacta un prompt de "design system board" (ver `references/prompting.md` §3) a
partir del tema y la estética que quiera el usuario. Genéralo:
```
python3 scripts/kie_image.py \
  --prompt-file decks/<nombre>/prompts/design-system.txt \
  --aspect-ratio 16:9 --resolution 2K \
  --out decks/<nombre>/design-system.png
```
Muestra la imagen al usuario. Si pide cambios, ajusta el prompt y regenera
(guarda intentos como `design-system-v2.png`, etc.). **Repite hasta el OK.**

Cuando apruebe, destila de la imagen/acuerdo el **bloque de estilo** reutilizable
(paleta hex, tipografías, mood, tratamiento de imagen) — ver `references/prompting.md` §1.

## PASO 4 — Generar todas las slides
Para cada white frame aprobado, redacta un prompt que combine: el **bloque de
estilo** + el layout y los **textos literales** de ese frame (sigue
`references/prompting.md` §2 — texto entre comillas, poco texto, "ortografía
perfecta en español", 16:9). Guarda cada prompt en `prompts/slide-NN.txt`.

Genera cada slide (numera con cero a la izquierda para que el orden alfabético
sea correcto: `slide-01.png`, `slide-02.png`, ...):
```
python3 scripts/kie_image.py \
  --prompt-file decks/<nombre>/prompts/slide-01.txt \
  --aspect-ratio 16:9 --resolution 2K \
  --out decks/<nombre>/slides/slide-01.png
```
Puedes lanzarlas en paralelo (varias llamadas Bash a la vez). Revisa cada imagen:
si el texto sale mal o el estilo no encaja, ajusta el prompt y regenera esa slide.

## PASO 5 — Montar el PDF
```
python3 scripts/build_pdf.py \
  --dir decks/<nombre>/slides \
  --out decks/<nombre>/<nombre>.pdf
```
Confirma el número de páginas y el orden (lo imprime en JSON). Abre el PDF para
revisión final (`open decks/<nombre>/<nombre>.pdf`) y entrega la ruta al usuario.

---

## Reglas
- **Para entre pasos a pedir aprobación**: white frames (paso 2) y sistema de
  diseño (paso 3) son puertas de aprobación. No generes las 10+ slides (que
  cuestan créditos) sin el OK del diseño.
- Mantén **mismo aspect_ratio (16:9) y resolution (2K)** en todas las slides.
- Numera archivos con dos dígitos para que `build_pdf.py --dir` los ordene bien.
- Si una llamada falla, el script imprime `{"ok": false, "error": "..."}`;
  lee el error (key inválida, rate limit, prompt muy largo) y corrige.
- Detalles de la API en `references/kie-api.md`; técnicas de prompt en
  `references/prompting.md`.
