import type { Metadata } from "next"
import { Fraunces, Newsreader, Barlow_Condensed } from "next/font/google"
import { TooltipProvider } from "@/components/ui/tooltip"
import { SiteHeader } from "@/components/site-header"
import { ThemeScript } from "@/components/theme-script"
import "./globals.css"

const display = Fraunces({
  variable: "--font-display",
  subsets: ["latin", "latin-ext"],
})

const reading = Newsreader({
  variable: "--font-reading",
  subsets: ["latin", "latin-ext"],
  style: ["normal", "italic"],
})

const ui = Barlow_Condensed({
  variable: "--font-ui",
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "600"],
})

export const metadata: Metadata = {
  title: {
    default: "Bíblia Sagrada — Figueiredo",
    template: "%s — Bíblia Figueiredo",
  },
  description:
    "Leitura integral da Bíblia Sagrada na tradução de Antônio Pereira de Figueiredo, a partir da Vulgata latina. Cânone católico, 73 livros.",
}

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="pt-BR"
      suppressHydrationWarning
      className={`${display.variable} ${reading.variable} ${ui.variable} h-full`}
    >
      <body className="min-h-full flex flex-col font-ui antialiased">
        <ThemeScript />
        <TooltipProvider>
          <SiteHeader />
          <div className="flex-1">{children}</div>
          <footer className="border-t border-border/80 py-8 text-center text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
            Figueiredo · Vulgata latina · domínio público
          </footer>
        </TooltipProvider>
      </body>
    </html>
  )
}
