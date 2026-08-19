"use client"

import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { useEffect, useState } from "react"
import { Input } from "@/components/ui/input"

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

function fold(s: string) {
  return s
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .toLowerCase()
}

const KIND: Record<string, string> = {
  verso: "Texto",
  nota: "Nota",
  dicionario: "Dicionário",
}

export function SearchPanel() {
  const params = useSearchParams()
  const fromUrl = params.get("q") ?? ""
  const [q, setQ] = useState(fromUrl)
  const [ready, setReady] = useState(false)
  const [hits, setHits] = useState<Hit[]>([])

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
    const needle = fold(value.trim())
    if (needle.length < 3 || !cache) {
      setHits([])
      return
    }
    const ref = needle.match(/^([a-z0-9]{1,6})\s+(\d{1,3})(?:,\s*|\s+|:)(\d{1,3})$/)
    if (ref) {
      const [, ab, c, v] = ref
      setHits(
        cache
          .filter(
            (h) =>
              fold(h.a) === ab && h.c === Number(c) && h.v === Number(v) && h.k !== "dicionario"
          )
          .slice(0, 40)
      )
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
        Procura no texto sagrado, nas notas explicativas da edição de 1950 e no
        dicionário bíblico (volume 13). Referência: Gn 1,1.
      </p>
      <Input
        value={q}
        onChange={(e) => run(e.target.value)}
        placeholder={ready ? "Ex.: firmamento, ou Jo 1,1" : "A carregar o índice..."}
        name="q"
        className="mt-8 h-12 bg-card font-reading text-base"
        autoFocus
      />
      <p className="mt-3 text-xs text-muted-foreground">
        {q.trim().length < 3 ? "Escreva pelo menos três letras." : `${hits.length} ocorrências`}
      </p>
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
