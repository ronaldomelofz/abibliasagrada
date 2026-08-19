import { Search } from "lucide-react"
import { cn } from "@/lib/utils"

type Props = {
  size?: "header" | "hero"
  defaultValue?: string
  className?: string
}

export function SearchBar({ size = "header", defaultValue = "", className }: Props) {
  const hero = size === "hero"
  return (
    <form
      action="/busca/"
      method="get"
      role="search"
      className={cn(
        "flex min-w-0 items-center border border-border bg-card",
        hero ? "h-12" : "h-9",
        className
      )}
    >
      <label htmlFor={hero ? "busca-hero" : "busca-header"} className="sr-only">
        Buscar na Bíblia
      </label>
      <Search
        className={cn("ml-3 shrink-0 text-muted-foreground", hero ? "size-5" : "size-4")}
        aria-hidden
      />
      <input
        id={hero ? "busca-hero" : "busca-header"}
        name="q"
        type="search"
        defaultValue={defaultValue}
        placeholder={hero ? "Mateus 5  ou  Mateus 5,1" : "Mateus 5,1"}
        autoComplete="off"
        className={cn(
          "min-w-0 flex-1 bg-transparent px-2.5 outline-none placeholder:text-muted-foreground",
          hero ? "h-12 font-reading text-base" : "h-9 text-[13px]"
        )}
      />
      <button
        type="submit"
        className={cn(
          "shrink-0 uppercase tracking-[0.16em] text-primary hover:bg-muted",
          hero ? "h-12 px-5 text-[12px]" : "h-9 px-3 text-[11px]"
        )}
      >
        Buscar
      </button>
    </form>
  )
}
