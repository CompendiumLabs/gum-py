// Point this adapter at an installed Gum workspace without changing its manifest.
import { existsSync, mkdirSync, readFileSync, rmSync, symlinkSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = fileURLToPath(new URL('.', import.meta.url))
const root = resolve(process.argv[2] ?? join(here, '../../../gum-jsx'))
const manifest = JSON.parse(readFileSync(join(here, 'package.json'), 'utf8'))
const packages = Object.keys(manifest.dependencies) as string[]

// Validate every target before replacing any local dependency directory.
for (const name of packages) {
    const target = join(root, name.replace('@gum-jsx/', 'gum-jsx-'))
    if (!existsSync(join(target, 'package.json'))) throw new Error(`Missing Gum package: ${target}`)
}
for (const name of packages) {
    const target = join(root, name.replace('@gum-jsx/', 'gum-jsx-'))
    const link = join(here, 'node_modules', name)
    mkdirSync(join(here, 'node_modules', '@gum-jsx'), { recursive: true })
    rmSync(link, { recursive: true, force: true })
    symlinkSync(target, link, 'dir')
    console.log(`${name} -> ${target}`)
}
