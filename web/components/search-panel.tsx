"use client"

import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { useEffect, useState } from "react"
import { Input } from "@/components/ui/input"
import {
  interpretQuery,
  textMatches,
  type BibleRef,
  type RefBook,
} from "@/lib/bible-ref"

type Hit = {
  b: string
  n: string
  a: string
  c: number
  v: number
  t: string
  k?: "verso" | "nota" | "dicionario"
}

let cache: Hit[] | null = null

async function loadIndex() {
  if (cache) return cache
  const res = await fetch("/data/search.json")
  cache = (await res.json()) as Hit[]
  return cache
}

const KIND: Record<string, string> = {
  verso: "Texto",
  nota: "Nota",
  dicionario: "Dicionário",
}

function hitsForRef(ref: BibleRef): Hit[] {
  if (!cache) return []
  const ids = new Set(ref.books.map((b) => b.id))
  const out = cache.filter((h) => {
    if (!ids.has(h.b) || h.c !== ref.chapter || h.k === "dicionario") return false
    if (ref.verse != null) return h.v === ref.verse
    return h.k === "verso" || h.k == null
  })
  out.sort((a, b) => {
    const ia = ref.books.findIndex((bk) => bk.id === a.b)
    const ib = ref.books.findIndex((bk) => bk.id === b.b)
    if (ia !== ib) return ia - ib
    if (a.v !== b.v) return a.v - b.v
    return (a.k === "nota" ? 1 : 0) - (b.k === "nota" ? 1 : 0)
  })
  return out
}

function groupHits(hits: Hit[]) {
  const order: string[] = []
  const map = new Map<string, Hit[]>()
  for (const h of hits) {
    if (!map.has(h.b)) {
      order.push(h.b)
      map.set(h.b, [])
    }
    map.get(h.b)!.push(h)
  }
  return order.map((id) => ({ id, nome: map.get(id)![0].n, items: map.get(id)! }))
}

