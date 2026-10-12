// JSON lines plus length-prefixed binary payloads for the Python adapter.
import { create_evaluator, layout } from '@gum-jsx/cli'
import { format_image, format_pixels } from '@gum-jsx/cli/kitty'
import { inspect_fragment, render_svg } from '@gum-jsx/core'
import type { OutputPrecision, TextRenderMode, ThemeName } from '@gum-jsx/core'
import { createMathFonts } from '@gum-jsx/math'
import { render_png, render_pixels } from '@gum-jsx/png'
import type { RasterSelection } from '@gum-jsx/png'
import { render_pdf } from '@gum-jsx/pdf'
import { render_pptx } from '@gum-jsx/pptx'

type Options = {
    output_format?: string
    page?: number
    width?: number
    height?: number
    theme?: ThemeName
    background?: string
    ratio?: number
    select?: RasterSelection
    text_mode?: TextRenderMode
    seed?: number
    title?: string
    id_prefix?: string
    precision?: OutputPrecision
    size?: readonly [number, number]
}
type Message = Options & {
    input_format?: string
    data?: string
    bytes_length?: number
}
type Result = { format: string; data: unknown; binary?: Uint8Array }

const evaluator = await create_evaluator()
const fonts = createMathFonts()

// Source diagnostics must never share the protocol's stdout stream.
console.log = console.info = (...args: unknown[]) => console.error(...args)

function error_result(error: unknown): Result {
    const cause = error instanceof Error ? error : new Error(String(error))
    return { format: 'error', data: {
        error: cause.name === 'LayoutError' ? 'LAYOUT' : 'PARSE',
        message: cause.message, stack: cause.stack,
    } }
}

// Binary response metadata records the realized raster size, including sampling.
function binary_result(format: string, binary: Uint8Array,
    size?: readonly [number, number]): Result {
    return { format, data: { length: binary.byteLength, size }, binary }
}

// Read the standard PNG IHDR without expanding binary data to base64.
function png_size(data: Uint8Array): { width: number; height: number } {
    const png = Buffer.from(data.buffer, data.byteOffset, data.byteLength)
    const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])
    if (png.length < 24 || !png.subarray(0, 8).equals(signature)
        || png.toString('ascii', 12, 16) !== 'IHDR') throw new TypeError('Invalid PNG data')
    return { width: png.readUInt32BE(16), height: png.readUInt32BE(20) }
}

