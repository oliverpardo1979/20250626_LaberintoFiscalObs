"""Build the web edition from the repository LaTeX and the final print PDF.

The script never modifies the editorial sources. It removes commented LaTeX
before parsing, records excluded assets, and renders published figures from the
final PDF when a reliable SVG build is not available in this environment.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pdfplumber
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
PDF = ROOT.parent / "Libro PDF Definitivo 1ra edición.pdf"
OUT_CONTENT = SITE / "src" / "content" / "chapters"
OUT_DATA = SITE / "src" / "data"
OUT_PUBLIC = SITE / "public"
OUT_FIGURES = OUT_PUBLIC / "assets" / "figures"
OUT_BRAND = OUT_PUBLIC / "assets" / "brand"
TMP = SITE / ".generated"
PDFTOPPM = Path(
    r"C:\Users\olive\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe"
)


CHAPTERS = [
    ("prologo", "Prólogo", "Prólogo", "front", None, "Capitulos/Prologo.tex", "José Antonio Ocampo"),
    ("prefacio", "Prefacio", "Prefacio", "front", None, "Capitulos/Prefacio.tex", None),
    ("introduccion", "Introducción", "Introducción", "front", None, "Capitulos/Introducion.tex", None),
    ("capitulos/1-la-pandemia-y-sus-secuelas", "Capítulo 1. La pandemia y sus secuelas", "La pandemia y sus secuelas", "chapter", 1, "Capitulos/Capitulo01.tex", None),
    ("capitulos/2-dame-mas-gasolina-y-otras-formas-de-gasto", "Capítulo 2. Dame más gasolina y otras formas de gasto", "Dame más gasolina y otras formas de gasto", "chapter", 2, "Capitulos/Capitulo02.tex", None),
    ("capitulos/3-lecciones-recientes-y-desafios-inmediatos", "Capítulo 3. Lecciones recientes y desafíos inmediatos", "Lecciones recientes y desafíos inmediatos", "chapter", 3, "Capitulos/Capitulo03.tex", None),
    ("capitulos/4-perspectivas-de-la-deuda-y-necesidad-de-consolidacion-fiscal", "Capítulo 4. Perspectivas de la deuda y necesidad de consolidación fiscal", "Perspectivas de la deuda y necesidad de consolidación fiscal", "chapter", 4, "Capitulos/Capitulo04.tex", None),
    ("capitulos/5-conteniendo-el-gasto", "Capítulo 5. Conteniendo el gasto", "Conteniendo el gasto", "chapter", 5, "Capitulos/Capitulo05.tex", None),
    ("capitulos/6-inevitables-como-la-muerte", "Capítulo 6. Inevitables como la muerte", "Inevitables como la muerte", "chapter", 6, "Capitulos/Capitulo06.tex", None),
    ("capitulos/7-reformando-las-reglas-de-juego", "Capítulo 7. Reformando las reglas de juego", "Reformando las reglas de juego", "chapter", 7, "Capitulos/Capitulo07.tex", None),
    ("epilogo", "Epílogo", "Epílogo", "back", None, "Capitulos/Epilogo.tex", None),
]


# The order and page references were reconciled with the final printed PDF.
# Page is the physical PDF page, not the printed folio.
FIGURES = [
    ("Figuras/Cap01/PIB", "1.1", "Evolución del PIB", "fig:PIB", 29),
    ("Figuras/Cap01/Gasto", "1.2", "Gasto del GNC", "fig:Gasto", 30),
    ("Figuras/Cap01/Ingreso", "1.3", "Ingresos del GNC", "fig:Ingreso", 31),
    ("Figuras/Cap01/Balance", "1.4", "Balance (déficit o superávit) del GNC", "fig:Balance", 31),
    ("Figuras/Cap01/Deuda", "1.5", "Deuda neta del GNC", "fig:Deuda", 32),
    ("Figuras/Cap01/Intereses", "1.6", "Pago de intereses del GNC", "fig:Intereses", 33),
    ("Figuras/Cap02/BalFEPC", "2.1", "Balance del GNC con y sin ajuste de causación del FEPC", "fig:BalFEPC", 43),
    ("Figuras/Cap02/VF", "2.2", "Vigencias futuras e inversión pública (porcentaje del PIB)", "fig:VF", 46),
    ("Figuras/Cap03/reservas", "3.1", "Evolución de reservas (compromisos sin obligar)", "fig:reservas", 58),
    ("Figuras/Cap03/depositos", "3.2", "Depósitos del Tesoro Nacional", "fig:depositos", 64),
    ("Figuras/Cap04/Deuda2", "4.1", "Proyecciones de la deuda neta del GNC", "fig:consolida", 69),
    ("Figuras/Cap04/BP2", "4.2", "Proyecciones del balance primario del GNC", "fig:bp", 69),
    ("Figuras/Cap05/proyVF", "5.1", "Vigencias futuras para inversión (porcentaje del PIB)", "fig:proyVF", 77),
    ("Figuras/Cap05/transpensiones", "5.2", "Transferencias del GNC para pensiones y asignaciones de retiro", "fig:transpensiones", 80),
    ("Figuras/Cap05/trans_upc", "5.3", "Transferencia del GNC a la Adres*", "fig:trans_upc", 86),
    ("Figuras/Cap05/sgp_forecast", "5.4", "Proyección del SGP como porcentaje del PIB", "fig:sgp_forecast", 89),
    ("Figuras/Cap06/rentacree2", "6.1", "Evolución del recaudo del impuesto a la renta*", "fig:rentacree", 102),
    ("Figuras/Cap06/citrate2", "6.2", "Evolución de la tarifa nominal del impuesto sobre la renta de personas jurídicas*", "fig:citrate", 104),
    ("Figuras/Cap06/vat_rev_rate2", "6.3", "Evolución del recaudo del IVA", "fig:vat_rev_rate", 111),
    ("Figuras/Cap06/contrabando", "6.4", "Valor de las mercancías de contrabando (porcentaje del PIB)", "fig:contrabando", 113),
    ("Figuras/Cap07/flujoPGN", "7.1", "Propuesta para el ciclo de aprobación del PGN", "fig:flujoPGN", 124),
]

TABLES = [
    ("Tablas/Cap02/GastoDesagregado", "2.1", "Desagregación del gasto del GNC (porcentaje del PIB)", "tab:GastoDesagregado"),
    ("Tablas/Cap02/Transferencias2024", "2.2", "Desagregación de transferencias del GNC (porcentaje del PIB)", "tab:Transferencias"),
    ("Tablas/Cap02/Personal", "2.3", "Nómina de la nación presupuestada para el 2025", "tab:Personal"),
    ("Tablas/Cap03/cierre2023PGN2024", "3.1", "Balance del GNC. Cierre del 2023 vs. pronóstico para el PGN del 2024 (porcentaje del PIB)", "tab:cierre2023PGN2024"),
    ("Tablas/Cap03/PGN2024Cierre2024", "3.2", "Balance del GNC. Pronóstico del PGN del 2024 vs. cierre del 2024 (porcentaje del PIB)", "tab:PGN2024Cierre2024"),
    ("Tablas/Cap03/cierre2023cierre2024", "3.3", "Balance del GNC. Cierre del 2023 vs. cierre del 2024 (porcentaje del PIB)", "tab:cierre2023cierre2024"),
    ("Tablas/Cap03/ingtributarios", "3.4", "Desglose de los ingresos tributarios del GNC 2022-2024 (porcentaje del PIB)", "tab:ingresos_tributarios"),
    ("Tablas/Cap03/Cierre2024PF2025", "3.5", "Balance del GNC. Cierre del 2024 vs. MFMP del 2025 (porcentaje del PIB)", "tab:Cierre2024PF2025"),
    ("Tablas/Cap04/flexsemiflex", "4.1", "Composición del gasto por nivel de flexibilidad", "tab:flexsemiflex"),
    ("Tablas/Cap05/costocomp", "5.1", "Costo de las competencias del GNC transferibles a las ET (2024)", "tab:costocomp"),
    ("Tablas/Cap05/nomina", "5.2", "Nómina pública (2023-2025)", "tab:nomina"),
    ("Tablas/Cap06/intaggtax2", "6.1", "Evolución del recaudo de los principales impuestos (porcentaje del PIB)", "tab:intaggtax"),
    ("Tablas/Cap06/bentrib", "6.2", "Gastos tributarios por tipo de impuesto", "tab:bentrib"),
    ("Tablas/Cap06/topact", "6.3", "Top diez de actividades económicas con mayores beneficios en impuesto de renta (2021)", "tab:topact"),
    ("Tablas/Cap06/aportes_colombia", "6.4", "Aportes a seguridad social y parafiscales, según tipo de trabajador y nivel salarial en Colombia", "tab:aportes_colombia"),
    ("Tablas/Cap06/pit_shares", "6.5", "Participación de tipos de rentas sobre el total de ingresos brutos y el total de rentas líquidas de las personas naturales", "tab:composicion_renta"),
    ("Tablas/Cap06/des_gt_iva", "6.6", "Desagregación del gasto tributario del IVA (2023)", "tab:des_gt_iva"),
    ("Tablas/Cap06/othertaxes", "6.7", "Recaudo del resto de impuestos como porcentaje del PIB (2024)", "tab:othertaxes"),
]

EXCLUDED = [
    ("Figuras/Cap04/flexnoflex.tex", "La inclusión está comentada en Capitulo04.tex."),
    ("Figuras/Cap04/debt-holders.tex", "La inclusión está dentro de un entorno comment en Capitulo04.tex."),
    ("Tablas/Cap04/tax-summ.tex", "La inclusión está comentada. El archivo se renombró desde tax:summ.tex para permitir un checkout normal en Windows."),
    ("Tablas/Cap03/Cierre2024PGN2025.tex", "El archivo existe, pero no aparece en una inclusión activa de la edición final."),
]


# Editorial metadata reconciled against the definitive print PDF. These
# overrides are deliberately kept in the web build instead of changing the
# original LaTeX sources.
SOURCE_OVERRIDES = {
    "fig-1-2": "Ministerio de Hacienda y Crédito Público (2025a)",
    "fig-1-3": "Elaboración propia con base en Ministerio de Hacienda y Crédito Público (2025a)",
    "fig-1-4": "Ministerio de Hacienda y Crédito Público (2025a)",
    "fig-1-6": "Ministerio de Hacienda y Crédito Público (2025a)",
    "fig-2-1": "Elaboración propia con base en Ministerio de Hacienda y Crédito Público (2025a)",
    "fig-3-2": "Elaboración propia con base en datos de la Dirección de Crédito Público, Ministerio de Hacienda",
    "fig-7-1": "Elaboración propia",
    "table-2-1": "Elaboración propia con base en Ministerio de Hacienda y Crédito Público (2025a)",
    "table-2-2": "Elaboración propia con base en Ministerio de Hacienda y Crédito Público (2025a)",
    "table-6-5": "Elaboración propia con base en estadísticas de la DIAN del año gravable 2023",
}


FIGURE_ALT_OVERRIDES = {
    "fig-1-1": "Serie anual del índice del PIB real de Colombia entre 2019 y 2024, con 2019 igual a uno.",
    "fig-1-2": "Series anuales del gasto total y del gasto primario del Gobierno Nacional Central como porcentaje del PIB entre 2011 y 2024.",
    "fig-1-3": "Series anuales de los ingresos totales y tributarios del Gobierno Nacional Central como porcentaje del PIB entre 2011 y 2024.",
    "fig-1-4": "Series anuales del balance total y del balance primario del Gobierno Nacional Central como porcentaje del PIB entre 2011 y 2024.",
    "fig-1-5": "Serie anual de la deuda neta del Gobierno Nacional Central como porcentaje del PIB entre 2000 y 2024, junto con el ancla y el límite de la regla fiscal.",
    "fig-1-6": "Serie anual del pago de intereses del Gobierno Nacional Central como porcentaje del PIB entre 2011 y 2024.",
    "fig-2-1": "Comparación anual del balance del Gobierno Nacional Central observado y ajustado por la causación del FEPC entre 2019 y 2024.",
    "fig-2-2": "Series anuales de vigencias futuras y de inversión pública como porcentaje del PIB entre 2019 y 2025.",
    "fig-3-1": "Serie anual de las reservas presupuestales o compromisos sin obligar como porcentaje del PIB entre 2019 y 2024.",
    "fig-3-2": "Depósitos mensuales del Tesoro Nacional en 2024 comparados con el mínimo de 2019 a 2023, en miles de millones de pesos constantes de 2019.",
    "fig-4-1": "Proyecciones de la deuda neta del Gobierno Nacional Central como porcentaje del PIB entre 2019 y 2035 bajo distintos escenarios fiscales.",
    "fig-4-2": "Proyecciones del balance primario del Gobierno Nacional Central como porcentaje del PIB entre 2019 y 2035 bajo distintos escenarios fiscales.",
    "fig-5-1": "Proyección de las vigencias futuras para inversión como porcentaje del PIB entre 2025 y 2030.",
    "fig-5-2": "Proyección de las transferencias para pensiones y asignaciones de retiro como porcentaje del PIB entre 2024 y 2035, desagregada por destino.",
    "fig-5-3": "Proyección de las transferencias del Gobierno Nacional Central a la Adres como porcentaje del PIB entre 2024 y 2035 bajo dos escenarios de la UPC.",
    "fig-5-4": "Proyecciones del Sistema General de Participaciones como porcentaje del PIB entre 2024 y 2038 bajo el MFMP y el acto legislativo.",
    "fig-6-1": "Serie anual del recaudo del impuesto sobre la renta como porcentaje del PIB entre 2012 y 2024, incluido el CREE entre 2013 y 2016.",
    "fig-6-2": "Serie anual de la tarifa nominal del impuesto sobre la renta de personas jurídicas entre 2012 y 2024.",
    "fig-6-3": "Serie anual del recaudo del IVA como porcentaje del PIB entre 2012 y 2024, acompañada por su promedio del período.",
    "fig-6-4": "Valor anual de las mercancías de contrabando como porcentaje del PIB entre 2018 y 2023, acompañado por su promedio del período.",
    "fig-7-1": "Diagrama de seis pasos para la propuesta de validación, presentación y aprobación del Presupuesto General de la Nación.",
}


# A few PDF pages leave less white space between prose and the plot. These
# small, resolution-specific trims remove only that preceding prose after the
# general content-boundary detector has run.
FIGURE_TOP_TRIMS_PX = {
    "fig-2-2": 78,
    "fig-3-1": 28,
    "fig-5-1": 28,
    "fig-7-1": 28,
}


def strip_comments(text: str) -> str:
    text = re.sub(r"\\begin\{comment\}.*?\\end\{comment\}", "", text, flags=re.S)
    cleaned = []
    for line in text.splitlines():
        out = []
        escaped = False
        for idx, char in enumerate(line):
            if char == "%" and not escaped:
                break
            out.append(char)
            if char == "\\":
                escaped = not escaped
            else:
                escaped = False
        cleaned.append("".join(out).rstrip())
    return "\n".join(cleaned)


def read_tex(path: Path) -> str:
    return strip_comments(path.read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")


def extract_braced(text: str, start: int) -> tuple[str, int]:
    depth = 0
    content = []
    for pos in range(start, len(text)):
        ch = text[pos]
        if ch == "{" and (pos == 0 or text[pos - 1] != "\\"):
            depth += 1
            if depth == 1:
                continue
        elif ch == "}" and (pos == 0 or text[pos - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return "".join(content), pos + 1
        if depth >= 1:
            content.append(ch)
    return "".join(content), len(text)


def replace_command(text: str, command: str, fn) -> str:
    token = "\\" + command
    cursor = 0
    while True:
        idx = text.find(token, cursor)
        if idx < 0:
            return text
        brace = idx + len(token)
        if brace >= len(text) or text[brace] != "{":
            cursor = brace
            continue
        inner, end = extract_braced(text, brace)
        text = text[:idx] + fn(inner) + text[end:]
        cursor = idx


def latex_text(value: str) -> str:
    value = value.replace(r"\textbackslash{}", "/").replace(r"\dagger", "†")
    replacements = {
        r"\'a": "á", r"\'e": "é", r"\'i": "í", r"\'\i": "í", r"\'{i}": "í", r"\'o": "ó", r"\'u": "ú",
        r"\'A": "Á", r"\'E": "É", r"\'I": "Í", r"\'O": "Ó", r"\'U": "Ú", r"\~n": "ñ", r"\~{n}": "ñ",
        r"\&": "&", r"\%": r"\%", r"\$": r"\$", r"\#": "#", r"\_": "_", "~": " ",
        "``": "“", "''": "”", "---": "—", "--": "–", r"\,": " ", r"\;": " ", r"\!": "",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    for command in ("textbf", "textit", "emph", "texttt", "mbox", "mathrm", "footnotesize", "small", "Large"):
        value = replace_command(value, command, lambda x: x)
    value = replace_command(value, "textsuperscript", lambda x: f"^{x}")
    value = re.sub(r"\\(noindent|centering|raggedright|raggedleft|newpage|clearpage|pagebreak|linebreak|smallskip|medskip|bigskip)\b", "", value)
    value = re.sub(r"\\vspace\*?\{[^{}]*\}", "", value)
    value = re.sub(r"\\hspace\*?\{[^{}]*\}", "", value)
    value = re.sub(r"\\(?:par|quad|qquad)\b", " ", value)
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def markdown_inline_html(value: str) -> str:
    value = value.replace(r"\%", "%").replace(r"\$", "$")
    value = re.sub(r"\$\^\{?(\d+)\}?\$", r"<sup>\1</sup>", value)
    value = value.replace("$†$", "<sup>†</sup>")
    value = re.sub(r"\^(\d+)", r"<sup>\1</sup>", value)
    value = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", value)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"\*(.+?)\*", r"<em>\1</em>", value)
    return value


def glossary() -> dict[str, str]:
    text = (ROOT / "Principal.tex").read_text(encoding="utf-8")
    return {key: short for key, short, _long in re.findall(r"\\newacronym\{([^}]+)\}\{([^}]+)\}\{([^}]+)\}", text)}


GLOSSARY = glossary()


def parse_bib() -> dict[str, dict[str, str]]:
    text = (ROOT / "bibliografia.bib").read_text(encoding="utf-8")
    entries: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,]+),", text):
        kind, key = match.group(1), match.group(2).strip()
        start = match.end()
        depth = 1
        pos = start
        while pos < len(text) and depth:
            if text[pos] == "{": depth += 1
            elif text[pos] == "}": depth -= 1
            pos += 1
        body = text[start:pos - 1]
        fields: dict[str, str] = {"kind": kind}
        for fm in re.finditer(r"(?ms)^\s*(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|[^,\n]+)\s*,?", body):
            raw = fm.group(2).strip().strip('{}"')
            fields[fm.group(1).lower()] = latex_text(raw)
        entries[key] = fields
    return entries


BIB = parse_bib()


def citation(keys: str, textual: bool = False) -> str:
    rendered = []
    for key in keys.split(","):
        entry = BIB.get(key.strip(), {})
        author = entry.get("author", key.strip())
        first_author = author.split(" and ")[0] if author else key.strip()
        corporate_terms = ("Ministerio", "Dirección", "Departamento", "Comité", "Banco", "Gobierno", "DIAN", "CARF", "OCDE", "OECD")
        surname = first_author if any(term in first_author for term in corporate_terms) else first_author.split(",")[0].split()[-1]
        year = entry.get("year", "s. f.")
        rendered.append(f"{surname} ({year})" if textual else f"{surname}, {year}")
    return "; ".join(rendered) if textual else "(" + "; ".join(rendered) + ")"


VISUAL_ROWS = []
for source, number, title, label, page in FIGURES:
    VISUAL_ROWS.append({"id": f"fig-{number.replace('.', '-')}", "type": "figure", "number": number, "title": title,
                        "label": label, "sourceFile": source + ".tex", "pdfPage": page})
for source, number, title, label in TABLES:
    VISUAL_ROWS.append({"id": f"table-{number.replace('.', '-')}", "type": "table", "number": number, "title": title,
                        "label": label, "sourceFile": source + ".tex", "pdfPage": None})
BY_SOURCE = {row["sourceFile"].removesuffix(".tex").replace("\\", "/"): row for row in VISUAL_ROWS}
BY_LABEL = {row["label"]: row for row in VISUAL_ROWS}


def plain_inline(text: str) -> str:
    text = replace_command(text, "gls", lambda x: GLOSSARY.get(x, x.upper()))
    text = replace_command(text, "Gls", lambda x: GLOSSARY.get(x, x.upper()))
    text = re.sub(r"\(\\cite\{([^}]+)\}\)", lambda m: citation(m.group(1)), text)
    text = replace_command(text, "textcite", lambda x: citation(x, textual=True))
    text = replace_command(text, "parencite", lambda x: citation(x))
    text = replace_command(text, "cite", lambda x: citation(x))
    text = replace_command(text, "textbf", lambda x: f"**{plain_inline(x)}**")
    text = replace_command(text, "textit", lambda x: f"*{plain_inline(x)}*")
    text = replace_command(text, "emph", lambda x: f"*{plain_inline(x)}*")
    text = replace_command(text, "href", lambda url: url)  # second argument handled below where present
    text = re.sub(r"(https?://\S+)\{([^{}]+)\}", lambda m: f"[{plain_inline(m.group(2))}]({m.group(1)})", text)
    text = replace_command(text, "url", lambda x: f"<{x}>")
    text = replace_command(text, "footnote", lambda x: f" <span class=\"inline-note\" role=\"note\">({plain_inline(x)})</span>")

    def ref_repl(match):
        label = match.group(1)
        visual = BY_LABEL.get(label)
        if visual:
            return f"[{visual['number']}](#{visual['id']})"
        chapter_numbers = {
            "chap:antecedentes": "1", "chap:fepc": "2", "chap:juego": "3", "chap:perspectivas": "4",
            "chap:menosgasto": "5", "chap:masingresos": "6", "chap:normas": "7",
        }
        return chapter_numbers.get(label, "")

    text = re.sub(r"\\(?:auto|page)?ref\{([^}]+)\}", ref_repl, text)
    text = latex_text(text)
    text = html.escape(text, quote=False).replace("&lt;a href=", "<a href=").replace("&lt;/a&gt;", "</a>")
    text = text.replace("&lt;span class=\"inline-note\" role=\"note\"&gt;", '<span class="inline-note" role="note">').replace("&lt;/span&gt;", "</span>")
    text = re.sub(r"\s+([,.;:?!])", r"\1", text)
    return text.strip()


def extract_source_note(tex: str) -> tuple[str, str]:
    tail = tex
    source = ""
    notes = []
    for raw in re.findall(r"\\(?:par\s*)?\\?footnotesize\{(.*?)\}", tail, flags=re.S):
        clean = plain_inline(raw)
        normalized = clean.strip("* ")
        if normalized.lower().startswith("fuente:"):
            source = normalized.split(":", 1)[1].strip().rstrip(".*")
        elif clean:
            notes.append(clean)
    if not source:
        match = re.search(r"Fuente:\s*(.*?)(?:\\end|$)", tail, flags=re.S | re.I)
        if match:
            source = plain_inline(match.group(1))
    return source.rstrip("."), " ".join(notes)


def extract_table_environment(tex: str) -> tuple[str, int] | None:
    """Return the first active table body using balanced LaTeX arguments."""
    candidates = []
    for environment in ("tabularx", "tabular", "longtable"):
        token = rf"\begin{{{environment}}}"
        position = tex.find(token)
        if position >= 0:
            candidates.append((position, environment, token))
    if not candidates:
        return None
    position, environment, token = min(candidates)
    cursor = position + len(token)
    arguments = 2 if environment == "tabularx" else 1
    for _ in range(arguments):
        while cursor < len(tex) and tex[cursor].isspace():
            cursor += 1
        if cursor >= len(tex) or tex[cursor] != "{":
            return None
        _, cursor = extract_braced(tex, cursor)
    end_token = rf"\end{{{environment}}}"
    end = tex.find(end_token, cursor)
    if end < 0:
        return None
    return tex[cursor:end], end + len(end_token)


def parse_table(row: dict) -> dict:
    tex = read_tex(ROOT / row["sourceFile"])
    environment = extract_table_environment(tex)
    if not environment:
        return {"headers": [], "rows": [], "notes": "Conversión pendiente: estructura LaTeX no reconocida.", "source": ""}
    body, environment_end = environment
    body = re.sub(r"\\(?:hline|toprule|midrule|bottomrule)\b", "", body)
    body = re.sub(r"\\(?:cline|cmidrule)\{[^}]+\}", "", body)
    body = re.sub(r"\\addlinespace(?:\[[^]]*\])?", "", body)
    chunks = re.split(r"(?<!\\)\\\\(?:\[[^]]*\])?", body)
    parsed = []
    for chunk in chunks:
        cells = re.split(r"(?<!\\)&", chunk)
        values = []
        for cell in cells:
            cell = re.sub(r"\\multicolumn\{\d+\}\{[^}]+\}\{(.*)\}", r"\1", cell.strip())
            cell = re.sub(r"\\multirow(?:\[[^]]*\])?\{[^}]+\}\{[^}]+\}\{(.*)\}", r"\1", cell)
            clean = markdown_inline_html(plain_inline(cell).replace("\\", "").strip())
            if clean:
                values.append(clean)
            elif len(cells) > 1:
                values.append("")
        if values and any(values):
            parsed.append(values)
    width = max((len(r) for r in parsed), default=0)
    parsed = [r + [""] * (width - len(r)) for r in parsed]
    source, notes = extract_source_note(tex[environment_end:])
    result = {"headers": parsed[0] if parsed else [], "rows": parsed[1:] if len(parsed) > 1 else [], "notes": markdown_inline_html(notes), "source": source}

    # Table 6.4 has a two-tier printed header. Flattening it preserves the
    # column relationships for screen readers and narrow horizontal scrolling.
    if row["id"] == "table-6-4":
        result["headers"] = [
            "Aportes / IBC", "1 SMLMV — dependiente", "1 SMLMV — independiente",
            "2 SMLMV — dependiente", "2 SMLMV — independiente",
            "4 SMLMV — dependiente", "4 SMLMV — independiente",
            "10 SMLMV — dependiente", "10 SMLMV — independiente",
        ]
        if result["rows"] and "Dep." in " ".join(result["rows"][0]):
            result["rows"] = result["rows"][1:]

    # The definitive PDF corrects the arithmetic total printed in table 6.3.
    if row["id"] == "table-6-3" and result["rows"]:
        result["rows"][-1][-1] = "<strong>0,74%</strong>"

    if row["id"] in SOURCE_OVERRIDES:
        result["source"] = SOURCE_OVERRIDES[row["id"]]
    return result


def clean_document(tex: str) -> str:
    tex = re.sub(r"\\chapter\*?\{.*?\}(?:\\label\{[^}]+\})?", "", tex, count=1, flags=re.S)
    # The custom environments in the editorial sources are not consistently
    # named in Spanish: Prefacio.tex and Introducion.tex use the English names
    # ``preface`` and ``introduction``. Remove both variants before inline
    # conversion so LaTeX control words can never leak into the reading text.
    frontmatter_environments = (
        "prologo|prefacio|introduccion|epilogo|"
        "prologue|preface|introduction|epilogue"
    )
    tex = re.sub(
        rf"\\(?:begin|end)\{{(?:{frontmatter_environments})\}}",
        "",
        tex,
    )
    tex = re.sub(r"\\begin\{flushright\}|\\end\{flushright\}", "", tex)
    tex = re.sub(r"\\Large", "", tex)
    tex = re.sub(r"\\label\{[^}]+\}", "", tex)
    for source, visual in BY_SOURCE.items():
        tex = re.sub(r"\\input\{" + re.escape(source) + r"(?:\.tex)?\s*\}", f"\n\n[[VISUAL:{visual['id']}]]\n\n", tex)
    tex = re.sub(r"\\input\{[^}]+\}", "", tex)
    tex = re.sub(r"\\begin\{itemize\}", "\n", tex)
    tex = re.sub(r"\\end\{itemize\}", "\n", tex)
    tex = re.sub(r"\\item\s*", "\n- ", tex)
    tex = re.sub(r"\\begin\{enumerate\}", "\n", tex)
    tex = re.sub(r"\\end\{enumerate\}", "\n", tex)
    return tex


def section_heading(block: str, chapter_number: int | None, counters: dict[str, int]) -> str | None:
    for command, level in (("section", 2), ("subsection", 3), ("subsubsection", 4)):
        prefix = "\\" + command + "{"
        if block.strip().startswith(prefix):
            start = block.index("{")
            title, _ = extract_braced(block, start)
            clean = plain_inline(title)
            if level == 2:
                counters["section"] += 1
                counters["subsection"] = 0
                number = f"{chapter_number}.{counters['section']}" if chapter_number else ""
            elif level == 3:
                counters["subsection"] += 1
                number = f"{chapter_number}.{counters['section']}.{counters['subsection']}" if chapter_number else ""
            else:
                number = ""
            label = f"{number} {clean}".strip()
            return f"\n{'#' * level} {label}\n"
    return None


def convert_chapter(tex: str, chapter_number: int | None) -> tuple[str, list[str]]:
    tex = clean_document(tex)
    blocks = re.split(r"\n\s*\n", tex)
    out = []
    pending: list[str] = []
    used: list[str] = []
    counters = {"section": 0, "subsection": 0}
    for raw in blocks:
        block = raw.strip()
        if not block:
            continue
        marker = re.fullmatch(r"\[\[VISUAL:([^]]+)\]\]", block)
        if marker:
            visual_id = marker.group(1)
            if visual_id not in used and visual_id not in pending:
                pending.append(visual_id)
            continue
        heading = section_heading(block, chapter_number, counters)
        if heading:
            out.append(heading)
            continue
        if block.startswith("-"):
            lines = []
            for line in block.splitlines():
                lines.append("- " + plain_inline(line.removeprefix("-").strip()) if line.lstrip().startswith("-") else plain_inline(line))
            out.append("\n".join(lines))
            continue
        references = [BY_LABEL[label]["id"] for label in re.findall(r"\\ref\{([^}]+)\}", block) if label in BY_LABEL]
        paragraph = plain_inline(block.replace("\n", " "))
        if paragraph:
            out.append(paragraph)
        to_insert = []
        for visual_id in references:
            if visual_id not in used and visual_id not in to_insert:
                to_insert.append(visual_id)
        if not to_insert and pending and paragraph:
            to_insert.append(pending[0])
        for visual_id in to_insert:
            out.append(f'<VisualAnchor visualId="{visual_id}" />')
            used.append(visual_id)
            if visual_id in pending:
                pending.remove(visual_id)
    for visual_id in pending:
        if visual_id not in used:
            out.append(f'<VisualAnchor visualId="{visual_id}" />')
            used.append(visual_id)
    return "\n\n".join(out), used


def figure_alt(row: dict) -> str:
    return FIGURE_ALT_OVERRIDES[row["id"]]


def render_pdf_page(page: int, output: Path, dpi: int = 180) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    # Poppler's Windows build cannot reliably open a Unicode input filename.
    # Work from an ASCII-only copy while preserving the definitive PDF untouched.
    safe_pdf = TMP / "book-final.pdf"
    if not safe_pdf.exists() or safe_pdf.stat().st_mtime < PDF.stat().st_mtime:
        safe_pdf.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PDF, safe_pdf)
    subprocess.run([str(PDFTOPPM), "-f", str(page), "-l", str(page), "-r", str(dpi), "-png", "-singlefile", str(safe_pdf), str(output.with_suffix(""))], check=True)


def pdf_caption_positions(document, page_number: int) -> list[float]:
    words = document.pages[page_number - 1].extract_words()
    return sorted([float(word["top"]) for word in words if word["text"] == "Figura"])


def detect_figure_top(image: Image.Image, left: int, right: int, top_limit: int, bottom: int) -> int:
    """Locate the nearest continuous graphic block above a PDF caption."""
    gray = image.convert("L")
    pixels = gray.load()
    sample_step = 2
    active_threshold = max(5, int((right - left) / sample_step * 0.0025))
    gap_required = max(14, int(image.height * 0.006))
    seen_content = False
    gap = 0
    highest_content = bottom
    for y in range(bottom - 1, top_limit - 1, -1):
        ink = sum(1 for x in range(left, right, sample_step) if pixels[x, y] < 238)
        if ink >= active_threshold:
            seen_content = True
            gap = 0
            highest_content = y
        elif seen_content:
            gap += 1
            if gap >= gap_required:
                return max(top_limit, highest_content - 10)
    return top_limit


def render_figures() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    OUT_FIGURES.mkdir(parents=True, exist_ok=True)
    grouped: dict[int, list[dict]] = {}
    for row in VISUAL_ROWS:
        if row["type"] == "figure":
            grouped.setdefault(row["pdfPage"], []).append(row)
    with pdfplumber.open(PDF) as doc:
        for page_number, figures in grouped.items():
            raster = TMP / f"pdf-page-{page_number}.png"
            render_pdf_page(page_number, raster, 210)
            image = Image.open(raster)
            pdf_page = doc.pages[page_number - 1]
            scale_x = image.width / float(pdf_page.width)
            scale_y = image.height / float(pdf_page.height)
            caption_tops = pdf_caption_positions(doc, page_number)
            # Filter duplicated production-mark captions if present.
            caption_tops = [y for y in caption_tops if y < float(pdf_page.height) - 45]
            for index, row in enumerate(figures):
                cap = caption_tops[min(index, len(caption_tops) - 1)] if caption_tops else float(pdf_page.height) * 0.72
                previous_bottom = caption_tops[index - 1] + 58 if index > 0 and len(caption_tops) > index - 1 else 24
                spans = {
                    "fig-1-1": 180, "fig-1-2": 180, "fig-1-3": 205, "fig-1-4": 205, "fig-1-5": 180, "fig-1-6": 220,
                    "fig-2-1": 190, "fig-2-2": 190, "fig-3-1": 170, "fig-3-2": 205,
                    "fig-4-1": 200, "fig-4-2": 200, "fig-5-1": 160, "fig-5-2": 195, "fig-5-3": 190, "fig-5-4": 175,
                    "fig-6-1": 185, "fig-6-2": 185, "fig-6-3": 173, "fig-6-4": 160, "fig-7-1": 310,
                }
                span = spans[row["id"]]
                manual_top = max(previous_bottom, cap - span)
                left_px = int(34 * scale_x)
                right_px = int((float(pdf_page.width) - 34) * scale_x)
                bottom = max(manual_top + 24, cap - 5)
                bottom_px = int(bottom * scale_y)
                top_px = detect_figure_top(image, left_px, right_px, int(manual_top * scale_y), bottom_px)
                # Keep a conservative fallback for unusually sparse diagrams.
                if bottom_px - top_px < int(70 * scale_y):
                    top_px = int(manual_top * scale_y)
                crop = image.crop((left_px, top_px, right_px, bottom_px))
                trim = FIGURE_TOP_TRIMS_PX.get(row["id"], 0)
                if trim:
                    crop = crop.crop((0, trim, crop.width, crop.height))
                out = OUT_FIGURES / f"{row['id']}.png"
                crop.save(out, optimize=True)
                row["image"] = f"/assets/figures/{out.name}"


def render_brand_assets() -> None:
    OUT_BRAND.mkdir(parents=True, exist_ok=True)
    for name in ("cover-final.png", "cover-final-1000.webp", "cover-final-600.webp"):
        path = OUT_BRAND / name
        if path.exists():
            path.unlink()

    font_candidates = [
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]

    def font(size: int):
        for candidate in font_candidates:
            if candidate.exists():
                return ImageFont.truetype(str(candidate), size)
        return ImageFont.load_default()

    # Original web-only identity. It uses the documented palette and an
    # abstract maze, but it does not reproduce or crop the printed cover.
    og = Image.new("RGB", (1200, 630), "#341a22")
    draw = ImageDraw.Draw(og)
    red = "#a32429"
    green = "#a9b12a"
    paper = "#fbf8f0"
    width = 22
    draw.rectangle((65, 65, 430, 565), outline=red, width=width)
    draw.line((120, 125, 315, 125, 315, 255, 185, 255, 185, 445), fill=red, width=width, joint="curve")
    draw.line((120, 500, 285, 500, 285, 365, 385, 365), fill=red, width=width, joint="curve")
    draw.line((380, 105, 380, 220, 245, 220, 245, 330, 360, 330, 360, 500), fill=green, width=width, joint="curve")
    draw.text((500, 135), "EL LABERINTO", font=font(62), fill=paper)
    draw.text((500, 207), "FISCAL DE COLOMBIA", font=font(62), fill=paper)
    draw.text((503, 315), "CAUSAS, RIESGOS Y SALIDAS", font=font(27), fill=green)
    draw.text((503, 355), "A LA CRISIS FISCAL", font=font(27), fill=green)
    draw.text((503, 465), "Oliver Pardo", font=font(31), fill=paper)
    og.save(OUT_BRAND / "social-card.png", optimize=True)

    fav = Image.new("RGB", (256, 256), "#341a22")
    fav_draw = ImageDraw.Draw(fav)
    fav_draw.rectangle((18, 18, 238, 238), outline=red, width=16)
    fav_draw.line((58, 62, 171, 62, 171, 126, 101, 126, 101, 198), fill=red, width=16, joint="curve")
    fav_draw.line((198, 55, 198, 158, 145, 158, 145, 212), fill=green, width=16, joint="curve")
    fav.save(OUT_BRAND / "favicon.png", optimize=True)
    logo_page = TMP / "logo-page-7.png"
    render_pdf_page(7, logo_page, 240)
    with Image.open(logo_page) as im:
        # The published three-mark lockup is located across the top of the credits page.
        crop = im.crop((int(im.width * 0.08), int(im.height * 0.055), int(im.width * 0.92), int(im.height * 0.13)))
        crop.save(OUT_BRAND / "published-institutional-lockup.png", optimize=True)
    shutil.copy2(ROOT / "Logo_Ofiscal_color_vertical.png", OUT_BRAND / "logo-ofiscal-color-vertical.png")


def build_content() -> None:
    OUT_CONTENT.mkdir(parents=True, exist_ok=True)
    search_rows = []
    audit_rows = []
    chapter_visuals: dict[str, list[str]] = {}
    for order, (slug, title, short, kind, number, source, author) in enumerate(CHAPTERS, start=1):
        tex = read_tex(ROOT / source)
        mdx, used = convert_chapter(tex, number)
        chapter_visuals[slug] = used
        description = re.sub(r"<[^>]+>|\[[^]]+\]\([^)]*\)|[*#]", "", mdx.split("\n\n")[0]).strip()[:240]
        front = ["---", f'title: "{title}"', f'shortTitle: "{short}"', f'slug: "{slug}"', f"order: {order}", f'kind: "{kind}"',
                 f"chapterNumber: {number if number is not None else 'null'}", f'description: "{description.replace(chr(34), chr(39))}"', f'sourceFile: "{source}"']
        if author:
            front.append(f'author: "{author}"')
        front.extend(["---", "", 'import VisualAnchor from "../../components/VisualAnchor.astro";', "", mdx, ""])
        filename = f"{order:02d}-{slug.replace('/', '-')}.mdx"
        (OUT_CONTENT / filename).write_text("\n".join(front), encoding="utf-8")
        clean_search = re.sub(r"\\(?:begin|end)(?:preface|introduction)\b", " ", mdx)
        clean_search = re.sub(r"<[^>]+>|\[[^]]+\]\([^)]*\)|[*#{}]", " ", clean_search)
        search_rows.append({"title": title, "slug": slug, "kind": kind, "text": re.sub(r"\s+", " ", clean_search)})
        for visual_id in used:
            visual = next(item for item in VISUAL_ROWS if item["id"] == visual_id)
            audit_rows.append((source, title, visual["type"], visual["number"], visual["title"], f"/{slug}/#{visual_id}", visual["sourceFile"]))

    cited = set()
    all_tex = "\n".join(read_tex(ROOT / row[5]) for row in CHAPTERS)
    for raw in re.findall(r"\\(?:textcite|parencite|cite)\{([^}]+)\}", all_tex):
        cited.update(key.strip() for key in raw.split(","))
    refs = []
    for key in sorted(cited, key=lambda item: (BIB.get(item, {}).get("author", item), BIB.get(item, {}).get("year", ""))):
        entry = BIB.get(key)
        if not entry:
            refs.append(f"- {key}. [Entrada citada no localizada en bibliografia.bib].")
            continue
        author = entry.get("author", "Autor no especificado").replace(" and ", "; ")
        year = entry.get("year", "s. f.")
        title = entry.get("title", "Sin título")
        container = entry.get("journal") or entry.get("booktitle") or entry.get("publisher") or entry.get("institution") or ""
        url = entry.get("doi") or entry.get("url") or ""
        suffix = f" [{url}](https://doi.org/{url})" if entry.get("doi") else (f" [Enlace]({url})" if url else "")
        refs.append(f"- {author} ({year}). *{title}*. {container}.{suffix}")
    ref_front = """---
