import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { fileURLToPath } from 'node:url';

const defaultOrigin = 'https://oliverpardo1979.github.io';
const defaultBase = '/20250626_LaberintoFiscalObs';
const isDevelopment = process.env.NODE_ENV === 'development';
const site = process.env.SITE_URL || defaultOrigin;
const base = process.env.BASE_PATH ?? (isDevelopment ? '/' : defaultBase);
const picomatchCompat = fileURLToPath(new URL('./src/lib/picomatch-compat.mjs', import.meta.url));

export default defineConfig({
  site,
  base,
  output: 'static',
  trailingSlash: 'always',
  integrations: [mdx(), sitemap()],
  vite: {
    resolve: { alias: { picomatch: picomatchCompat } }
  },
  markdown: {
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeKatex],
    shikiConfig: { theme: 'github-light' }
  }
});
