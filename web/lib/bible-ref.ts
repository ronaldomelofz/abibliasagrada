import { catalog } from "@/lib/catalog"

export function fold(s: string) {
  return s
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .toLowerCase()
    .replace(/[.’'`]/g, "")
    .replace(/\./g, " ")
    .replace(/\s+/g, " ")
    .trim()
}

export type RefBook = {
  id: string
  nome: string
  abbrev: string
  capitulos: number
}

export type BibleRef = {
  books: RefBook[]
  chapter: number
  verse: number | null
}

const ROMAN: Record<string, string> = { "1": "i", "2": "ii", "3": "iii" }

const EXTRA: Record<string, string[]> = {
  genesis: ["genese", "gen"],
  exodo: ["exodo"],
  cantico: ["cantares", "canticos"],
  atos: ["actos", "actos dos apostolos"],
  mateus: ["sao mateus", "s mateus"],
  marcos: ["sao marcos", "s marcos"],
  lucas: ["sao lucas", "s lucas"],
  joao: ["sao joao", "s joao", "evangelho de joao"],
  jo: ["job"],
  salmos: ["salmo"],
  "1-cronicas": ["1 cronicas", "i cronicas", "1 paralipomenos", "cronicas", "paralipomenos"],
  "2-cronicas": ["2 cronicas", "ii cronicas", "2 paralipomenos"],
  apocalipse: ["apoc"],
}

function aliasesFor(id: string, nome: string, abbrev: string): string[] {
  const out = new Set<string>()
  const add = (s: string) => {
    const f = fold(s)
    if (f) out.add(f)
  }
  add(id)
  add(id.replace(/-/g, " "))
  add(id.replace(/-/g, ""))
  add(nome)
  add(abbrev)
  add(abbrev.replace(/(\d)([a-z])/i, "$1 $2"))
  const numbered = id.match(/^(\d)-(.+)$/)
  if (numbered) {
    const [, n, rest] = numbered
    const restName = rest.replace(/-/g, " ")
    add(restName)
    add(`${n} ${restName}`)
    add(`${n}${restName}`)
    add(`${ROMAN[n]} ${restName}`)
  }
  for (const extra of EXTRA[id] ?? []) add(extra)
  return [...out]
}

type BookRow = RefBook & { aliases: string[] }

const BOOKS: BookRow[] = catalog.livros.map((b) => ({
  id: b.id,
  nome: b.nome,
  abbrev: b.abbrev,
  capitulos: b.capitulos,
  aliases: aliasesFor(b.id, b.nome, b.abbrev),
}))

function toRef(b: BookRow): RefBook {
  return { id: b.id, nome: b.nome, abbrev: b.abbrev, capitulos: b.capitulos }
}

function matchKind(needle: string, aliases: string[]): "exact" | "partial" | null {
  if (aliases.includes(needle)) return "exact"
  if (needle.length < 3) return null
  for (const alias of aliases) {
    if (alias.startsWith(needle)) return "partial"
    const core = alias.replace(/^(i|ii|iii|1|2|3) /, "")
    if (core === needle || core.startsWith(needle)) return "partial"
    for (const token of alias.split(" ")) {
      if (token === needle || token.startsWith(needle)) return "partial"
    }
  }
  return null
}

/** Nome completo, abreviatura ou parte (ex.: macabeus → I e II Macabeus). */
export function findBooks(name: string): RefBook[] {
  const n = fold(name)
  if (!n) return []
  const exact: RefBook[] = []
  const partial: RefBook[] = []
  for (const b of BOOKS) {
    const kind = matchKind(n, b.aliases)
    if (kind === "exact") exact.push(toRef(b))
    else if (kind === "partial") partial.push(toRef(b))
  }
  const seen = new Set(exact.map((b) => b.id))
  return [...exact, ...partial.filter((b) => !seen.has(b.id))]
}

/** Livro + capítulo, e versículo só após vírgula ou dois-pontos. */
export function parseBibleRef(raw: string): BibleRef | null {
  const needle = fold(raw)
  if (!needle) return null
  const m = needle.match(/^([a-z0-9 ]+?)(?:\s+|:)?(\d{1,3})(?:\s*[,:]\s*(\d{1,3})?)?$/)
  if (!m) return null
  const books = findBooks(m[1])
  if (!books.length) return null
  return {
    books,
    chapter: Number(m[2]),
    verse: m[3] ? Number(m[3]) : null,
  }
}
