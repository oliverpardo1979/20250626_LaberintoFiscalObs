import test from "node:test";
import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";

const root = new URL("../", import.meta.url);
const content = new URL("src/content/chapters/", root);

test("el índice publicado tiene doce entradas en orden", async () => {
  const book = await readFile(new URL("src/data/book.ts", root), "utf8");
  const entries = [...book.matchAll(/\{ order: \d+, title:/g)];
  assert.equal(entries.length, 12);
  for (const title of ["Prólogo", "Prefacio", "Introducción", "La pandemia y sus secuelas", "Epílogo", "Referencias"]) assert.match(book, new RegExp(title));
});

test("se generan todas las entradas de lectura", async () => {
  const files = (await readdir(content)).filter((file) => file.endsWith(".mdx"));
  assert.equal(files.length, 12);
});

test("el contacto y los perfiles personales del autor están publicados", async () => {
  const book = await readFile(new URL("src/data/book.ts", root), "utf8");
  const footer = await readFile(new URL("src/components/SiteFooter.astro", root), "utf8");
  const introduction = await readFile(new URL("src/content/chapters/03-introduccion.mdx", root), "utf8");
  assert.match(book, /oliverpardo@gmail\.com/);
  assert.ok(book.includes("https://x.com/opardor"));
  assert.ok(book.includes("linkedin.com/in/oliver-pardo-4a606422"));
  assert.match(footer, /mailto:/);
  assert.match(introduction, /mailto:oliverpardo@gmail\.com/);
});

test("el inventario coincide con 21 figuras y 18 tablas publicadas", async () => {
  const visuals = JSON.parse(await readFile(new URL("src/data/visuals.json", root), "utf8"));
  assert.equal(visuals.filter((item) => item.type === "figure").length, 21);
  assert.equal(visuals.filter((item) => item.type === "table").length, 18);
  assert.ok(visuals.every((item) => item.title && item.number && item.sourceFile));
});

test("todas las tablas tienen contenido HTML completo y consistente", async () => {
  const visuals = JSON.parse(await readFile(new URL("src/data/visuals.json", root), "utf8"));
  const tables = visuals.filter((item) => item.type === "table");
  for (const table of tables) {
    assert.ok(table.headers.length > 1, `${table.id}: faltan encabezados`);
    assert.ok(table.rows.length > 0, `${table.id}: faltan filas`);
    assert.ok(table.rows.every((row) => row.length === table.headers.length), `${table.id}: ancho inconsistente`);
    assert.doesNotMatch(JSON.stringify(table), /Conversión pendiente|textbackslash|\\(?:begin|end)\{/i, table.id);
  }
});

test("la tabla 6.3 respeta el total publicado en el PDF definitivo", async () => {
  const visuals = JSON.parse(await readFile(new URL("src/data/visuals.json", root), "utf8"));
  const table = visuals.find((item) => item.id === "table-6-3");
  assert.match(table.rows.at(-1).at(-1), /0,74%/);
});

test("las figuras tienen fuente y descripción alternativa específica", async () => {
  const visuals = JSON.parse(await readFile(new URL("src/data/visuals.json", root), "utf8"));
  for (const figure of visuals.filter((item) => item.type === "figure")) {
    assert.ok(figure.source, `${figure.id}: falta fuente`);
    assert.ok(figure.alt.length >= 60, `${figure.id}: texto alternativo insuficiente`);
    assert.doesNotMatch(figure.alt, /Gráfico publicado que presenta/, figure.id);
  }
});

test("cada visual aparece una sola vez por capítulo", async () => {
  const files = (await readdir(content)).filter((file) => file.endsWith(".mdx"));
  for (const file of files) {
    const mdx = await readFile(new URL(file, content), "utf8");
    const ids = [...mdx.matchAll(/<VisualAnchor visualId="([^"]+)" \/>/g)].map((match) => match[1]);
    assert.equal(new Set(ids).size, ids.length, `${file}: hay anclas visuales duplicadas`);
  }
});

test("no se convierten inclusiones comentadas", async () => {
  const visuals = await readFile(new URL("src/data/visuals.json", root), "utf8");
  for (const excluded of ["flexnoflex", "debt-holders", "tax:summ", "Cierre2024PGN2025"]) assert.ok(!visuals.includes(excluded));
});

test("no se distribuye el PDF definitivo", async () => {
  const publicFiles = await readdir(new URL("public/", root), { recursive: true });
  assert.ok(publicFiles.every((file) => !file.toLowerCase().endsWith(".pdf")));
});

test("la cubierta tampoco se distribuye como activo web", async () => {
  const publicFiles = await readdir(new URL("public/", root), { recursive: true });
  assert.ok(publicFiles.every((file) => !/(^|[\\/])cover\.(?:png|jpe?g|webp|avif|svg)$/i.test(file)));
});

test("el índice de búsqueda no contiene comandos LaTeX", async () => {
  const index = await readFile(new URL("public/search-index.json", root), "utf8");
  assert.doesNotMatch(index, /\\\\(?:begin|end|[A-Za-z]+)/);
});

test("no se filtran entornos LaTeX al contenido publicado", async () => {
  const files = (await readdir(content)).filter((file) => file.endsWith(".mdx"));
  for (const file of files) {
    const mdx = await readFile(new URL(file, content), "utf8");
    assert.doesNotMatch(mdx, /\\\\(?:begin|end)(?:[A-Za-z]+|\{)/, file);
  }
});
