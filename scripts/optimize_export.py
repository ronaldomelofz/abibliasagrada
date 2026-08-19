# -*- coding: utf-8 -*-
"""Inventário dos PDFs e compactação do JSON publicado (sem republicar CNBB/Jerusalém)."""
from __future__ import annotations

import json
from pathlib import Path

import fitz

ROOT = Path(r"E:\PROJETOS-CURSOR\BIBLIA")
DOCS = ROOT / "documentos"
OCR = ROOT / "_ocr"
WEB = ROOT / "web"
LIVROS = WEB / "data" / "livros"
SEARCH = WEB / "public" / "data" / "search.json"


def inventory() -> None:
    print("=== PDFs ===")
    for f in sorted(DOCS.glob("*.pdf")):
        doc = fitz.open(f)
        sample = doc[min(20, doc.page_count - 1)].get_text()
        print(
            f"{f.name:62} págs={doc.page_count:4} "
            f"camada_texto={len(sample):5} chars"
        )
        doc.close()
    print("\n=== OCR vs PDF (Figueiredo) ===")
    for vol in range(1, 17):
        ocr_p = OCR / f"vol_{vol:02d}.ocr.pages.json"
        pdfs = list(DOCS.glob(f"*-{vol:02d}.pdf")) + list(DOCS.glob(f"*-{vol}.pdf"))
        if not ocr_p.exists() or not pdfs:
            print(f"vol {vol:02d} FALTA")
            continue
        pages = json.loads(ocr_p.read_text(encoding="utf-8"))
        doc = fitz.open(pdfs[0])
        ok = "ok" if len(pages) == doc.page_count else "DIVERGE"
        print(f"vol {vol:02d} OCR={len(pages):4} PDF={doc.page_count:4} {ok}")
        doc.close()


def compact() -> None:
    books_meta = []
    idx = {}
    hits = []
    stripped = 0
    for f in sorted(LIVROS.glob("*.json")):
        b = json.loads(f.read_text(encoding="utf-8"))
        slug = b["id"]
        if slug not in idx:
            idx[slug] = len(books_meta)
            books_meta.append([slug, b["nome"], b["abbrev"]])
        changed = False
        for ch in b.get("capitulos") or []:
            for v in ch.get("versiculos") or []:
                notas = [n for n in (v.get("notas") or []) if (n.get("t") or "").strip()]
                if v.get("notas") == []:
                    del v["notas"]
                    changed = True
                    stripped += 1
                elif v.get("notas") and len(notas) != len(v["notas"]):
                    v["notas"] = notas
                    changed = True
                t = (v.get("t") or "").strip()
                if t:
                    snippet = t if len(t) <= 480 else t[:477] + "…"
                    hits.append([idx[slug], ch["n"], v["n"], snippet, 0])
                for n in notas:
                    nt = (n.get("t") or "").strip()
                    if not nt:
                        continue
                    snippet = nt if len(nt) <= 360 else nt[:357] + "…"
                    hits.append([idx[slug], ch["n"], v["n"], snippet, 1])
        if changed:
            f.write_text(json.dumps(b, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    payload = {"v": 2, "b": books_meta, "h": hits}
    SEARCH.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"\nbusca compacta: {len(books_meta)} livros, {len(hits)} entradas, notas vazias removidas={stripped}")
    print(f"search.json {SEARCH.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    inventory()
    compact()
