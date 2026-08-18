import type { APIRoute } from "astro";

export const GET: APIRoute = ({ site }) => {
  const isPublic = import.meta.env.PUBLICATION_STATUS === "public";
  const rules = isPublic
    ? `User-agent: *\nAllow: /\nSitemap: ${new URL(`${import.meta.env.BASE_URL}sitemap-index.xml`, site)}\n`
    : "User-agent: *\nDisallow: /\n";

  return new Response(rules, {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};
