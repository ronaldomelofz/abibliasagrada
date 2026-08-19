import { readFileSync } from "fs"
import { join } from "path"
import { catalog, type CatalogBook } from "@/lib/catalog"

export type { CatalogBook }
export { catalog }

export type Note = { n: number; t: string }
export type Verse = { n: number; t: string; notas?: Note[] }
export type Chapter = { n: number; titulo: string; versiculos: Verse[] }
export type Book = {
  id: string
  nome: string
  abbrev: string
  testamento: "at" | "nt"
  capitulos: Chapter[]
}

export type BookGroup = {
  id: string
  titulo: string
  testamento: "at" | "nt"
  ids: string[]
}

export const GROUPS: BookGroup[] = [
  {
    id: "lei",
    titulo: "Pentateuco",
    testamento: "at",
    ids: ["genesis", "exodo", "levitico", "numeros", "deuteronomio"],
  },
  {
    id: "historicos",
    titulo: "Livros históricos",
    testamento: "at",
    ids: [
      "josue",
      "juizes",
      "rute",
      "1-samuel",
      "2-samuel",
      "1-reis",
      "2-reis",
      "1-cronicas",
      "2-cronicas",
      "esdras",
      "neemias",
      "tobias",
      "judite",
      "ester",
      "1-macabeus",
      "2-macabeus",
    ],
  },
  {
    id: "sabedoria",
    titulo: "Livros sapienciais",
    testamento: "at",
    ids: [
      "jo",
      "salmos",
      "proverbios",
      "eclesiastes",
      "cantico",
      "sabedoria",
      "eclesiastico",
    ],
  },
  {
    id: "profetas",
    titulo: "Profetas",
    testamento: "at",
    ids: [
      "isaias",
      "jeremias",
      "lamentacoes",
      "baruc",
      "ezequiel",
      "daniel",
      "oseias",
      "joel",
      "amos",
      "abdias",
      "jonas",
      "miqueias",
      "naum",
      "habacuc",
      "sofonias",
      "ageu",
      "zacarias",
      "malaquias",
    ],
  },
  {
    id: "evangelhos",
    titulo: "Evangelhos",
    testamento: "nt",
    ids: ["mateus", "marcos", "lucas", "joao"],
  },
  {
    id: "atos",
    titulo: "História apostólica",
    testamento: "nt",
    ids: ["atos"],
  },
  {
    id: "paulo",
    titulo: "Cartas paulinas",
    testamento: "nt",
    ids: [
      "romanos",
      "1-corintios",
      "2-corintios",
      "galatas",
      "efesios",
      "filipenses",
      "colossenses",
      "1-tessalonicenses",
      "2-tessalonicenses",
      "1-timoteo",
      "2-timoteo",
      "tito",
      "filemom",
      "hebreus",
    ],
  },
  {
    id: "catolicas",
    titulo: "Cartas catolicas",
    testamento: "nt",
    ids: ["tiago", "1-pedro", "2-pedro", "1-joao", "2-joao", "3-joao", "judas"],
  },
  {
    id: "apocalipse",
    titulo: "Apocalipse",
    testamento: "nt",
    ids: ["apocalipse"],
  },
]

const bookMap = new Map(catalog.livros.map((b) => [b.id, b]))

export function getCatalogBook(slug: string) {
  return bookMap.get(slug)
}

export function getBook(slug: string): Book {
  const path = join(process.cwd(), "data", "livros", `${slug}.json`)
  return JSON.parse(readFileSync(path, "utf8")) as Book
}

export function neighbors(slug: string) {
  const i = catalog.livros.findIndex((b) => b.id === slug)
  return {
    prev: i > 0 ? catalog.livros[i - 1] : null,
    next: i >= 0 && i < catalog.livros.length - 1 ? catalog.livros[i + 1] : null,
  }
}

export function chapterHasText(book: Book, n: number) {
  const ch = book.capitulos.find((c) => c.n === n)
  return Boolean(ch && ch.versiculos.length > 0)
}

export function totals() {
  return catalog.livros.reduce(
    (acc, b) => {
      acc.livros += 1
      acc.capitulos += b.capitulos
      acc.versiculos += b.versiculos
      acc.notas += b.notas ?? 0
      return acc
    },
    { livros: 0, capitulos: 0, versiculos: 0, notas: 0 }
  )
}
