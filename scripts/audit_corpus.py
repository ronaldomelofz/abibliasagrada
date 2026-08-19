# -*- coding: utf-8 -*-
"""Auditoria do corpus Figueiredo: versículos, notas e OCR."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"E:\PROJETOS-CURSOR\BIBLIA")
OCR = ROOT / "_ocr"
WEB = ROOT / "web" / "data" / "livros"

FN = re.compile(r"\(\s*(\d{1,2})\s*\)")
FN_START = re.compile(r"^\(\s*(\d{1,2})\s*\)")
ALT_START = re.compile(r"^(\d{1,2})\s*[\)\].\-–—]\s+\S")


def main() -> None:
    print("=== OCR Tesseract (já existente) ===")
    ocr_pages = ocr_note_lines = pages_no_notes = 0
    ocr_fn_marks = 0
    for f in sorted(OCR.glob("vol_*.ocr.pages.json")):
        pages = json.loads(f.read_text(encoding="utf-8"))
        with_notes = sum(1 for p in pages if p.get("notes"))
        n_lines = sum(len(p.get("notes") or []) for p in pages)
        marks = 0
        for p in pages:
            for ln in p.get("notes") or []:
                if FN_START.match(ln) or ALT_START.match(ln):
                    marks += 1
        print(
            f"{f.name}: páginas={len(pages):4} com_notas={with_notes:4} "
            f"linhas_nota={n_lines:5} marcas={marks:4}"
        )
        ocr_pages += len(pages)
        ocr_note_lines += n_lines
        pages_no_notes += len(pages) - with_notes
        ocr_fn_marks += marks
    print(
        f"TOTAL OCR páginas={ocr_pages} linhas_de_nota={ocr_note_lines} "
        f"páginas_sem_bloco_nota={pages_no_notes} marcas_início={ocr_fn_marks}"
    )

    print("\n=== JSON publicado (web/data/livros) ===")
    empty_v = []
    short_v = []
    gaps = []
    empty_note = 0
    total_v = total_n = 0
    chapters_no_notes = []
    markers_without_note = []
    per_book = []

    for f in sorted(WEB.glob("*.json")):
        b = json.loads(f.read_text(encoding="utf-8"))
        slug = b.get("id") or f.stem
        bv = bn = 0
        for ch in b.get("capitulos") or []:
            vs = ch.get("versiculos") or []
            nums = [v["n"] for v in vs]
            ncount = 0
            if vs and nums[0] != 1:
                gaps.append((slug, ch["n"], f"começa no v.{nums[0]}"))
            if nums:
                missing = [x for x in range(nums[0], nums[-1] + 1) if x not in nums]
                if missing:
                    gaps.append((slug, ch["n"], f"faltam {missing[:15]}"))
            for v in vs:
                total_v += 1
                bv += 1
                t = (v.get("t") or "").strip()
                if not t:
                    empty_v.append((slug, ch["n"], v["n"]))
                elif len(t) < 12:
                    short_v.append((slug, ch["n"], v["n"], t))
                notas = v.get("notas") or []
                ncount += len(notas)
                total_n += len(notas)
                bn += len(notas)
                for n in notas:
                    if not (n.get("t") or "").strip():
                        empty_note += 1
                refs = [int(x) for x in FN.findall(t)]
                have = {n["n"] for n in notas if n.get("t")}
                for r in refs:
                    if r not in have:
                        markers_without_note.append((slug, ch["n"], v["n"], r))
            if vs and ncount == 0:
                chapters_no_notes.append(f"{slug} {ch['n']}")
        per_book.append((slug, bv, bn))

    print(f"versículos={total_v} notas={total_n} notas_vazias={empty_note}")
    print(f"versículos vazios={len(empty_v)} curtos(<12)={len(short_v)} falhas_numeração={len(gaps)}")
    print(f"capítulos sem nenhuma nota={len(chapters_no_notes)}")
    print(f"marcadores (n) no texto sem nota ligada={len(markers_without_note)}")

    print("\n-- falhas de numeração --")
    for g in gaps[:50]:
        print(" ", g)
    if len(gaps) > 50:
        print(f"  … +{len(gaps) - 50}")

    print("\n-- versículos curtos --")
    for s in short_v[:30]:
        print(" ", s)

    print("\n-- (n) sem texto de nota (amostra) --")
    by = defaultdict(int)
    for slug, c, v, n in markers_without_note:
        by[slug] += 1
    for slug, n in sorted(by.items(), key=lambda x: -x[1])[:20]:
        print(f"  {slug}: {n}")
    for m in markers_without_note[:15]:
        print(" ", m)

    print("\n-- livros com menos notas por versículo --")
    ratio = [(s, v, n, (n / v if v else 0)) for s, v, n in per_book]
    for s, v, n, r in sorted(ratio, key=lambda x: x[3])[:15]:
        print(f"  {s:22} v={v:4} notas={n:4}  {r:.2f} nota/verso")


if __name__ == "__main__":
    main()
