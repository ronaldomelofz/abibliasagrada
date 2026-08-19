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

export type QueryIntent =
  | { type: "empty" }
  | { type: "books"; books: RefBook[] }
  | { type: "ref"; ref: BibleRef }
  | { type: "unknown-ref"; bookHint: string; chapter: number; verse: number | null }
  | { type: "text"; needle: string }

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

/** Separa «livro capítulo» e, só depois de vírgula, o versículo. */
export function splitRef(raw: string): { book: string; chapter: number; verse: number | null } | null {
  let rest = fold(raw).replace(/[,:]$/, "")
  if (!rest) return null
  let verse: number | null = null
  const withVerse = rest.match(/^(.*)[,:]\s*(\d{1,3})$/)
  if (withVerse && fold(withVerse[1])) {
    verse = Number(withVerse[2])
    rest = fold(withVerse[1])
  }
  const withChapter = rest.match(/^(.*?)(?:\s+|:)(\d{1,3})$/)
  if (!withChapter) return null
  const book = fold(withChapter[1])
  if (!book || !/[a-z]/.test(book)) return null
  return { book, chapter: Number(withChapter[2]), verse }
}

export function parseBibleRef(raw: string): BibleRef | null {
  const intent = interpretQuery(raw)
  return intent.type === "ref" ? intent.ref : null
}

export function interpretQuery(raw: string): QueryIntent {
  const needle = fold(raw)
  if (!needle) return { type: "empty" }

  const split = splitRef(needle)
  if (split) {
    const matched = findBooks(split.book)
    const books = matched.filter((b) => split.chapter >= 1 && split.chapter <= b.capitulos)
    if (books.length) {
      return { type: "ref", ref: { books, chapter: split.chapter, verse: split.verse } }
    }
    return {
      type: "unknown-ref",
      bookHint: split.book,
      chapter: split.chapter,
      verse: split.verse,
    }
  }

  const books = findBooks(needle)
  if (books.length) return { type: "books", books }
  if (needle.length < 3) return { type: "empty" }
  return { type: "text", needle }
}

/** Palavras inteiras; um número não casa o prefixo de outro (1 ≠ 12). */
export function textMatches(haystack: string, needle: string): boolean {
  const hay = fold(haystack)
  const tokens = fold(needle).split(" ").filter(Boolean)
  if (!tokens.length) return false
  return tokens.every((token) => {
    if (/^\d+$/.test(token)) {
      return new RegExp(`(?:^|\\D)${token}(?:\\D|$)`).test(hay)
    }
    return hay.includes(token)
  })
}
