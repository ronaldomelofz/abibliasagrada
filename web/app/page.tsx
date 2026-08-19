import Link from "next/link"
import { SearchBar } from "@/components/search-bar"
import { getBook, GROUPS, catalog, totals } from "@/lib/bible"

export default function HomePage() {
  const stats = totals()
  const genesis = getBook("genesis")
  const opening = genesis.capitulos[0]?.versiculos.slice(0, 3) ?? []

  return (
    <main>
      <section className="border-b border-border">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 py-16 sm:px-6 lg:grid-cols-[1.15fr_0.85fr] lg:py-24">
          <div>
            <p className="text-[11px] uppercase tracking-[0.32em] text-primary">
              Tradução da Vulgata · 1781 / 1950
            </p>
            <h1 className="mt-4 font-display text-[2.8rem] leading-[0.95] tracking-tight sm:text-6xl">
              Bíblia
              <span className="block italic text-primary">Sagrada</span>
            </h1>
            <p className="mt-6 max-w-md font-reading text-lg leading-8 text-muted-foreground">
              Texto integral em português, na tradução de Antônio Pereira de
              Figueiredo, oratoriano, natural de Mação, feita a partir da
              Vulgata latina. Cânone católico: setenta e três livros.
            </p>
            <div className="mt-8 flex flex-wrap gap-x-8 gap-y-2 text-[12px] uppercase tracking-[0.18em] text-muted-foreground">
              <span>{stats.livros} livros</span>
              <span>{stats.capitulos} capítulos</span>
              <span>{stats.versiculos.toLocaleString("pt-BR")} versículos</span>
              <span>{stats.notas.toLocaleString("pt-BR")} notas</span>
            </div>
            <SearchBar size="hero" className="mt-8 max-w-xl" />
            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                href="/livro/genesis/1/"
                className="inline-flex h-10 items-center bg-primary px-5 text-[12px] uppercase tracking-[0.18em] text-primary-foreground"
              >
                Abrir o Gênesis
              </Link>
              <Link
                href="/livro/mateus/1/"
                className="inline-flex h-10 items-center border border-border px-5 text-[12px] uppercase tracking-[0.18em] hover:bg-muted"
              >
                Evangelho de Mateus
              </Link>
            </div>
          </div>
          <aside className="self-end border-l-2 border-primary/70 pl-6">
            <p className="text-[11px] uppercase tracking-[0.24em] text-muted-foreground">
              Gênesis 1
            </p>
            <div className="mt-4 font-reading text-[1.05rem] leading-8">
              {opening.map((v) => (
                <p key={v.n} className="mb-4">
                  <sup className="mr-1 text-[0.7em] text-primary">{v.n}</sup>
                  {v.t}
                </p>
              ))}
            </div>
            <Link href="/livro/genesis/1/" className="text-[12px] uppercase tracking-[0.18em] text-primary">
              Continuar a leitura
            </Link>
          </aside>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        {["at", "nt"].map((test) => (
          <div key={test} className="mb-16">
            <h2 className="font-display text-3xl tracking-tight">
              {test === "at" ? "Antigo Testamento" : "Novo Testamento"}
            </h2>
            <div className="mt-8 grid gap-10 md:grid-cols-2">
              {GROUPS.filter((g) => g.testamento === test).map((group) => (
                <div key={group.id}>
                  <h3 className="mb-3 text-[11px] uppercase tracking-[0.22em] text-primary">
                    {group.titulo}
                  </h3>
                  <ol className="divide-y divide-border/70 border-y border-border/70">
                    {group.ids.map((id) => {
                      const b = catalog.livros.find((x) => x.id === id)
                      if (!b) return null
                      return (
                        <li key={id}>
                          <Link
                            href={`/livro/${id}/1/`}
                            className="flex items-baseline justify-between gap-3 py-2.5 hover:text-primary"
                          >
                            <span className="font-reading text-[1.05rem]">{b.nome}</span>
                            <span className="shrink-0 font-ui text-[11px] uppercase tracking-[0.16em] text-muted-foreground">
                              {b.abbrev} · {b.capitulos} cap.
                            </span>
                          </Link>
                        </li>
                      )
                    })}
                  </ol>
                </div>
              ))}
            </div>
          </div>
        ))}
      </section>
    </main>
  )
}
