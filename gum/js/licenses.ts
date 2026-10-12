import { readdir, readFile, realpath, stat, writeFile } from 'node:fs/promises'
import { dirname, join } from 'node:path'

// Preserve runtime dependency licenses, including bundled font and map notices.
export async function write_notices(root: string, destination: string) {
    const seen = new Set<string>()
    const notices: string[] = []

    async function visit(directory: string) {
        directory = await realpath(directory)
        if (seen.has(directory)) return
        seen.add(directory)
        const pkg = JSON.parse(await readFile(join(directory, 'package.json'), 'utf8'))
        for (const relative of ['', 'src/fonts', 'data']) {
            const source = join(directory, relative)
            let entries
            try { entries = await readdir(source, { withFileTypes: true }) }
            catch (error) {
                if ((error as NodeJS.ErrnoException).code === 'ENOENT') continue
                throw error
            }
            for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
                if (!entry.isFile() || !/(license|notice|copying|^ofl)/i.test(entry.name)) continue
                const file = join(relative, entry.name)
                const text = await readFile(join(directory, file), 'utf8')
                notices.push(`${pkg.name}@${pkg.version} (${file})\n\n${text}`)
            }
        }

        // Resolve installed packages through node_modules, including local links.
        for (const name of Object.keys(pkg.dependencies ?? {}).sort()) {
            let current = directory
            while (true) {
                const candidate = join(current, 'node_modules', name)
                try { await stat(join(candidate, 'package.json')) }
                catch (error) {
                    if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error
                    const parent = dirname(current)
                    if (parent === current) throw new Error(`Cannot find dependency notices for ${name}`)
                    current = parent
                    continue
                }
                await visit(candidate)
                break
            }
        }
    }

    await visit(root)
    await writeFile(destination, notices.join('\n\n' + '='.repeat(80) + '\n\n') + '\n')
}
