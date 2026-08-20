import { access, readFile, readdir } from "node:fs/promises";
import { join } from "node:path";

const dist = new URL("../dist/", import.meta.url);
const required = [
  "index.html",
  "prologo/index.html",
  "capitulos/1-la-pandemia-y-sus-secuelas/index.html",
  "buscar/index.html",
  "robots.txt",
  "sitemap-index.xml",
];

for (const file of required) await access(new URL(file, dist));
const home = await readFile(new URL("index.html", dist), "utf8");
for (const marker of ["lang=\"es\"", "application/ld+json", "978-628-502-066-7", "Saltar al contenido", "Ficha editorial"]) {
  if (!home.includes(marker)) throw new Error(`Falta en la compilación: ${marker}`);
}
if (home.includes('name="robots" content="noindex')) throw new Error("La página inicial pública no debe incluir noindex");
const robots = await readFile(new URL("robots.txt", dist), "utf8");
if (!robots.includes("Allow: /") || !robots.includes("Sitemap:")) throw new Error("robots.txt no habilita el rastreo público");

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  return (await Promise.all(entries.map((entry) => entry.isDirectory() ? walk(join(directory, entry.name)) : [join(directory, entry.name)]))).flat();
}

const files = await walk(dist.pathname.replace(/^\/(.:)/, "$1"));
const htmlFiles = files.filter((file) => file.endsWith(".html"));
for (const file of htmlFiles) {
  const source = await readFile(file, "utf8");
  if (/\\(?:chapter|section|input|gls|textcite|begin)\b/.test(source)) throw new Error(`Comando LaTeX visible en ${file}`);
  if (process.env.BASE_PATH !== "/" && /href="\/((?!20250626_LaberintoFiscalObs|\/|#|https?:).)/.test(source)) throw new Error(`Enlace absoluto sin base en ${file}`);
}
console.log(`Build verificado: ${htmlFiles.length} páginas HTML.`);
