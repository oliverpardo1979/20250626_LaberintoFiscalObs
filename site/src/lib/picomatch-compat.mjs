import { createRequire } from 'node:module';

const picomatch = createRequire(import.meta.url)('picomatch');

export default picomatch;