function render_jsx(data: string, options: Options): Result {
    const { output_format = 'svg', page, width, height, theme, background,
        ratio, select, seed, id_prefix, precision } = options
    const formats = ['svg', 'png', 'pixels', 'kitty', 'pdf', 'pptx', 'tree', 'json']
    if (!formats.includes(output_format)) throw new TypeError(`Invalid output format: ${output_format}`)
    if (select && !['png', 'pixels', 'kitty'].includes(output_format)) {
        throw new TypeError('select is supported only for PNG, pixels, and kitty output')
    }
    if (!data.trim()) return { format: 'error', data: { error: 'NOCODE', message: 'No JSX source supplied' } }

    // Match the CLI's source sizing, theme precedence, and text rendering policy.
    const raster = ['png', 'pixels', 'kitty'].includes(output_format)
    const text_mode = raster ? 'path' : options.text_mode
        ?? (output_format === 'pdf' ? 'live' : output_format === 'pptx' ? 'mixed' : 'path')
    const value = evaluator.evaluate(data, { seed })
    const result = layout(value, {
        width, height, theme, fonts, textMode: text_mode,
        defaultTheme: output_format === 'kitty' ? 'dark' : 'light',
    })
    // Keep document pages independent, matching the CLI's one-based selection.
    const pages = result.kind === 'value' ? []
        : result.kind === 'document' ? result.pages : [result.fragment]
    if (page !== undefined && (!Number.isSafeInteger(page) || page < 1 || page > pages.length)) {
        throw new RangeError(`page must select a page from 1 to ${pages.length}`)
    }
    const selected = page === undefined ? pages : [pages[page - 1]]
    if (selected.length > 1 && !['pdf', 'pptx', 'tree', 'json'].includes(output_format)) {
        throw new Error(`${output_format.toUpperCase()} output requires one page; `
            + 'use page=... or export as PDF or PPTX')
    }
    if (result.kind === 'value') {
        if (value === undefined) return { format: 'error', data: {
            error: 'NORETURN', message: 'Source did not return a value or element',
        } }
        return { format: 'string', data: typeof value === 'string' ? value : JSON.stringify(value, null, 2) }
    }
    const fragment = selected[0]
    const title = options.title ?? (result.kind === 'document' ? result.title : undefined)
    if (output_format === 'svg') return { format: 'string', data:
        render_svg(fragment, { background, title, id_prefix, precision }) }
    if (output_format === 'tree') return { format: 'string', data: selected.map((item, index) =>
        (selected.length > 1 ? `Page ${index + 1}\n` : '')
        + inspect_fragment(item, { precision })).join('\n\n') }
    if (output_format === 'json') return { format: 'string', data: JSON.stringify(
        result.kind === 'document' && page === undefined ? { title, pages } : fragment) }
    if (output_format === 'pdf') return binary_result('pdf',
        render_pdf(selected, { background, title, precision, fonts }))
    if (output_format === 'pptx') return binary_result('pptx',
        render_pptx(selected, { background, title, fonts }))
    if (output_format === 'pixels') {
        const image = render_pixels(fragment, { background, ratio, select })
        return binary_result('pixels', new Uint8Array(image.data.buffer,
            image.data.byteOffset, image.data.byteLength), [image.width, image.height])
    }

    const png = render_png(fragment, { background, ratio, select })
    if (output_format === 'kitty') return { format: 'kitty', data: format_image(Buffer.from(png)) }
    const size = png_size(png)
    return binary_result('png', png, [size.width, size.height])
}

function handle_message(message: Message, binary: Buffer): Result {
    const { input_format = 'jsx', data = '', ...options } = message
    if (input_format === 'jsx') return render_jsx(data, options)
    if (options.output_format !== 'kitty') throw new TypeError(`${input_format} input supports only kitty output`)
    if (input_format === 'png') {
        png_size(binary)
        return { format: 'kitty', data: format_image(binary) }
    }
    if (input_format === 'pixels') {
        const [width, height] = options.size ?? []
        if (!Number.isSafeInteger(width) || !Number.isSafeInteger(height)
            || width! <= 0 || height! <= 0 || binary.length !== width! * height! * 4) {
            throw new TypeError('Pixels require size=(width, height) and exactly width * height * 4 RGBA bytes')
        }
        return { format: 'kitty', data: format_pixels(binary, { width: width!, height: height! }) }
    }
    throw new TypeError(`Invalid input format: ${input_format}`)
}

// Parse fragmented and coalesced requests without treating binary newlines as headers.
let buffer = Buffer.alloc(0)
let pending: Message | undefined
let length = 0
function receive(chunk: Buffer): void {
    buffer = Buffer.concat([buffer, chunk])
    while (true) {
        if (!pending) {
            const newline = buffer.indexOf(0x0a)
            if (newline < 0) return
            const line = buffer.subarray(0, newline).toString('utf8')
            buffer = buffer.subarray(newline + 1)
            pending = JSON.parse(line) as Message
            length = pending.bytes_length ?? 0
            if (!Number.isSafeInteger(length) || length < 0) throw new TypeError('Invalid bytes_length')
        }
        if (buffer.length < length) return
        const binary = buffer.subarray(0, length), message = pending
        buffer = buffer.subarray(length)
        pending = undefined
        let result: Result
        try { result = handle_message(message, binary) }
        catch (error) { result = error_result(error) }
        write_result(result)
    }
}

function write_result({ binary, ...result }: Result): void {
    process.stdout.write(JSON.stringify(result) + '\n')
    if (binary) process.stdout.write(binary)
}

process.stdin.on('data', (chunk: Buffer) => {
    try { receive(chunk) }
    catch (error) {
        pending = undefined
        buffer = Buffer.alloc(0)
        write_result(error_result(error))
    }
})
