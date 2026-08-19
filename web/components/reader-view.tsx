"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useEffect, useMemo, useState } from "react"
import { ChevronLeft, ChevronRight, Minus, Plus, Type } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { Book, Note } from "@/lib/bible"
import { cn } from "@/lib/utils"

const SIZES = [1, 1.08, 1.18, 1.3, 1.45]

export function ReaderView({
  book,
  chapter,
  prevHref,
  nextHref,
}: {
  book: Book
  chapter: number
  prevHref: string | null
  nextHref: string | null
}) {
  const router = useRouter()
  const [size, setSize] = useState(1)
  const [openNote, setOpenNote] = useState<number | null>(null)
  const ch = book.capitulos.find((c) => c.n === chapter)
  const verses = ch?.versiculos ?? []

  const notes = useMemo(() => {
    const map = new Map<number, Note>()
    for (const v of verses) {
      for (const n of v.notas ?? []) {
        if (!map.has(n.n) && n.t) map.set(n.n, n)
      }
    }
    return [...map.values()].sort((a, b) => a.n - b.n)
  }, [verses])

  useEffect(() => {
    const stored = Number(localStorage.getItem("biblia:size") || "1")
    if (stored >= 0 && stored < SIZES.length) setSize(stored)
    localStorage.setItem("biblia:last", `/livro/${book.id}/${chapter}/`)
    setOpenNote(null)
  }, [book.id, chapter])

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return
      if ((e.key === "ArrowRight" || e.key === "j") && nextHref) router.push(nextHref)
      if ((e.key === "ArrowLeft" || e.key === "k") && prevHref) router.push(prevHref)
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [nextHref, prevHref, router])

  const title = useMemo(() => ch?.titulo?.replace(/\s+/g, " ").trim() ?? "", [ch])

  function bump(delta: number) {
    setSize((s) => {
      const n = Math.min(SIZES.length - 1, Math.max(0, s + delta))
      localStorage.setItem("biblia:size", String(n))
      return n
    })
  }

  return (
    <article className="mx-auto w-full max-w-[42rem] px-4 pb-24 pt-10 sm:px-6">
      <header className="mb-10 border-b border-border pb-8">
        <p className="text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
          {book.testamento === "at" ? "Antigo Testamento" : "Novo Testamento"} · {book.abbrev}
        </p>
        <div className="mt-3 flex items-end justify-between gap-4">
          <div>
            <h1 className="font-display text-4xl leading-none tracking-tight sm:text-5xl">
              {book.nome}
            </h1>
            <p className="mt-3 font-display text-xl italic text-primary">Capítulo {chapter}</p>
          </div>
          <div className="flex items-center gap-1 text-muted-foreground">
            <Type className="size-3.5" />
            <Button variant="ghost" size="icon-xs" onClick={() => bump(-1)} aria-label="Diminuir texto">
              <Minus />
            </Button>
            <Button variant="ghost" size="icon-xs" onClick={() => bump(1)} aria-label="Aumentar texto">
              <Plus />
            </Button>
          </div>
        </div>
        {title ? (
          <p className="mt-4 max-w-xl text-sm leading-relaxed text-muted-foreground">{title}</p>
        ) : null}
      </header>

      {verses.length === 0 ? (
        <p className="font-reading text-lg leading-8 text-muted-foreground">
          Este capítulo ainda não foi reconstruído com clareza a partir do original impresso.
          Avance para o próximo.
        </p>
      ) : (
        <div
          className="font-reading text-foreground"
          style={{ fontSize: `${SIZES[size]}rem`, lineHeight: 1.72 }}
        >
          {verses.map((v, i) => (
            <p
              key={v.n}
              id={`v${v.n}`}
              className={cn("mb-[0.7em]", i === 0 && v.n === 1 && "drop-cap")}
            >
              <sup className="mr-1.5 select-none align-super text-[0.68em] font-ui tracking-wide text-primary">
                {v.n}
              </sup>
              {v.t}
              {(v.notas ?? []).map((n) => (
                <button
                  key={n.n}
                  type="button"
                  onClick={() => {
                    setOpenNote(n.n)
                    document.getElementById(`nota-${n.n}`)?.scrollIntoView({ behavior: "smooth", block: "nearest" })
                  }}
                  className="ml-0.5 align-super font-ui text-[0.65em] text-primary hover:underline"
                  aria-label={`Nota ${n.n}`}
                >
                  [{n.n}]
                </button>
              ))}
            </p>
          ))}
        </div>
      )}

      {notes.length > 0 ? (
        <section className="mt-12 border-t border-border pt-8">
          <h2 className="text-[11px] uppercase tracking-[0.28em] text-primary">
            Notas explicativas · {notes.length}
          </h2>
          <ol className="mt-5 space-y-5">
            {notes.map((n) => (
              <li
                key={n.n}
                id={`nota-${n.n}`}
                className={cn(
                  "font-reading text-[0.95rem] leading-7 text-muted-foreground",
                  openNote === n.n && "text-foreground"
                )}
              >
                <span className="mr-2 font-ui text-[11px] uppercase tracking-[0.16em] text-primary">
                  {n.n}
                </span>
                {n.t}
              </li>
            ))}
          </ol>
        </section>
      ) : null}

      <nav className="mt-14 flex items-center justify-between gap-3 border-t border-border pt-6 text-[13px] uppercase tracking-[0.16em]">
        {prevHref ? (
          <Link href={prevHref} className="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground">
            <ChevronLeft className="size-4" /> Anterior
          </Link>
        ) : (
          <span />
        )}
        <Link href={`/livro/${book.id}/`} className="text-muted-foreground hover:text-foreground">
          Sumário
        </Link>
        {nextHref ? (
          <Link href={nextHref} className="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground">
            Seguinte <ChevronRight className="size-4" />
          </Link>
        ) : (
          <span />
        )}
      </nav>
    </article>
  )
}
