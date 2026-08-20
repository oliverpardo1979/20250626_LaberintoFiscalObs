export const book = {
  title: 'El laberinto fiscal de Colombia',
  subtitle: 'Causas, riesgos y salidas a la crisis fiscal',
  author: 'Oliver Pardo',
  publisher: 'Editorial Pontificia Universidad Javeriana',
  published: 'Octubre de 2025',
  datePublished: '2025-10',
  isbnPrint: '978-628-502-065-0',
  isbnDigital: '978-628-502-066-7',
  doi: 'https://doi.org/10.11144/Javeriana.9786285020667',
  officialPage: 'https://www.javeriana.edu.co/web/editorial/w/laberinto-fiscal-colombia',
  contact: {
    email: 'oliverpardo@gmail.com',
    x: 'https://x.com/opardor',
    linkedin: 'https://www.linkedin.com/in/oliver-pardo-4a606422/'
  },
  description:
    'Desde la pandemia, el gasto público ha crecido de manera persistente sin que los ingresos tributarios hayan seguido el mismo ritmo. El libro explica cómo las rigideces del gasto y la sobreestimación de los ingresos han producido déficits y problemas de liquidez, y plantea rutas para contener las presiones de gasto, aumentar el recaudo y reformar las instituciones que determinan la política fiscal.',
  authorBio:
    'Oliver Pardo es director del Centro Javeriano de Competitividad y profesor asociado de la Pontificia Universidad Javeriana. Economista de la Universidad Nacional de Colombia y doctor en Economía de la London School of Economics. Ha sido director de Política Macroeconómica del Ministerio de Hacienda, director del Observatorio Fiscal de la Pontificia Universidad Javeriana, director de Estudios Económicos de Asobancaria e investigador del Departamento Nacional de Planeación.',
  copyright:
    '© Pontificia Universidad Javeriana y © Oliver Pardo. Las ideas expresadas en el libro son responsabilidad de su autor y no necesariamente representan la opinión de la Pontificia Universidad Javeriana.'
} as const;

export const publishedNavigation = [
  { order: 0, title: 'Prólogo', shortTitle: 'Prólogo', slug: 'prologo', number: null },
  { order: 1, title: 'Prefacio', shortTitle: 'Prefacio', slug: 'prefacio', number: null },
  { order: 2, title: 'Introducción', shortTitle: 'Introducción', slug: 'introduccion', number: null },
  { order: 3, title: 'La pandemia y sus secuelas', shortTitle: 'La pandemia y sus secuelas', slug: 'capitulos/1-la-pandemia-y-sus-secuelas', number: 1 },
  { order: 4, title: 'Dame más gasolina y otras formas de gasto', shortTitle: 'Dame más gasolina', slug: 'capitulos/2-dame-mas-gasolina-y-otras-formas-de-gasto', number: 2 },
  { order: 5, title: 'Lecciones recientes y desafíos inmediatos', shortTitle: 'Lecciones recientes', slug: 'capitulos/3-lecciones-recientes-y-desafios-inmediatos', number: 3 },
  { order: 6, title: 'Perspectivas de la deuda y necesidad de consolidación fiscal', shortTitle: 'Perspectivas de la deuda', slug: 'capitulos/4-perspectivas-de-la-deuda-y-necesidad-de-consolidacion-fiscal', number: 4 },
  { order: 7, title: 'Conteniendo el gasto', shortTitle: 'Conteniendo el gasto', slug: 'capitulos/5-conteniendo-el-gasto', number: 5 },
  { order: 8, title: 'Inevitables como la muerte', shortTitle: 'Inevitables como la muerte', slug: 'capitulos/6-inevitables-como-la-muerte', number: 6 },
  { order: 9, title: 'Reformando las reglas de juego', shortTitle: 'Reformando las reglas', slug: 'capitulos/7-reformando-las-reglas-de-juego', number: 7 },
  { order: 10, title: 'Epílogo', shortTitle: 'Epílogo', slug: 'epilogo', number: null },
  { order: 11, title: 'Referencias', shortTitle: 'Referencias', slug: 'referencias', number: null }
] as const;

export const pendingDecisions = [
  'Mantener la cubierta y el PDF digital completo fuera del sitio público hasta nueva autorización.',
  'Elegir y registrar el dominio definitivo a nombre del autor o de la entidad responsable.',
  'Revisar las diferencias editoriales documentadas en CONTENT_AUDIT.md.'
] as const;