title: "Referencias"
shortTitle: "Referencias"
slug: "referencias"
order: 12
kind: "back"
chapterNumber: null
description: "Referencias bibliográficas citadas en la obra."
sourceFile: "bibliografia.bib"
---

"""
    (OUT_CONTENT / "12-referencias.mdx").write_text(ref_front + "\n".join(refs) + "\n", encoding="utf-8")
    search_rows.append({"title": "Referencias", "slug": "referencias", "kind": "back", "text": " ".join(refs)})

    (OUT_PUBLIC / "search-index.json").write_text(json.dumps(search_rows, ensure_ascii=False), encoding="utf-8")
    audit = ["# Auditoría de contenido", "", "Generado a partir del PDF definitivo y de las inclusiones LaTeX activas después de retirar comentarios.", "",
             "| Archivo de capítulo | Capítulo publicado | Tipo | N.º | Título publicado | Ruta web | Fuente del activo |", "|---|---|---:|---:|---|---|---|"]
    audit += [f"| `{a}` | {b} | {c} | {d} | {e} | `{f}` | `{g}` |" for a, b, c, d, e, f, g in audit_rows]
    audit += ["", "## Diferencias y exclusiones relevantes", "",
              "- El PDF definitivo prevalece en capitalización, numeración, títulos, créditos e identidad institucional.",
              "- `Capitulos/Capitulo03.tex` conserva un título anterior comentado; no se publicó.",
              "- Algunas fuentes contienen versiones alternativas después de comentarios; solo se procesó la primera estructura activa incluida por el capítulo.",
              "- La tabla 6.3 totaliza 0,74 % del PIB en el PDF definitivo; el archivo `Tablas/Cap06/topact.tex` conserva 0,63 %. La versión web usa 0,74 % y no modifica el fuente editorial.",
              "- Las figuras se publican como recortes PNG de alta resolución del PDF definitivo: el entorno no dispone de una cadena TeX capaz de garantizar SVG fiel. El archivo LaTeX original queda inventariado como fuente.", ""]
    for path, reason in EXCLUDED:
        audit.append(f"- `{path}`: {reason}")
    (SITE / "CONTENT_AUDIT.md").write_text("\n".join(audit) + "\n", encoding="utf-8")


def write_inventory() -> None:
    lines = ["# Inventario de activos", "", "## Figuras publicadas (21)", "", "| N.º | Archivo fuente | PDF | Activo web |", "|---:|---|---:|---|"]
    for row in VISUAL_ROWS:
        if row["type"] == "figure":
            lines.append(f"| {row['number']} | `{row['sourceFile']}` | {row['pdfPage']} | `public{row['image']}` |")
    lines += ["", "## Tablas publicadas (18)", "", "| N.º | Archivo fuente | Conversión |", "|---:|---|---|"]
    for row in VISUAL_ROWS:
        if row["type"] == "table":
            lines.append(f"| {row['number']} | `{row['sourceFile']}` | HTML semántico |")
    lines += ["", "## Marcas", "", "| Activo | Procedencia | Tratamiento |", "|---|---|---|",
              "| `logo-ofiscal-color-vertical.png` | Repositorio | Copia sin alteraciones |",
              "| `published-institutional-lockup.png` | Página de créditos del PDF definitivo | Recorte de alta resolución, sin redibujo ni recoloración |",
              "| `social-card.png` y `favicon.png` | Identidad web original | Composición tipográfica y laberinto abstracto; no reproducen la cubierta |", "", "## Excluidos", "",
              "- `Cover.pdf`, `Cover.png` y derivados de la cubierta — excluidos de `site/public` por decisión del autor."]
    for path, reason in EXCLUDED:
        lines.append(f"- `{path}` — {reason}")
    (SITE / "ASSET_INVENTORY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not PDF.exists():
        raise SystemExit(f"No se encontró el PDF definitivo: {PDF}")
    render_brand_assets()
    render_figures()
    for row in VISUAL_ROWS:
        if row["type"] == "figure":
            source_tex = read_tex(ROOT / row["sourceFile"])
            source, notes = extract_source_note(source_tex)
            source = SOURCE_OVERRIDES.get(row["id"], source)
            row.update({"alt": figure_alt(row), "source": source, "notes": markdown_inline_html(notes), "format": "PNG de alta resolución extraído del PDF definitivo"})
        else:
            row.update(parse_table(row))
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    (OUT_DATA / "visuals.json").write_text(json.dumps(VISUAL_ROWS, ensure_ascii=False, indent=2), encoding="utf-8")
    build_content()
    write_inventory()
    print(f"Generados {len(CHAPTERS) + 1} textos, {len(FIGURES)} figuras y {len(TABLES)} tablas.")


if __name__ == "__main__":
    main()
