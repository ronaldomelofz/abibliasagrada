import Link from "next/link"
import { notFound } from "next/navigation"
import { catalog, neighbors } from "@/lib/bible"

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
        {Array.from({ length: meta.capitulos }, (_, i) => (
          <Link
            key={i + 1}
            href={`/livro/${slug}/${i + 1}/`}
            className="flex h-11 items-center justify-center border border-border bg-card text-sm hover:border-primary hover:text-primary"
          >
            {i + 1}
          </Link>
        ))}
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
