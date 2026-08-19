import Link from "next/link"

export default function NotFound() {
  return (
    <main className="mx-auto max-w-xl px-4 py-24 text-center">
      <p className="text-[11px] uppercase tracking-[0.28em] text-primary">404</p>
      <h1 className="mt-3 font-display text-4xl">Página não encontrada</h1>
      <p className="mt-4 font-reading text-muted-foreground">
        Esse livro ou capítulo não existe neste cânone.
      </p>
      <Link href="/" className="mt-8 inline-block text-[12px] uppercase tracking-[0.18em] text-primary">
        Voltar ao índice
      </Link>
    </main>
  )
}
