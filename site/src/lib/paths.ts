const normalizedBase = import.meta.env.BASE_URL.endsWith('/')
  ? import.meta.env.BASE_URL
  : `${import.meta.env.BASE_URL}/`;

export function withBase(path = ''): string {
  if (/^(?:https?:|mailto:|tel:|#)/.test(path)) return path;
  const normalizedPath = `/${path.replace(/^\/+/, '')}`.replace(/\/{2,}/g, '/');
  const basePath = normalizedBase === '/' ? '/' : normalizedBase.replace(/\/$/, '');
  if (basePath !== '/' && (normalizedPath === basePath || normalizedPath.startsWith(`${basePath}/`))) {
    return normalizedPath;
  }
  return `${normalizedBase}${normalizedPath.replace(/^\/+/, '')}`.replace(/\/{2,}/g, '/');
}

export function canonicalUrl(path = ''): URL {
  return new URL(withBase(path), import.meta.env.SITE);
}