export function SearchPanel() {
  const params = useSearchParams()
  const fromUrl = params.get("q") ?? ""
  const [q, setQ] = useState(fromUrl)
  const [ready, setReady] = useState(false)
  const [hits, setHits] = useState<Hit[]>([])
  const [ref, setRef] = useState<BibleRef | null>(null)
  const [books, setBooks] = useState<RefBook[]>([])
  const [miss, setMiss] = useState<string | null>(null)

  useEffect(() => {
    loadIndex().then(() => setReady(true))
  }, [])

  useEffect(() => {
    if (!ready) return
    if (fromUrl) run(fromUrl)
  }, [ready, fromUrl])

  function hrefFor(h: Hit) {
    if (h.k === "dicionario" || h.b === "dicionario") return "/dicionario/"
    return `/livro/${h.b}/${h.c}/#v${h.v}`
  }

  function run(value: string) {
    setQ(value)
    if (!cache) {
      setHits([])
      setRef(null)
      setBooks([])
      setMiss(null)
      return
    }
    const intent = interpretQuery(value)
    if (intent.type === "empty") {
      setHits([])
      setRef(null)
      setBooks([])
      setMiss(null)
      return
    }
    if (intent.type === "ref") {
      setRef(intent.ref)
      setBooks(intent.ref.books)
      setHits(hitsForRef(intent.ref))
      setMiss(null)
      return
    }
    if (intent.type === "unknown-ref") {
      setRef(null)
      setBooks([])
      setHits([])
      const v = intent.verse != null ? `,${intent.verse}` : ""
      setMiss(`Não há «${intent.bookHint} ${intent.chapter}${v}» no cânone desta edição.`)
      return
    }
    if (intent.type === "books") {
      setRef(null)
      setBooks(intent.books)
      setHits([])
      setMiss(null)
      return
    }
    setRef(null)
    setBooks([])
    setMiss(null)
    const out: Hit[] = []
    for (const h of cache) {
      if (textMatches(h.t, intent.needle)) {
        out.push(h)
        if (out.length >= 80) break
      }
    }
    setHits(out)
  }

  const groups = ref && ref.books.length > 1 ? groupHits(hits) : null

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-12">
      <p className="text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
        Só nos documentos Figueiredo
      </p>
      <h1 className="mt-2 font-display text-4xl tracking-tight">Busca</h1>
      <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted-foreground">
        Livro (ou parte do nome), depois o capítulo. O versículo só entra depois
        da vírgula: Macabeus 1 ou Macabeus 1,1.
      </p>
      <Input
        value={q}
        onChange={(e) => run(e.target.value)}
        placeholder={ready ? "Ex.: Macabeus 1  ou  Macabeus 1,1" : "Carregando o índice..."}
        name="q"
        className="mt-8 h-12 bg-card font-reading text-base"
        autoFocus
      />
      <p className="mt-3 text-xs text-muted-foreground">
        {!q.trim()
          ? "Comece pelo nome do livro, ou por parte dele."
          : miss
            ? miss
            : ref
              ? `${hits.length} ${ref.verse != null ? "ocorrência" : "versículo"}${hits.length === 1 ? "" : "s"}`
              : books.length
                ? `${books.length} livro${books.length === 1 ? "" : "s"} — acrescente o capítulo, por exemplo ${books[0].nome.replace(/^I+ /, "")} 1.`
                : `${hits.length} ocorrência${hits.length === 1 ? "" : "s"}`}
      </p>
      {!ref && books.length > 0 ? (
        <ul className="mt-6 divide-y divide-border border-y border-border">
          {books.map((b) => (
            <li key={b.id}>
              <Link href={`/livro/${b.id}/`} className="group flex items-baseline justify-between gap-4 py-3">
                <span className="font-display text-xl tracking-tight group-hover:text-primary">{b.nome}</span>
                <span className="shrink-0 text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
                  {b.abbrev} · {b.capitulos} cap.
                </span>
              </Link>
            </li>
          ))}
        </ul>
      ) : null}
      {ref && ref.books.length > 0 ? (
        <p className="mt-2 text-sm">
          {ref.books.map((b, i) => (
            <span key={b.id}>
              {i > 0 ? " · " : null}
              <Link
                href={
                  ref.verse != null
                    ? `/livro/${b.id}/${ref.chapter}/#v${ref.verse}`
                    : `/livro/${b.id}/${ref.chapter}/`
                }
                className="text-primary underline-offset-4 hover:underline"
              >
                Abrir {b.nome} {ref.chapter}
                {ref.verse != null ? `,${ref.verse}` : ""}
              </Link>
            </span>
          ))}
        </p>
      ) : null}
      {groups ? (
        <div className="mt-8 space-y-10">
          {groups.map((g) => (
            <section key={g.id}>
              <h2 className="font-display text-2xl tracking-tight">
                {g.nome} {ref!.chapter}
                {ref!.verse != null ? `,${ref!.verse}` : ""}
              </h2>
              <ol className="mt-4 space-y-5">
                {g.items.map((h, i) => (
                  <HitItem key={`${h.k}-${h.b}-${h.c}-${h.v}-${i}`} h={h} href={hrefFor(h)} />
                ))}
              </ol>
            </section>
          ))}
        </div>
      ) : (
        <ol className="mt-8 space-y-5">
          {hits.map((h, i) => (
            <HitItem key={`${h.k}-${h.b}-${h.c}-${h.v}-${i}`} h={h} href={hrefFor(h)} />
          ))}
        </ol>
      )}
    </div>
  )
}

function HitItem({ h, href }: { h: Hit; href: string }) {
  return (
    <li>
      <Link href={href} className="group block">
        <p className="text-[11px] uppercase tracking-[0.2em] text-primary">
          {KIND[h.k || "verso"]} · {h.n}
          {h.c ? ` ${h.c},${h.v}` : ""}
        </p>
        <p className="mt-1 font-reading text-[1.05rem] leading-7 group-hover:text-primary">
          {h.t.length > 420 ? `${h.t.slice(0, 420)}…` : h.t}
        </p>
      </Link>
    </li>
  )
}
