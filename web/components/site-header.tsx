"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Menu, Moon, Sun } from "lucide-react"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { SearchBar } from "@/components/search-bar"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { catalog } from "@/lib/catalog"
import { cn } from "@/lib/utils"

const links = [
  { href: "/", label: "Livros" },
  { href: "/busca/", label: "Busca" },
  { href: "/dicionario/", label: "Dicionário" },
  { href: "/sobre/", label: "Sobre" },
]

export function SiteHeader() {
  const path = usePathname()
  const [dark, setDark] = useState(false)
  const [last, setLast] = useState<string | null>(null)

  useEffect(() => {
    setDark(document.documentElement.classList.contains("dark"))
    setLast(localStorage.getItem("biblia:last"))
  }, [path])

  function toggleTheme() {
    const next = !document.documentElement.classList.contains("dark")
    document.documentElement.classList.toggle("dark", next)
    localStorage.setItem("biblia:theme", next ? "dark" : "light")
    setDark(next)
  }

  return (
    <header className="sticky top-0 z-40 border-b border-border/80 bg-background/85 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-3 px-4">
        <Link href="/" className="flex min-w-0 items-baseline gap-2">
          <span className="font-display text-[1.35rem] leading-none tracking-tight">
            Bíblia
          </span>
          <span className="hidden truncate text-[11px] uppercase tracking-[0.22em] text-muted-foreground sm:inline">
            Figueiredo · 73 livros
          </span>
        </Link>
        <SearchBar className="mx-1 min-w-0 flex-1 sm:mx-4 sm:max-w-md" />
        <nav className="ml-auto hidden items-center gap-1 sm:flex">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={cn(
                "px-3 py-1.5 text-[13px] uppercase tracking-[0.16em] transition-colors",
                path === l.href || (l.href !== "/" && path.startsWith(l.href))
                  ? "text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {l.label}
            </Link>
          ))}
          {last ? (
            <Link
              href={last}
              className="px-3 py-1.5 text-[13px] uppercase tracking-[0.16em] text-muted-foreground hover:text-foreground"
            >
              Continuar
            </Link>
          ) : null}
          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Alternar tema">
            {dark ? <Sun /> : <Moon />}
          </Button>
        </nav>
        <div className="flex items-center gap-1 sm:hidden">
          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Tema">
            {dark ? <Sun /> : <Moon />}
          </Button>
          <Sheet>
            <SheetTrigger render={<Button variant="ghost" size="icon" aria-label="Menu" />}>
              <Menu />
            </SheetTrigger>
            <SheetContent side="right" className="w-72">
              <SheetHeader>
                <SheetTitle className="font-display">Navegar</SheetTitle>
              </SheetHeader>
              <div className="mt-4 flex flex-col gap-1 px-2">
                {links.map((l) => (
                  <Link key={l.href} href={l.href} className="rounded-md px-3 py-2 text-sm hover:bg-muted">
                    {l.label}
                  </Link>
                ))}
                <p className="mt-4 px-3 text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
                  Antigo Testamento
                </p>
                {catalog.livros
                  .filter((b) => b.testamento === "at")
                  .slice(0, 12)
                  .map((b) => (
                    <Link
                      key={b.id}
                      href={`/livro/${b.id}/1/`}
                      className="rounded-md px-3 py-1.5 text-sm hover:bg-muted"
                    >
                      {b.nome}
                    </Link>
                  ))}
                <Link href="/" className="px-3 py-2 text-sm text-primary">
                  Ver todos os livros
                </Link>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}
