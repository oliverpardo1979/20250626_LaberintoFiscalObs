import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { glob } from 'astro/loaders';

const chapters = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/chapters' }),
  schema: z.object({
    title: z.string(),
    shortTitle: z.string(),
    slug: z.string(),
    order: z.number(),
    kind: z.enum(['front', 'chapter', 'back']),
    chapterNumber: z.number().nullable(),
    author: z.string().optional(),
    description: z.string(),
    sourceFile: z.string()
  })
});

export const collections = { chapters };
