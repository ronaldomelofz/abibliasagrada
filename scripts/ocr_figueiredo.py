# -*- coding: utf-8 -*-
"""OCR lento e completo da Figueiredo com Tesseract 5 (português).

Este PC não tem GPU: Marker 2 balanced / MinerU VLM / olmOCR
exigem NVIDIA. Tesseract 5.5 + tessdata `por` é o motor fiável em CPU.

Gera `_ocr/vol_XX.ocr.pages.json` no mesmo formato do extrator PyMuPDF,
página a página, com retoma se o processo for interrompido.
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import fitz
import pytesseract
from PIL import Image

ROOT = Path(r"E:\PROJETOS-CURSOR\BIBLIA")
DOCS = ROOT / "documentos"
OCR_DIR = ROOT / "_ocr"
EXTRACT = ROOT / "_extract"
DPI = 300
WORKERS = 3
LANG = "por"
TESS_CFG = "--oem 1 --psm 4"


def find_pdfs() -> dict[int, Path]:
    mapping = {}
    for f in DOCS.glob("*.pdf"):
        import re
        m = re.search(r"figueiredo-(\d+)", f.name)
        if m:
            mapping[int(m.group(1))] = f
    return mapping


def render_gray(page) -> Image.Image:
    zoom = DPI / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
    return Image.frombytes("L", [pix.width, pix.height], pix.samples)


def tesseract_lines(img: Image.Image) -> list[dict]:
    data = pytesseract.image_to_data(
        img, lang=LANG, config=TESS_CFG, output_type=pytesseract.Output.DICT
    )
    grouped: dict[tuple, dict] = {}
    n = len(data["text"])
    for i in range(n):
        txt = (data["text"][i] or "").strip()
        if not txt:
            continue
        try:
            conf = float(data["conf"][i])
        except (TypeError, ValueError):
            conf = 0.0
        if conf < 15:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        rec = grouped.setdefault(
            key,
            {"y": data["top"][i], "x": data["left"][i], "hs": [], "parts": []},
        )
        rec["x"] = min(rec["x"], data["left"][i])
        rec["y"] = min(rec["y"], data["top"][i])
        rec["hs"].append(float(data["height"][i]))
        rec["parts"].append((data["left"][i], txt))
    lines = []
    for rec in grouped.values():
        rec["parts"].sort()
        text = " ".join(t for _, t in rec["parts"])
        text = " ".join(text.split())
        if not text:
            continue
        sz = statistics.median(rec["hs"]) if rec["hs"] else 12.0
        lines.append({"y": float(rec["y"]), "x": float(rec["x"]), "sz": float(sz), "t": text})
    lines.sort(key=lambda l: (l["y"], l["x"]))
    return lines


def split_body_notes(lines: list[dict]) -> tuple[list[str], list[str]]:
    if not lines:
        return [], []
    heights = [l["sz"] for l in lines]
    med = statistics.median(heights)
    ymax = max(l["y"] for l in lines) or 1.0
    body, notes = [], []
    seen_fn = False
    for l in lines:
        t = l["t"]
        small = l["sz"] <= med * 0.86
        bottom = l["y"] >= ymax * 0.70
        starts_fn = t.startswith("(") and len(t) > 2 and t[1].isdigit()
        if starts_fn:
            seen_fn = True
        if seen_fn and (small or bottom or starts_fn):
            notes.append(t)
        elif small and bottom:
            notes.append(t)
        else:
            body.append(t)
    if not body:
        return [l["t"] for l in lines], []
    return body, notes


def ocr_page_job(payload: tuple) -> tuple[int, dict, str]:
    pdf_path, page_index, cache_path = payload
    cache = Path(cache_path)
    if cache.exists():
        return page_index, json.loads(cache.read_text(encoding="utf-8")), "cache"
    doc = fitz.open(pdf_path)
    img = render_gray(doc[page_index])
    doc.close()
    lines = tesseract_lines(img)
    body, notes = split_body_notes(lines)
    rec = {"page": page_index + 1, "body": body, "notes": notes}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    return page_index, rec, "ocr"


def ocr_volume(vol: int, pdf: Path) -> list[dict]:
    out_vol = OCR_DIR / f"vol_{vol:02d}"
    out_vol.mkdir(parents=True, exist_ok=True)
    merged_path = OCR_DIR / f"vol_{vol:02d}.ocr.pages.json"
    doc = fitz.open(pdf)
    n = doc.page_count
    doc.close()
    jobs = []
    for i in range(n):
        jobs.append((str(pdf), i, str(out_vol / f"page_{i+1:04d}.json")))
    pages: list[dict | None] = [None] * n
    done = sum(1 for _, _, p in jobs if Path(p).exists())
    print(f"Volume {vol:02d}  {pdf.name}  {n} páginas  já OCR={done}", flush=True)
    t0 = time.time()
    finished = done
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futs = {pool.submit(ocr_page_job, job): job[1] for job in jobs}
        for fut in as_completed(futs):
            idx, rec, src = fut.result()
            pages[idx] = rec
            if src == "ocr":
                finished += 1
            if finished % 15 == 0 or finished == n:
                elapsed = time.time() - t0
                print(
                    f"  vol {vol:02d}  {finished}/{n}  "
                    f"{elapsed/60:.1f} min",
                    flush=True,
                )
    # preencher falhas a partir do disco
    for i in range(n):
        if pages[i] is None:
            p = out_vol / f"page_{i+1:04d}.json"
            pages[i] = json.loads(p.read_text(encoding="utf-8"))
    result = list(pages)
    merged_path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    EXTRACT.mkdir(parents=True, exist_ok=True)
    # o parser passa a preferir este ficheiro
    (EXTRACT / f"vol_{vol:02d}.pages.json").write_text(
        json.dumps(result, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Volume {vol:02d} concluído em {(time.time()-t0)/60:.1f} min", flush=True)
    return result


def main():
    os.environ.setdefault("OMP_THREAD_LIMIT", "1")
    mapping = find_pdfs()
    vols = [int(x) for x in sys.argv[1:]] or list(range(1, 17))
    for vol in vols:
        if vol not in mapping:
            print("FALTA PDF volume", vol)
            continue
        ocr_volume(vol, mapping[vol])


if __name__ == "__main__":
    main()
