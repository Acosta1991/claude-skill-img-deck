# kie.ai — Referencia de API (GPT Image 2)

Documentación oficial: https://docs.kie.ai/market/gpt/gpt-image-2-text-to-image

## Autenticación
Todas las llamadas requieren cabeceras:
```
Authorization: Bearer $KIE_API_KEY
Content-Type: application/json
```
La key se obtiene en https://kie.ai (Dashboard → API Keys). El script lee la
variable de entorno `KIE_API_KEY`.

## 1. Crear tarea — POST
```
POST https://api.kie.ai/api/v1/jobs/createTask
```
Body:
```json
{
  "model": "gpt-image-2-text-to-image",
  "input": {
    "prompt": "texto de la imagen (máx 20000 chars)",
    "aspect_ratio": "16:9",
    "resolution": "2K"
  }
}
```
- `aspect_ratio`: auto, 1:1, 3:2, 2:3, 4:3, 3:4, 5:4, 4:5, 16:9, 9:16, 2:1,
  1:2, 3:1, 1:3, 21:9, 9:21. (Para slides: **16:9**.)
- `resolution`: 1K, 2K, 4K. Reglas: `1:1` no admite 4K; `auto` solo usa 1K.
- Respuesta: `{ "code":200, "data": { "taskId": "task_gptimage_..." } }`

> Un 200 OK solo significa que la tarea se creó, NO que terminó. Es asíncrona.

## 2. Consultar resultado (poll) — GET
```
GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=task_...
```
Respuesta:
```json
{
  "code": 200,
  "data": {
    "taskId": "task_...",
    "state": "success",                 // waiting | queuing | generating | success | fail
    "resultJson": "{\"resultUrls\":[\"https://...png\"]}",
    "failMsg": ""
  }
}
```
- Hacer poll cada ~3-10 s hasta `state == success` (o `fail`).
- La URL final está en `resultJson.resultUrls[0]` (es un string JSON, hay que parsearlo).

## Otros modelos útiles (mismo patrón createTask/recordInfo)
- `gpt-image-2-image-to-image` — variar/editar a partir de imagen(es) de
  referencia. Requiere URLs públicas de las imágenes de entrada, por lo que
  necesita subir el archivo primero. Por simplicidad, esta skill usa
  text-to-image y mantiene consistencia con un bloque de estilo reutilizable
  (ver prompting.md).
- Marketplace completo: https://kie.ai/market

## Costes / logs
Todas las tareas y su estado quedan en https://kie.ai/logs
