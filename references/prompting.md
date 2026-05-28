# Guía de prompting para slides con gpt-image-2

El reto de generar cada slide como **imagen completa** es: (a) que el texto salga
correcto y legible, y (b) que todas las slides compartan la misma identidad
visual. Estas dos técnicas lo resuelven.

## 1. El "bloque de estilo" (style block)
Tras aprobar el sistema de diseño, destila su descripción en un bloque de texto
reutilizable que se antepone a CADA prompt de slide. Esto da consistencia.

Plantilla del bloque de estilo:
```
ESTILO VISUAL (aplica a toda la presentación):
- Paleta: <colores hex principales y de acento, p.ej. fondo #0E1116, acento #4F8DFF>
- Tipografía: títulos <sans geométrica bold>, cuerpo <sans humanista>, gran jerarquía
- Mood / estética: <p.ej. editorial minimalista, mucho aire, sombras suaves>
- Tratamiento de imagen: <p.ej. ilustración isométrica / foto con duotono / 3D mate>
- Composición: rejilla limpia, márgenes amplios, formato 16:9 horizontal
- Idioma del texto: español, ortografía perfecta
```

## 2. Prompt por slide (basado en el white frame aprobado)
Cada `.slide` del white frame se traduce a un prompt que describe layout +
textos EXACTOS. Pon el texto literal entre comillas para maximizar fidelidad.

Estructura recomendada del prompt completo:
```
<BLOQUE DE ESTILO>

SLIDE <n> — <tipo: portada / contenido / dato>:
Formato 16:9. Composición: <describe dónde va cada bloque según el white frame>.
Renderiza este texto EXACTO, perfectamente legible y bien ortografiado:
- Título (arriba izquierda, grande): "<texto literal del título>"
- Cuerpo (bajo el título): "<bullets o frase literal>"
- <Zona de imagen>: <describe la ilustración/foto y su posición>
Sin marcas de agua. Sin texto de relleno ("lorem ipsum"). Alto contraste y legibilidad.
```

### Consejos clave
- **Poco texto por slide.** Cuanto menos texto, más fiable lo renderiza el modelo.
  Frases cortas > párrafos. Idealmente ≤ 20 palabras visibles por slide.
- **Texto literal entre comillas.** "..." reduce errores de ortografía.
- **Reitera "ortografía perfecta / texto legible / español"** en cada prompt.
- **Una idea por slide.** Si un white frame tiene demasiado texto, divídelo.
- **Mismo aspect_ratio (16:9) y misma resolution (2K) en todas** para uniformidad.
- Si una slide sale con texto incorrecto, regenera ajustando el prompt (acortar
  el texto o describir mejor la posición). Guarda cada intento con nombre claro.

## 3. Prompt del SISTEMA DE DISEÑO (una sola imagen, paso de aprobación)
Genera UNA imagen tipo "style guide" que el usuario aprueba antes de producir slides:
```
Crea una hoja de estilo / design system board en 16:9 para una presentación sobre
<tema>. Muestra en una sola imagen: muestras de paleta de color con sus hex,
ejemplos de tipografía (título y cuerpo) con nombres, 2-3 componentes de ejemplo
(una tarjeta, un bullet, un gráfico), tratamiento de imagen de referencia y el
mood general. Estética: <adjetivos: minimalista/corporativo/editorial/tech/...>.
Etiquetas en español, ortografía perfecta, alta legibilidad.
```
Tras el OK del usuario, extrae de esa imagen (o de su descripción acordada) el
**bloque de estilo** del punto 1 y reúsalo en todas las slides.
