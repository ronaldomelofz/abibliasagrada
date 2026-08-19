import { Suspense } from "react"
import { SearchPanel } from "@/components/search-panel"

export const metadata = { title: "Busca" }

export default function SearchPage() {
  return (
    <main>
      <Suspense
        fallback={
          <div className="mx-auto w-full max-w-3xl px-4 py-12 text-sm text-muted-foreground">
            A carregar a busca…
          </div>
        }
      >
        <SearchPanel />
      </Suspense>
    </main>
  )
}
