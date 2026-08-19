# Bíblia Sagrada — Figueiredo

Leitura integral da [Bíblia Sagrada](https://abibliasagrada.netlify.app/) na tradução de António Pereira de Figueiredo (Vulgata latina, cânone católico, 73 livros).

Site: **https://abibliasagrada.netlify.app**  
Publicação: Netlify, a partir deste repositório.

## O que entra no GitHub

Código do site (`web/`), JSON extraído (`web/data`, `web/public/data`) e os scripts de extração. Ficam de fora — de propósito, para o repositório permanecer leve:

- PDFs da pasta `documentos/`
- OCR (`_ocr/`) e caches (`_extract/`, `.venv-ocr/`)
- `node_modules/` e o export estático `web/out/`

A Netlify volta a gerar o site em cada `git push` (`pnpm build` em `web/`).

## Desenvolvimento

```bash
cd web
pnpm install
pnpm dev
```

Abrir [http://localhost:3000](http://localhost:3000).

## Publicar

Alterações em `main` disparam o deploy em [abibliasagrada.netlify.app](https://abibliasagrada.netlify.app/).

## Extração (opcional, local)

Os 16 volumes da Figueiredo (1950) leem-se com Tesseract e `scripts/extract_and_parse.py`. Só é necessário se os PDFs OCR mudarem; o texto já extraído está em `web/data/`.
