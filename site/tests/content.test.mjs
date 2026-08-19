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

test("el inventario coincide con 21 figuras y 18 tablas publicadas", async () => {
  const visuals = JSON.parse(await readFile(new URL("src/data/visuals.json", root), "utf8"));
  assert.equal(visuals.filter((item) => item.type === "figure").length, 21);
  assert.equal(visuals.filter((item) => item.type === "table").length, 18);
  assert.ok(visuals.every((item) => item.title && item.number && item.sourceFile));
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
