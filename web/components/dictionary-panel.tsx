"use client"

import { useEffect, useMemo, useState } from "react"
import { Input } from "@/components/ui/input"

type Entry = { lemma: string; t: string }

function fold(s: string) {
  return s.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase()
}

export function DictionaryPanel() {
  const [q, setQ] = useState("")
  const [entries, setEntries] = useState<Entry[]>([])

  useEffect(() => {
    fetch("/data/dicionario.json")
      .then((r) => r.json())
      .then((d) => setEntries(d.verbetes ?? []))
  }, [])

  const shown = useMemo(() => {
    const needle = fold(q.trim())
    if (needle.length < 2) return entries.slice(0, 40)
    return entries.filter((e) => fold(e.lemma).includes(needle) || fold(e.t).includes(needle)).slice(0, 80)
  }, [q, entries])

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-12">
      <p className="text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
        Volume 13 · edição de 1950
      </p>
      <h1 className="mt-2 font-display text-4xl tracking-tight">Dicionário bíblico</h1>
      <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted-foreground">
        Verbetes extraídos do dicionário impresso na mesma coleção da Vulgata Figueiredo.
      </p>
      <Input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder={entries.length ? "Procurar verbete…" : "A carregar…"}
        className="mt-8 h-12 bg-card font-reading text-base"
      />
      <p className="mt-3 text-xs text-muted-foreground">
        {entries.length} verbetes · a mostrar {shown.length}
      </p>
      <ol className="mt-10 space-y-8">
        {shown.map((e) => (
          <li key={e.lemma} id={e.lemma}>
            <h2 className="font-display text-2xl tracking-tight text-primary">{e.lemma}</h2>
            <p className="mt-2 font-reading text-[1.05rem] leading-7">{e.t}</p>
          </li>
        ))}
      </ol>
    </div>
  )
}
