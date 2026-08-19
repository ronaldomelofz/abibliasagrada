import Link from "next/link"
import { notFound } from "next/navigation"
import { catalog, getBook, neighbors } from "@/lib/bible"

export function generateStaticParams() {
  return catalog.livros.map((b) => ({ slug: b.id }))
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const meta = catalog.livros.find((b) => b.id === slug)
  return { title: meta?.nome ?? "Livro" }
}

export default async function BookPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const meta = catalog.livros.find((b) => b.id === slug)
  if (!meta) notFound()
  const book = getBook(slug)
  const { prev, next } = neighbors(slug)

  return (
    <main className="mx-auto w-full max-w-3xl px-4 py-12 sm:px-6">
      <p className="text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
        {meta.testamento === "at" ? "Antigo Testamento" : "Novo Testamento"}
      </p>
      <h1 className="mt-2 font-display text-5xl tracking-tight">{meta.nome}</h1>
      <p className="mt-4 text-sm text-muted-foreground">
        {meta.capitulos} capítulos · {meta.versiculos} versículos
        {meta.notas ? ` · ${meta.notas} notas` : ""}
      </p>
      <div className="mt-10 grid grid-cols-5 gap-2 sm:grid-cols-8">
        {book.capitulos.map((ch) => {
          const empty = ch.versiculos.length === 0
          return (
            <Link
              key={ch.n}
              href={`/livro/${slug}/${ch.n}/`}
              className={`flex h-11 items-center justify-center border text-sm ${
                empty
                  ? "border-dashed border-border text-muted-foreground"
                  : "border-border bg-card hover:border-primary hover:text-primary"
              }`}
            >
              {ch.n}
            </Link>
          )
        })}
      </div>
      <nav className="mt-12 flex justify-between text-[12px] uppercase tracking-[0.16em] text-muted-foreground">
        {prev ? (
          <Link href={`/livro/${prev.id}/`} className="hover:text-foreground">
            ← {prev.nome}
          </Link>
        ) : (
          <span />
        )}
        {next ? (
          <Link href={`/livro/${next.id}/`} className="hover:text-foreground">
            {next.nome} →
          </Link>
        ) : null}
      </nav>
    </main>
  )
}
