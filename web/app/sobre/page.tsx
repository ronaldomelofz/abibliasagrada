import { totals } from "@/lib/bible"

export const metadata = { title: "Sobre" }

export default function AboutPage() {
  const stats = totals()
  return (
    <main className="mx-auto max-w-2xl px-4 py-16 font-reading">
      <p className="font-ui text-[11px] uppercase tracking-[0.28em] text-primary">Colofão</p>
      <h1 className="mt-3 font-display text-4xl tracking-tight">Esta edição</h1>
      <div className="mt-8 space-y-5 text-lg leading-8">
        <p>
          Antônio Pereira de Figueiredo (1725–1797) traduziu a Bíblia a partir da
          Vulgata latina. O Novo Testamento saiu entre 1778 e 1781; o Antigo, entre
          1782 e 1790. A edição em volume único data de 1821. O texto, as notas e o
          dicionário foram lidos página a página com Tesseract 5.5 em português
          (300 dpi) a partir dos PDFs da pasta documentos — edição impressa de 1950
          (Ano Santo), Editora das Américas, São Paulo. A camada de texto antiga do
          PDF era irregular; o OCR reconstitui o impresso.
        </p>
        <p>
          O cânone segue a Igreja Católica Apostólica Romana: {stats.livros} livros,{" "}
          {stats.capitulos} capítulos, {stats.versiculos.toLocaleString("pt-BR")}{" "}
          versículos e {stats.notas.toLocaleString("pt-BR")} notas explicativas. A
          busca consulta só este conjunto: texto sagrado, notas de rodapé e o
          dicionário bíblico (volume 13).
        </p>
        <p>
          Salmos seguem a numeração da Vulgata. Tobias, Judite, Sabedoria,
          Eclesiástico, Baruc, I e II Macabeus, e os acréscimos de Ester e Daniel
          entram no cânone, como no Concílio de Trento. I–IV Reis da edição
          correspondem a I–II Samuel e I–II Reis.
        </p>
        <p>
          A Bíblia de Jerusalém e a tradução da CNBB servem só para
          conferir a ordem católica dos capítulos. O texto publicado, as
          notas de rodapé e o dicionário são exclusivamente da Figueiredo
          (1950). Não republicamos o texto daquelas duas edições: continuam
          protegidas por direitos de autor. O volume 17 (biografias dos papas)
          fica de fora pelo mesmo motivo.
        </p>
        <p>
          A tradução de Figueiredo, do século XVIII, está em domínio público. A
          grafia da edição de 1950 foi conservada no texto bíblico; a navegação do
          site está em português do Brasil. Esta composição digital não substitui
          uma edição crítica nem o juízo da Igreja sobre o texto sagrado.
        </p>
      </div>
    </main>
  )
}
