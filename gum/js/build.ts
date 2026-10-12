// Bundle the backend and its fonts for Node using the development toolchain.
import { rm } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { write_notices } from './licenses'

const root = fileURLToPath(new URL('.', import.meta.url))
const outdir = join(root, 'build')
// Match acorn-jsx's CommonJS entry so both imports share one parser.
const acorn = createRequire(import.meta.resolve('@gum-jsx/core')).resolve('acorn')

await rm(outdir, { recursive: true, force: true })
const result = await Bun.build({
    entrypoints: [join(root, 'pipe.ts')],
    target: 'node',
    outdir,
    naming: { entry: 'pipe.mjs' },
    plugins: [{
        name: 'deduplicate-acorn',
        setup(build) {
            build.onResolve({ filter: /^acorn$/ }, () => ({ path: acorn }))
        },
    }],
})
if (!result.success) throw new AggregateError(result.logs, 'Backend build failed')
await write_notices(root, join(outdir, 'THIRD_PARTY_NOTICES.txt'))
