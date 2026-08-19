# -*- coding: utf-8 -*-
"""Compara camada de texto do PDF com Tesseract (por) numa página difícil."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import fitz
import pytesseract
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

PDF = Path(r"E:\PROJETOS-CURSOR\BIBLIA\documentos\biblia-vulgata-padre-antonio-pereira-de-figueiredo-05.pdf")
PAGE = 340  # 1-based: Salmo 126/127
DPI = 300


def render(page) -> Image.Image:
    zoom = DPI / 72
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
    return Image.frombytes("L", [pix.width, pix.height], pix.samples)


def tesseract_lines(img: Image.Image) -> list[str]:
    data = pytesseract.image_to_data(
        img, lang="por", config="--oem 1 --psm 4", output_type=pytesseract.Output.DICT
    )
    lines = {}
    n = len(data["text"])
    for i in range(n):
        txt = (data["text"][i] or "").strip()
        if not txt:
            continue
        try:
            conf = float(data["conf"][i])
        except (TypeError, ValueError):
            conf = 0
        if conf < 20:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        rec = lines.setdefault(key, {"y": data["top"][i], "h": data["height"][i], "w": []})
        rec["w"].append((data["left"][i], txt, data["height"][i]))
    out = []
    for key in sorted(lines, key=lambda k: lines[k]["y"]):
        rec = lines[key]
        rec["w"].sort()
        out.append(" ".join(t for _, t, _ in rec["w"]))
    return out


def main():
    cache = json.loads(Path(r"E:\PROJETOS-CURSOR\BIBLIA\_extract\vol_05.pages.json").read_text(encoding="utf-8"))
    old = cache[PAGE - 1]
    print("=== CAMADA PDF (PyMuPDF) p.", PAGE, "===")
    for ln in old["body"][:12]:
        print(ln)
    print("-- notas --")
    for ln in old["notes"][:4]:
        print(ln)

    doc = fitz.open(PDF)
    img = render(doc[PAGE - 1])
    doc.close()
    print("\n=== TESSERACT por @300dpi p.", PAGE, "===")
    for ln in tesseract_lines(img)[:18]:
        print(ln)


if __name__ == "__main__":
    main()
