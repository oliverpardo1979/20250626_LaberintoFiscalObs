# Sitio web de *El laberinto fiscal de Colombia*

Edición web estática del libro de Oliver Pardo, construida con Astro, TypeScript y MDX. El sitio separa el contenido editorial (`src/content`) de la interfaz y de los activos. Está preparado para GitHub Pages, funciona bajo la ruta del repositorio y admite un dominio propio sin cambiar su arquitectura.

## Requisitos

- Node.js 22 o superior.
- pnpm 10.
- Solo para regenerar el contenido: Python 3.12, `pdfplumber`, Pillow y Poppler (`pdftoppm`). El PDF definitivo debe estar fuera de `site/public`.

## Desarrollo local

```bash
cd site
pnpm install
pnpm dev
```

Astro sirve el sitio en `http://localhost:4321/`. En desarrollo, `base` es `/`.

## Validación y construcción

```bash
pnpm check
pnpm test
pnpm build
node scripts/check-build.mjs
```

La salida se genera en `site/dist/`. `pnpm preview` permite revisar esa compilación.

## Regenerar el contenido editorial

El script `scripts/build-content.py`:

1. retira comentarios de línea y entornos `comment` antes de interpretar LaTeX;
2. convierte los capítulos a MDX;
3. transforma las tablas publicadas a HTML semántico;
4. renderiza como PNG de alta resolución las figuras publicadas del PDF definitivo;
5. crea los inventarios, el índice de búsqueda y `CONTENT_AUDIT.md`.

```powershell
python scripts/build-content.py
```

La ruta del PDF se resuelve como `../Libro PDF Definitivo 1ra edición.pdf` respecto al repositorio. Las figuras se extraen como alternativa documentada porque esta máquina no dispone de una cadena LaTeX que garantice SVG fiel para TikZ/PGFPlots. El script nunca modifica los `.tex` ni el PDF.

## Estructura

```text
site/
├─ public/                  # Activos web; no contiene el PDF
├─ scripts/                 # Conversión y control del build
├─ src/
│  ├─ components/          # Visuales, navegación y marcas
│  ├─ content/chapters/    # Un archivo MDX por unidad publicada
│  ├─ data/                # Metadatos e inventario de visuales
│  ├─ layouts/             # SEO, lectura y panel sticky
│  ├─ pages/               # Inicio, lector, búsqueda y 404
│  └─ styles/
├─ tests/
├─ ASSET_INVENTORY.md
├─ CONTENT_AUDIT.md
├─ DECISIONS_REQUIRING_APPROVAL.md
└─ DOMAIN_SETUP.md
```

## Publicación en GitHub Pages

El workflow `../.github/workflows/deploy-pages.yml` construye y valida el sitio antes de desplegarlo. En `Settings → Pages`, la fuente debe ser **GitHub Actions**.

Configuración inicial:

- `SITE_URL=https://oliverpardo1979.github.io`
- `BASE_PATH=/20250626_LaberintoFiscalObs`
- `PUBLICATION_STATUS=public`

El modo público es ahora el valor predeterminado: las páginas pueden indexarse y `robots.txt` permite el rastreo. Para una revisión privada futura, cree temporalmente la variable `PUBLICATION_STATUS=staging`; ese modo añade `noindex, nofollow, noarchive` y bloquea el rastreo en `robots.txt`.
- URL resultante: `https://oliverpardo1979.github.io/20250626_LaberintoFiscalObs/`

Estas variables ya tienen esos valores como predeterminados. Si se usan variables del repositorio, se configuran en `Settings → Secrets and variables → Actions → Variables`.

Para un dominio propio:

- `SITE_URL=https://www.DOMINIO-ELEGIDO`
- `BASE_PATH=/`

La guía completa está en [DOMAIN_SETUP.md](./DOMAIN_SETUP.md).

Los resultados de compilación, pruebas funcionales y Lighthouse están en [QA_REPORT.md](./QA_REPORT.md).

## Decisiones editoriales y permisos

Por decisión del autor, la versión web y los usos descritos de las marcas institucionales pasan a estado de publicación abierta. No se incluye la cubierta, un enlace de descarga ni una copia pública del PDF; esos materiales permanecen excluidos por decisión del autor. La portada web, la imagen social y el favicon utilizan una composición original que no reproduce la cubierta impresa. Tampoco se instala analítica, cookies o rastreadores. Las decisiones que todavía requieren intervención del autor están en [DECISIONS_REQUIRING_APPROVAL.md](./DECISIONS_REQUIRING_APPROVAL.md).
