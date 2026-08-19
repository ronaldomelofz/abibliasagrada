import catalogJson from "@/data/catalog.json"

export type CatalogBook = {
  id: string
  nome: string
  abbrev: string
  testamento: "at" | "nt"
  capitulos: number
  versiculos: number
  notas?: number
}

export const catalog = catalogJson as {
  traducao: string
  ano: number
  fonte?: string
  canone?: string
  livros: CatalogBook[]
  versiculos?: number
  notas?: number
}
