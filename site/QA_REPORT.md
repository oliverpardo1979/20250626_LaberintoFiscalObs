# Informe de calidad

Validación ejecutada el 18 de agosto de 2026 sobre una compilación de producción local.

## Compilación y contenido

- `astro check`: 0 errores, 0 advertencias y 0 indicaciones.
- Pruebas editoriales: 5 de 5 aprobadas.
- Compilación estática: 15 páginas generadas.
- Verificador del artefacto: sin comandos LaTeX visibles, rutas críticas presentes, metadatos y datos estructurados incluidos.
- Inventario: 21 figuras y 18 tablas publicadas; cuatro activos excluidos por no pertenecer a la edición impresa.
- El PDF definitivo no aparece en `public/` ni en la salida del sitio.
- La cubierta y sus derivados no aparecen en `public/`; la imagen social y el favicon son composiciones originales para la web.

## Lighthouse

Lighthouse 13.4.1, Chrome headless, perfil móvil predeterminado, vista previa de producción minificada. La página inicial se volvió a auditar después de excluir la cubierta:

| Página | Rendimiento | Accesibilidad | Buenas prácticas | SEO |
|---|---:|---:|---:|---:|
| Inicio | 100 | 100 | 100 | 100 |
| Capítulo 1 | 100 | 100 | 100 | 100 |

Informes completos:

- `qa/lighthouse-home.json`
- `qa/lighthouse-chapter.json`

Lighthouse completó y escribió ambos informes. En Windows, Chrome Launcher emitió después una advertencia `EPERM` al intentar borrar su carpeta temporal bloqueada; esta ocurrió tras producir los resultados y no afecta las puntuaciones ni el sitio.

## Pruebas funcionales en navegador

- Escritorio, 1440 × 1000: retícula de dos columnas, panel visual `sticky`, cambio automático de figura 1.1 a figura 1.2 mediante `IntersectionObserver`.
- Móvil, 390 × 844: panel fijo desactivado, figura integrada después del primer párrafo que la menciona, ancho de documento sin desbordamiento horizontal.
- Tabla 2.1 en móvil: contenedor enfocable, desplazamiento horizontal interno y encabezados `sticky`; la tabla no ensancha la página.
- Vista ampliada: apertura mediante botón con nombre accesible y cierre mediante control visible.
- Búsqueda local: 11 resultados para `deuda`.
- Semántica: `lang="es"`, enlace “Saltar al contenido”, un `main`, textos alternativos presentes y encabezados de tabla con `scope`.

## Capturas

- `qa/home-desktop.png`
- `qa/home-mobile.png`
- `qa/chapter-desktop.png`
- `qa/chapter-mobile.png`
