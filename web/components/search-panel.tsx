"use client"

import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { useEffect, useState } from "react"
import { Input } from "@/components/ui/input"
import { fold, parseBibleRef, type BibleRef } from "@/lib/bible-ref"

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
    if (a.b !== b.b) return a.b.localeCompare(b.b)
    if (a.v !== b.v) return a.v - b.v
    const ak = a.k === "nota" ? 1 : 0
    const bk = b.k === "nota" ? 1 : 0
    return ak - bk
  })
  return out
}

export function SearchPanel() {
  const params = useSearchParams()
  const fromUrl = params.get("q") ?? ""
  const [q, setQ] = useState(fromUrl)
  const [ready, setReady] = useState(false)
  const [hits, setHits] = useState<Hit[]>([])
  const [ref, setRef] = useState<BibleRef | null>(null)

  useEffect(() => {
    loadIndex().then(() => setReady(true))
  }, [])

  useEffect(() => {
    if (!ready) return
    if (fromUrl) run(fromUrl)
  }, [ready, fromUrl])

  function hrefFor(h: Hit) {
    if (h.k === "dicionario" || h.b === "dicionario") return "/dicionario/"
    const hash = `#v${h.v}`
    return `/livro/${h.b}/${h.c}/${hash}`
  }

  function run(value: string) {
    setQ(value)
    if (!cache) {
      setHits([])
      setRef(null)
      return
    }
    const parsed = parseBibleRef(value)
    if (parsed) {
      setRef(parsed)
      setHits(hitsForRef(parsed))
      return
    }
    setRef(null)
    const needle = fold(value)
    if (needle.length < 3) {
      setHits([])
      return
    }
    const out: Hit[] = []
    for (const h of cache) {
      if (fold(h.t).includes(needle)) {
        out.push(h)
        if (out.length >= 80) break
      }
    }
    setHits(out)
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-12">
      <p className="text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
        Só nos documentos Figueiredo
      </p>
      <h1 className="mt-2 font-display text-4xl tracking-tight">Busca</h1>
      <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted-foreground">
        Procura no texto sagrado, nas notas da edição de 1950 e no dicionário
        bíblico. Referência: livro e capítulo (Mateus 5); o versículo aparece
        depois da vírgula (Mateus 5,1).
      </p>
      <Input
        value={q}
        onChange={(e) => run(e.target.value)}
        placeholder={ready ? "Ex.: Mateus 5  ou  Mateus 5,1" : "A carregar o índice..."}
        name="q"
        className="mt-8 h-12 bg-card font-reading text-base"
        autoFocus
      />
      <p className="mt-3 text-xs text-muted-foreground">
        {!q.trim()
          ? "Comece pelo nome do livro, depois o capítulo."
          : ref
            ? `${hits.length} ${ref.verse != null ? "ocorrência" : "versículo"}${hits.length === 1 ? "" : "s"}`
            : fold(q).length < 3
              ? "Escreva pelo menos três letras, ou uma referência (Mateus 5)."
              : `${hits.length} ocorrências`}
      </p>
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
      <ol className="mt-8 space-y-5">
        {hits.map((h, i) => (
          <li key={`${h.k}-${h.b}-${h.c}-${h.v}-${i}`}>
            <Link href={hrefFor(h)} className="group block">
              <p className="text-[11px] uppercase tracking-[0.2em] text-primary">
                {KIND[h.k || "verso"]} · {h.n}
                {h.c ? ` ${h.c},${h.v}` : ""}
              </p>
              <p className="mt-1 font-reading text-[1.05rem] leading-7 group-hover:text-primary">
                {h.t.length > 420 ? `${h.t.slice(0, 420)}…` : h.t}
              </p>
            </Link>
          </li>
        ))}
      </ol>
    </div>
  )
}
