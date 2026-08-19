import { notFound } from "next/navigation"
import { ReaderView } from "@/components/reader-view"
import { catalog, getBook, neighbors } from "@/lib/bible"

export function generateStaticParams() {
  return catalog.livros.flatMap((b) =>
    Array.from({ length: b.capitulos }, (_, i) => ({
      slug: b.id,
      capitulo: String(i + 1),
    }))
  )
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string; capitulo: string }>
}) {
  const { slug, capitulo } = await params
  const meta = catalog.livros.find((b) => b.id === slug)
  return { title: meta ? `${meta.nome} ${capitulo}` : "Leitura" }
}

export default async function ChapterPage({
  params,
}: {
  params: Promise<{ slug: string; capitulo: string }>
}) {
  const { slug, capitulo } = await params
  const meta = catalog.livros.find((b) => b.id === slug)
  if (!meta) notFound()
  const n = Number(capitulo)
  if (!Number.isInteger(n) || n < 1 || n > meta.capitulos) notFound()
  const book = getBook(slug)
  const { prev, next } = neighbors(slug)

  const prevHref =
    n > 1
      ? `/livro/${slug}/${n - 1}/`
      : prev
        ? `/livro/${prev.id}/${prev.capitulos}/`
        : null
  const nextHref =
    n < meta.capitulos
      ? `/livro/${slug}/${n + 1}/`
      : next
        ? `/livro/${next.id}/1/`
        : null

  return <ReaderView book={book} chapter={n} prevHref={prevHref} nextHref={nextHref} />
}
