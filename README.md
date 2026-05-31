# img-deck — Presentaciones por IA en 5 pasos

**Skill para [Claude Code](https://claude.com/claude-code)** que crea presentaciones
donde **cada slide es una imagen completa** generada con `gpt-image-2` de
[kie.ai](https://kie.ai), y las monta en un PDF.

En lugar de maquetar diapositivas a mano, le explicas a Claude de qué quieres
hablar; la skill propone wireframes editables, acuerda contigo un sistema de
diseño visual coherente, y genera todas las slides como imágenes que se montan
en un único PDF.

| | |
|---|---|
| **Tipo** | Skill de Claude Code |
| **Salida** | PDF (una imagen por página, 16:9) |
| **Motor de imagen** | kie.ai · GPT Image 2 (`gpt-image-2-text-to-image`) |
| **Idioma** | Cualquier idioma — el deck se genera en el idioma que pidas |

---

## ¿Cómo funciona? — el flujo de 5 pasos

La skill guía una conversación con dos **puertas de aprobación** para que no se
gasten créditos generando slides hasta que el diseño esté aprobado:

1. **Cuentas el contenido.** Conversas con Claude sobre tema, objetivo,
   audiencia, nº de slides y mensajes clave. Claude resume todo en un *outline*.
2. **White frames editables.** Claude crea un HTML con un *wireframe* por slide.
   Trae un **editor visual integrado**: lo abres en el navegador y editas
   directamente sobre las diapositivas (clic para escribir, arrastrar para
   mover/redimensionar, duplicar o borrar slides) y guardas. Para que **"Guardar"
   sobrescriba el mismo archivo en cualquier navegador (incluido Safari)**, Claude
   lo sirve con un editor local (`scripts/edit_server.py`) y abres
   `http://127.0.0.1:8765`. *(puerta de aprobación)*
3. **Sistema de diseño.** Claude genera **una sola imagen** tipo "design system
   board" (paleta, tipografía, componentes, mood). La apruebas o pides cambios.
   *(puerta de aprobación)*
4. **Generar todas las slides.** Con el estilo aprobado, Claude redacta un prompt
   por slide y genera cada imagen (16:9, 2K). Revisa cada una y regenera si hace falta.
5. **Montar el PDF.** Las imágenes se combinan en un PDF, una por página.

```
decks/<nombre>/
  white-frames.html      # wireframes editables (paso 2)
  design-system.png      # sistema de diseño aprobado (paso 3)
  prompts/slide-01.txt   # prompt final por slide (paso 4)
  slides/slide-01.png    # imágenes finales (paso 4)
  <nombre>.pdf           # PDF montado (paso 5)
```

---

## Instalación

### 1. Requisitos
- [Claude Code](https://docs.claude.com/en/docs/claude-code) instalado.
- Una **API key de [kie.ai](https://kie.ai)** (Dashboard → API Keys).
- **Python 3** con:
  - `Pillow` — para montar el PDF (`pip install Pillow`)
  - `playwright` *(opcional)* — solo para previsualizar wireframes en imagen
    (`pip install playwright && playwright install chromium`)
- **Google Chrome** — para el editor visual de los white frames (paso 2).

### 2. Instalar la skill
Clona este repo dentro de tu carpeta de skills de Claude Code. La skill puede
ser de usuario (global) o de proyecto:

```bash
# Skill global (disponible en todos tus proyectos)
git clone https://github.com/Acosta1991/claude-skill-img-deck.git \
  ~/.claude/skills/img-deck

# …o skill de proyecto (solo en este repo)
git clone https://github.com/Acosta1991/claude-skill-img-deck.git \
  .claude/skills/img-deck
```

> La carpeta debe contener `SKILL.md` en su raíz. Si clonas con otro nombre,
> renómbrala a `img-deck`.

### 3. Configurar la API key
La key se lee de la variable de entorno `KIE_API_KEY` **o** de un archivo `.env`
en la raíz de tu proyecto. Copia la plantilla y rellénala:

```bash
cp .env.example .env
# edita .env y pega tu key:  KIE_API_KEY=tu_api_key_aqui
```

El script busca el `.env` subiendo desde el directorio actual, así que basta con
tenerlo en la raíz de tu proyecto. **Nunca subas tu `.env` a git** (ya está en
`.gitignore`).

---

## Uso

Una vez instalada, simplemente pídeselo a Claude Code en lenguaje natural:

> *"Quiero crear una presentación sobre [tu tema]"*
> *"Hazme un deck / pitch / unas slides sobre…"*

Claude reconocerá la skill y te llevará por los 5 pasos, parándose a pedir tu
aprobación en los white frames y en el sistema de diseño.

### Scripts (si quieres ejecutarlos a mano)

```bash
# Generar una imagen con kie.ai
python3 scripts/kie_image.py \
  --prompt-file decks/<nombre>/prompts/slide-01.txt \
  --aspect-ratio 16:9 --resolution 2K \
  --out decks/<nombre>/slides/slide-01.png

# Editar los white frames y que "Guardar" sobrescriba el mismo archivo
# (cualquier navegador, incl. Safari). Abre http://127.0.0.1:8765
python3 scripts/edit_server.py decks/<nombre>/white-frames.html

# Previsualizar los white frames como PNG (requiere Playwright)
python3 scripts/render_frame.py --html decks/<nombre>/white-frames.html --outdir frames/

# Montar el PDF a partir de la carpeta de slides
python3 scripts/build_pdf.py \
  --dir decks/<nombre>/slides \
  --out decks/<nombre>/<nombre>.pdf
```

---

## Estructura del repo

```
SKILL.md                 # instrucciones de la skill (las lee Claude Code)
templates/
  white-frame.html       # plantilla de wireframes con editor visual integrado
scripts/
  kie_image.py           # genera una imagen con kie.ai (solo stdlib de Python)
  build_pdf.py           # monta las imágenes en un PDF (Pillow)
  render_frame.py        # previsualiza wireframes a PNG (Playwright, opcional)
  edit_server.py         # editor local: "Guardar" sobrescribe el HTML (stdlib)
references/
  kie-api.md             # referencia de la API de kie.ai
  prompting.md           # técnicas de prompt para texto legible y estilo coherente
```

---

## Notas y consejos

- **Multiidioma.** La skill funciona en **cualquier idioma**. En el paso 1 se
  fija el idioma del deck (por defecto, el idioma en que escribes) y se reitera
  en cada prompt — eso es lo que hace que el texto salga con ortografía perfecta,
  sea español, inglés, francés, etc.
- **Poco texto por slide.** Cuanto menos texto, más fiable lo renderiza el
  modelo. Frases cortas y texto entre comillas → mejor ortografía. Ver
  [`references/prompting.md`](references/prompting.md).
- **Mantén 16:9 y 2K en todas las slides** para un PDF uniforme.
- **Costes:** cada imagen consume créditos de kie.ai. Las dos puertas de
  aprobación existen para no generar 10+ slides antes de aprobar el diseño.
  Revisa tus tareas en https://kie.ai/logs.
- Numera los archivos con dos dígitos (`slide-01`, `slide-02`…) para que el
  orden alfabético del PDF sea correcto.

## Licencia

MIT — ver [LICENSE](LICENSE).
