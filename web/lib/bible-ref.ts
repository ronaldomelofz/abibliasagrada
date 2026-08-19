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

export type RefBook = { id: string; nome: string }
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
  "1-cronicas": ["1 cronicas", "i cronicas", "1 paralipomenos"],
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
    add(`${n} ${restName}`)
    add(`${n}${restName}`)
    add(`${ROMAN[n]} ${restName}`)
  }
  for (const extra of EXTRA[id] ?? []) add(extra)
  return [...out]
}

const ALIASES: { alias: string; id: string; nome: string }[] = catalog.livros.flatMap((b) =>
  aliasesFor(b.id, b.nome, b.abbrev).map((alias) => ({ alias, id: b.id, nome: b.nome }))
)

function booksFor(name: string): RefBook[] {
  const n = fold(name)
  if (!n) return []
  const seen = new Set<string>()
  const books: RefBook[] = []
  for (const row of ALIASES) {
    if (row.alias !== n || seen.has(row.id)) continue
    seen.add(row.id)
    books.push({ id: row.id, nome: row.nome })
  }
  return books
}

/** Livro + capítulo, e versículo só após vírgula ou dois-pontos. */
export function parseBibleRef(raw: string): BibleRef | null {
  const needle = fold(raw)
  if (!needle) return null
  const m = needle.match(/^([a-z0-9 ]+?)(?:\s+|:)?(\d{1,3})(?:\s*[,:]\s*(\d{1,3})?)?$/)
  if (!m) return null
  const books = booksFor(m[1])
  if (!books.length) return null
  return {
    books,
    chapter: Number(m[2]),
    verse: m[3] ? Number(m[3]) : null,
  }
}
