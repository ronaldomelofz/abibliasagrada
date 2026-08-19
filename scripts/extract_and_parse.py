# -*- coding: utf-8 -*-
"""Extrai texto real dos PDFs Figueiredo (documentos/) e monta
livros catolicos com versiculos + notas explicativas."""
from __future__ import annotations

import json
import os
import re
import shutil
import statistics
import unicodedata
from collections import Counter
from pathlib import Path

import fitz

DOCS = Path(r"E:\PROJETOS-CURSOR\BIBLIA\documentos")
EXTRACT = Path(r"E:\PROJETOS-CURSOR\BIBLIA\_extract")
OCR_DIR = Path(r"E:\PROJETOS-CURSOR\BIBLIA\_ocr")
OUT = Path(r"E:\PROJETOS-CURSOR\BIBLIA\data")
WEB_DATA = Path(r"E:\PROJETOS-CURSOR\BIBLIA\web\data")
WEB_PUBLIC = Path(r"E:\PROJETOS-CURSOR\BIBLIA\web\public\data")

# Canone catolico (Trento): 73 livros. Capitulos da Vulgata / Figueiredo.
BOOKS = [
    ("genesis", "Genesis", "Gn", "at", 50),
    ("exodo", "Exodo", "Ex", "at", 40),
    ("levitico", "Levitico", "Lv", "at", 27),
    ("numeros", "Numeros", "Nm", "at", 36),
    ("deuteronomio", "Deuteronomio", "Dt", "at", 34),
    ("josue", "Josue", "Js", "at", 24),
    ("juizes", "Juizes", "Jz", "at", 21),
    ("rute", "Rute", "Rt", "at", 4),
    ("1-samuel", "I Samuel", "1Sm", "at", 31),
    ("2-samuel", "II Samuel", "2Sm", "at", 24),
    ("1-reis", "I Reis", "1Rs", "at", 22),
    ("2-reis", "II Reis", "2Rs", "at", 25),
    ("1-cronicas", "I Paralipomenos", "1Cr", "at", 29),
    ("2-cronicas", "II Paralipomenos", "2Cr", "at", 36),
    ("esdras", "Esdras", "Esd", "at", 10),
    ("neemias", "Neemias", "Ne", "at", 13),
    ("tobias", "Tobias", "Tb", "at", 14),
    ("judite", "Judite", "Jt", "at", 16),
    ("ester", "Ester", "Est", "at", 16),
    ("jo", "Jo", "Jo", "at", 42),
    ("salmos", "Salmos", "Sl", "at", 150),
    ("proverbios", "Proverbios", "Pr", "at", 31),
    ("eclesiastes", "Eclesiastes", "Ecl", "at", 12),
    ("cantico", "Cantico dos Canticos", "Ct", "at", 8),
    ("sabedoria", "Sabedoria", "Sb", "at", 19),
    ("eclesiastico", "Eclesiastico", "Eclo", "at", 51),
    ("isaias", "Isaias", "Is", "at", 66),
    ("jeremias", "Jeremias", "Jr", "at", 52),
    ("lamentacoes", "Lamentacoes", "Lm", "at", 5),
    ("baruc", "Baruc", "Br", "at", 6),
    ("ezequiel", "Ezequiel", "Ez", "at", 48),
    ("daniel", "Daniel", "Dn", "at", 14),
    ("oseias", "Oseias", "Os", "at", 14),
    ("joel", "Joel", "Jl", "at", 3),
    ("amos", "Amos", "Am", "at", 9),
    ("abdias", "Abdias", "Ab", "at", 1),
    ("jonas", "Jonas", "Jn", "at", 4),
    ("miqueias", "Miqueias", "Mq", "at", 7),
    ("naum", "Naum", "Na", "at", 3),
    ("habacuc", "Habacuc", "Hab", "at", 3),
    ("sofonias", "Sofonias", "Sf", "at", 3),
    ("ageu", "Ageu", "Ag", "at", 2),
    ("zacarias", "Zacarias", "Zc", "at", 14),
    ("malaquias", "Malaquias", "Ml", "at", 4),
    ("1-macabeus", "I Macabeus", "1Mc", "at", 16),
    ("2-macabeus", "II Macabeus", "2Mc", "at", 15),
    ("mateus", "Mateus", "Mt", "nt", 28),
    ("marcos", "Marcos", "Mc", "nt", 16),
    ("lucas", "Lucas", "Lc", "nt", 24),
    ("joao", "Joao", "Jo", "nt", 21),
    ("atos", "Atos dos Apostolos", "At", "nt", 28),
    ("romanos", "Romanos", "Rm", "nt", 16),
    ("1-corintios", "I Corintios", "1Cor", "nt", 16),
    ("2-corintios", "II Corintios", "2Cor", "nt", 13),
    ("galatas", "Galatas", "Gl", "nt", 6),
    ("efesios", "Efesios", "Ef", "nt", 6),
    ("filipenses", "Filipenses", "Fl", "nt", 4),
    ("colossenses", "Colossenses", "Cl", "nt", 4),
    ("1-tessalonicenses", "I Tessalonicenses", "1Ts", "nt", 5),
    ("2-tessalonicenses", "II Tessalonicenses", "2Ts", "nt", 3),
    ("1-timoteo", "I Timoteo", "1Tm", "nt", 6),
    ("2-timoteo", "II Timoteo", "2Tm", "nt", 4),
    ("tito", "Tito", "Tt", "nt", 3),
    ("filemom", "Filemom", "Fm", "nt", 1),
    ("hebreus", "Hebreus", "Hb", "nt", 13),
    ("tiago", "Tiago", "Tg", "nt", 5),
    ("1-pedro", "I Pedro", "1Pd", "nt", 5),
    ("2-pedro", "II Pedro", "2Pd", "nt", 3),
    ("1-joao", "I Joao", "1Jo", "nt", 5),
    ("2-joao", "II Joao", "2Jo", "nt", 1),
    ("3-joao", "III Joao", "3Jo", "nt", 1),
    ("judas", "Judas", "Jd", "nt", 1),
    ("apocalipse", "Apocalipse", "Ap", "nt", 22),
]

# Nomes com acento para a UI (UTF-8 escrito em runtime)
DISPLAY = {
    "genesis": "Gênesis",
    "exodo": "Êxodo",
    "levitico": "Levítico",
    "numeros": "Números",
    "deuteronomio": "Deuteronômio",
    "josue": "Josué",
    "juizes": "Juízes",
    "1-cronicas": "I Paralipômenos",
    "2-cronicas": "II Paralipômenos",
    "jo": "Jó",
    "proverbios": "Provérbios",
    "cantico": "Cântico dos Cânticos",
    "eclesiastico": "Eclesiástico",
    "isaias": "Isaías",
    "lamentacoes": "Lamentações",
    "oseias": "Oséias",
    "amos": "Amós",
    "miqueias": "Miquéias",
    "joao": "João",
    "atos": "Atos dos Apóstolos",
    "1-corintios": "I Coríntios",
    "2-corintios": "II Coríntios",
    "galatas": "Gálatas",
    "efesios": "Efésios",
    "1-timoteo": "I Timóteo",
    "2-timoteo": "II Timóteo",
    "filemom": "Filêmon",
    "1-joao": "I João",
    "2-joao": "II João",
    "3-joao": "III João",
}

ANCHORS = {
    (1, 29): "genesis", (1, 219): "exodo", (1, 375): "levitico",
    (2, 5): "numeros", (2, 145): "deuteronomio", (2, 273): "josue",
    (2, 357): "juizes", (2, 446): "rute",
    (3, 9): "1-samuel", (3, 117): "2-samuel", (3, 205): "1-reis",
    (3, 308): "2-reis", (3, 411): "1-cronicas",
    (4, 5): "2-cronicas", (4, 121): "esdras", (4, 155): "neemias",
    (4, 205): "tobias", (4, 241): "judite", (4, 287): "ester", (4, 337): "jo",
    (5, 17): "salmos", (5, 381): "proverbios",
    (6, 5): "proverbios", (6, 53): "eclesiastes", (6, 87): "cantico",
    (6, 123): "sabedoria", (6, 191): "eclesiastico", (6, 391): "isaias",
    (7, 5): "isaias", (7, 205): "jeremias", (7, 413): "lamentacoes",
    (8, 13): "baruc", (8, 45): "ezequiel", (8, 261): "daniel", (8, 345): "oseias",
    (9, 7): "joel", (9, 21): "amos", (9, 41): "abdias", (9, 51): "jonas",
    (9, 61): "miqueias", (9, 79): "naum", (9, 89): "habacuc", (9, 101): "sofonias",
    (9, 113): "ageu", (9, 123): "zacarias", (9, 161): "malaquias",
    (9, 177): "1-macabeus", (9, 291): "2-macabeus",
    (10, 21): "mateus", (10, 197): "marcos", (10, 287): "lucas",
    (11, 21): "joao", (11, 161): "atos", (11, 317): "romanos", (11, 389): "1-corintios",
    (12, 7): "2-corintios", (12, 49): "galatas", (12, 71): "efesios",
    (12, 95): "filipenses", (12, 111): "colossenses",
    (12, 127): "1-tessalonicenses", (12, 141): "2-tessalonicenses",
    (12, 153): "1-timoteo", (12, 177): "2-timoteo", (12, 191): "tito",
    (12, 203): "filemom", (12, 215): "hebreus", (12, 271): "tiago",
    (12, 297): "1-pedro", (12, 319): "2-pedro", (12, 333): "1-joao",
    (12, 351): "2-joao", (12, 357): "3-joao", (12, 363): "judas",
    (12, 373): "apocalipse",
}

# Volumes 6 e 7 continuam o livro do volume anterior (Provérbios, Isaías).
VOLUME_CONTINUES = {6, 7}

# Páginas em que o OCR desfigurou o título do capítulo (CaríruLo, Saimo, 2 Esdras).
CHAPTER_STARTS = {
    (1, 61): ("genesis", 11),
    (1, 364): ("exodo", 39),
    (1, 367): ("exodo", 40),
    (2, 9): ("numeros", 1),
    (2, 173): ("deuteronomio", 6),
    (2, 210): ("deuteronomio", 18),
    (2, 361): ("juizes", 1),
    (3, 115): ("1-samuel", 31),
    (4, 160): ("neemias", 3),
    (4, 169): ("neemias", 6),
    (4, 196): ("neemias", 13),
    (5, 42): ("salmos", 12),
    (5, 64): ("salmos", 21),
    (5, 162): ("salmos", 56),
    (5, 256): ("salmos", 92),
    (5, 311): ("salmos", 116),
    (5, 339): ("salmos", 125),
    (5, 345): ("salmos", 131),
    (5, 347): ("salmos", 132),
    (5, 429): ("proverbios", 15),
    (6, 104): ("cantico", 6),
    (6, 144): ("sabedoria", 9),
    (6, 416): ("isaias", 6),
    (6, 427): ("isaias", 8),
    (7, 5): ("isaias", 12),
    (7, 306): ("jeremias", 27),
    (7, 437): ("lamentacoes", 5),
    (8, 304): ("daniel", 8),
    (9, 54): ("jonas", 2),
    (9, 347): ("2-macabeus", 12),
    (12, 25): ("2-corintios", 8),
    (12, 171): ("1-timoteo", 6),
}

HEADER_RX = [
    ("genesis", re.compile(r"G[eéê]nesis", re.I)),
    ("exodo", re.compile(r"xodo", re.I)),
    ("levitico", re.compile(r"Lev[ií]tico", re.I)),
    ("numeros", re.compile(r"N[uú]meros", re.I)),
    ("deuteronomio", re.compile(r"Deuteron", re.I)),
    ("josue", re.compile(r"Josu[eé]", re.I)),
    ("juizes", re.compile(r"Ju[ií]zes", re.I)),
    ("rute", re.compile(r"^Rute\b", re.I)),
    ("1-samuel", re.compile(r"(?:1|I|À|à)\s*(?:Reis|Samuel)", re.I)),
    ("2-samuel", re.compile(r"(?:2|II)\s*(?:Reis|Samuel)", re.I)),
    ("1-reis", re.compile(r"(?:3|III)\s*Reis", re.I)),
    ("2-reis", re.compile(r"(?:4|IV)\s*Reis", re.I)),
    ("1-cronicas", re.compile(r"(?:1|I)\s*Paralip", re.I)),
    ("2-cronicas", re.compile(r"(?:2|II)\s*Paralip", re.I)),
    ("esdras", re.compile(r"Esdras", re.I)),
    ("neemias", re.compile(r"Neemias|(?:2|II)\s*Esdras", re.I)),
    ("tobias", re.compile(r"Tobias", re.I)),
    ("judite", re.compile(r"Judite", re.I)),
    ("ester", re.compile(r"Ester", re.I)),
    ("jo", re.compile(r"^J[oó]\s+\d", re.I)),
    ("salmos", re.compile(r"S\s*a[il]\s*m[oe]", re.I)),
    ("proverbios", re.compile(r"Prov[eé]rbios", re.I)),
    ("eclesiastes", re.compile(r"Eclesiaste", re.I)),
    ("cantico", re.compile(r"C[aâ]ntico", re.I)),
    ("sabedoria", re.compile(r"Sabedoria", re.I)),
    ("eclesiastico", re.compile(r"Eclesi(?!aste)", re.I)),
    ("isaias", re.compile(r"Isa[ií]as", re.I)),
    ("jeremias", re.compile(r"Jeremias", re.I)),
    ("lamentacoes", re.compile(r"Lamenta|Ora[cç][aã]o\s+de\s+Jeremias", re.I)),
    ("baruc", re.compile(r"Baruc", re.I)),
    ("ezequiel", re.compile(r"Ezequiel", re.I)),
    ("daniel", re.compile(r"Daniel", re.I)),
    ("oseias", re.compile(r"Os[eé]ias", re.I)),
    ("joel", re.compile(r"^Joel\b", re.I)),
    ("amos", re.compile(r"Am[oó]s", re.I)),
    ("abdias", re.compile(r"Abd", re.I)),
    ("jonas", re.compile(r"Jonas", re.I)),
    ("miqueias", re.compile(r"Miqu[eê]ias", re.I)),
    ("naum", re.compile(r"Naum", re.I)),
    ("habacuc", re.compile(r"Habacuc", re.I)),
    ("sofonias", re.compile(r"Sofonias", re.I)),
    ("ageu", re.compile(r"Ageu", re.I)),
    ("zacarias", re.compile(r"Zacarias", re.I)),
    ("malaquias", re.compile(r"Malaquias", re.I)),
    ("1-macabeus", re.compile(r"(?:1|I)\s*Macabeus", re.I)),
    ("2-macabeus", re.compile(r"(?:2|II)\s*Macabeus", re.I)),
    ("mateus", re.compile(r"Mateus", re.I)),
    ("marcos", re.compile(r"Marcos", re.I)),
    ("lucas", re.compile(r"Lucas", re.I)),
    ("joao", re.compile(r"Jo[\u00e3a]o", re.I)),
    ("atos", re.compile(r"Atos", re.I)),
    ("romanos", re.compile(r"Romanos", re.I)),
    ("1-corintios", re.compile(r"(?:1|I)\s*Cor", re.I)),
    ("2-corintios", re.compile(r"(?:2|II)\s*Cor", re.I)),
    ("galatas", re.compile(r"G[aá]latas", re.I)),
    ("efesios", re.compile(r"Ef[eé]sios", re.I)),
    ("filipenses", re.compile(r"Filipenses", re.I)),
    ("colossenses", re.compile(r"Colossenses", re.I)),
    ("1-tessalonicenses", re.compile(r"Tessalonic", re.I)),
    ("2-tessalonicenses", re.compile(r"(?:2|II|Segunda)\s*.{0,20}Tessal", re.I)),
    ("1-timoteo", re.compile(r"(?:1|I)\s*Tim", re.I)),
    ("2-timoteo", re.compile(r"(?:2|II)\s*Tim", re.I)),
    ("tito", re.compile(r"Tito", re.I)),
    ("filemom", re.compile(r"Fil[eê]mon", re.I)),
    ("hebreus", re.compile(r"Hebreus", re.I)),
    ("tiago", re.compile(r"Tiago", re.I)),
    ("1-pedro", re.compile(r"(?:1|I)\s*Pedro", re.I)),
    ("2-pedro", re.compile(r"(?:2|II)\s*Pedro", re.I)),
    ("1-joao", re.compile(r"(?:1|I)\s*Jo", re.I)),
    ("2-joao", re.compile(r"(?:2|II)\s*Jo", re.I)),
    ("3-joao", re.compile(r"(?:3|III)\s*Jo", re.I)),
    ("judas", re.compile(r"Judas", re.I)),
    ("apocalipse", re.compile(r"Apocalipse", re.I)),
]

RE_CH = re.compile(r"Cap[ií]tulo\s+(\d{1,3})|CAP[IÍ]TULO\s+(\d{1,3})", re.I)
RE_SALMO = re.compile(r"^S\s*[aáàt]\s*[ilt1]\s*[.,]?\s*m[oe]\s+([\d\s]{1,11})\s*\.?\s*$", re.I)
RE_TABLE = re.compile(
    r"GERAH|BEGAH|\bSICLO\b|MANEH|\bTALENTO\b|ETSB?AH|ZERETH|\bAMNAH\b|"
    r"TETALK|GAUCH|GRAMAS|\bMETROS\b|COVADO",
    re.I,
)
RE_VERSE = re.compile(r"^(\d{1,3})[.\-:\u2013\u2014]?\s+(.*\S.*)$")
RE_VERSE_ONLY = re.compile(r"^(\d{1,3})\s*[.\-:]?\s*$")
RE_FN_MARK = re.compile(r"^\(\s*(\d{1,2})\s*\)")
RE_FN_MARK_ALT = re.compile(
    r"^(?:\((?P<a>\d{1,2})\)|(?P<b>\d{1,2})\s*[\)\]]|(?P<c>\d{1,2})\s+[—–\-])\s+"
)
RE_FN_INLINE = re.compile(r"\(\s*(\d{1,2})\s*\)")
RE_INDEX = re.compile(r"INDICE|I N D I C E", re.I)
RE_PAGE_NUM = re.compile(r"^[\-\u2014\u2013]?\s*\d{1,3}\s*[\-\u2014\u2013]?\s*$")


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).upper()


def clean(s: str) -> str:
    s = s.replace("\u00ad", "").replace("\xa0", " ")
    return re.sub(r"[ \t]+", " ", s).strip()


def normalize_body(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"\bd,e\b", "de", text)
    text = re.sub(r"\bd,o\b", "do", text)
    text = re.sub(r"\bd,a\b", "da", text)
    text = re.sub(r"Faça-sc", "Faça-se", text)
    text = re.sub(r"fêz-sc", "fêz-se", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
    return text.replace(" ,", ",").replace(" .", ".").strip(" -\u2014")


def find_pdfs():
    mapping = {}
    skip = []
    for f in DOCS.glob("*.pdf"):
        m = re.search(r"figueiredo-(\d+)", f.name)
        if m:
            mapping[int(m.group(1))] = f
        else:
            skip.append(f.name)
    return mapping, skip


def extract_page_lines(page) -> list[dict]:
    d = page.get_text("dict")
    raw = []
    for b in d.get("blocks", []):
        if b.get("type") != 0:
            continue
        for line in b.get("lines", []):
            spans = line.get("spans") or []
            if not spans:
                continue
            text = clean("".join(s.get("text", "") for s in spans))
            if not text:
                continue
            try:
                sz = statistics.median([float(s.get("size", 0)) for s in spans])
            except statistics.StatisticsError:
                sz = float(spans[0].get("size", 0))
            y = float(line["bbox"][1])
            x = float(line["bbox"][0])
            raw.append((y, x, sz, text))
    raw.sort()
    merged: list[list] = []
    for y, x, sz, text in raw:
        if merged and abs(merged[-1][0] - y) < 2.2:
            prev = merged[-1]
            if x >= prev[1]:
                prev[3] = clean(prev[3] + " " + text)
            else:
                prev[3] = clean(text + " " + prev[3])
                prev[1] = x
            prev[2] = max(prev[2], sz)
        else:
            merged.append([y, x, sz, text])
    return [{"y": a[0], "x": a[1], "sz": a[2], "t": a[3]} for a in merged]


def split_body_notes(lines: list[dict]) -> tuple[list[str], list[str]]:
    if not lines:
        return [], []
    freq = Counter(round(l["sz"], 1) for l in lines)
    common = [sz for sz, n in freq.most_common() if n >= 3]
    if not common:
        return [l["t"] for l in lines], []
    body_sz = max(common)
    smaller = [s for s in common if s <= body_sz - 0.7]
    note_sz = max(smaller) if smaller else None
    body, notes, titles = [], [], []
    seen_verse = False
    for l in lines:
        t = l["t"]
        sz = l["sz"]
        if RE_PAGE_NUM.match(t) or fold(t).startswith("ANO SANTO"):
            continue
        if "BIBLIA SAGRADA" in fold(t) and sz > 12:
            continue
        is_chapter = bool(RE_CH.search(t) or RE_SALMO.match(t))
        is_body = sz >= body_sz - 0.45 or is_chapter
        if is_body:
            if RE_VERSE.match(t) or RE_VERSE_ONLY.match(t):
                seen_verse = True
            body.append(t)
            continue
        if note_sz is not None and sz <= note_sz + 0.45:
            if not seen_verse and not RE_FN_MARK.match(t):
                titles.append(t)
            else:
                notes.append(t)
            continue
        if seen_verse:
            notes.append(t)
        else:
            titles.append(t)
    return titles + body, notes


def parse_notes(note_lines: list[str]) -> dict[int, str]:
    notes: dict[int, str] = {}
    cur = None
    buf = []

    def flush():
        nonlocal cur, buf
        if cur is not None:
            txt = normalize_body(" ".join(buf))
            if len(txt) > 3:
                notes[cur] = txt
        cur = None
        buf = []

    for ln in note_lines:
        m = RE_FN_MARK.match(ln) or RE_FN_MARK_ALT.match(ln)
        if m:
            flush()
            cur = int(next(g for g in m.groups() if g))
            rest = ln[m.end() :].strip()
            buf = [rest] if rest else []
        elif cur is not None:
            buf.append(ln)
    flush()
    return notes


def extract_volume(vol: int, pdf: Path) -> list[dict]:
    ocr = OCR_DIR / f"vol_{vol:02d}.ocr.pages.json"
    cache = EXTRACT / f"vol_{vol:02d}.pages.json"
    if ocr.exists():
        print("  usando OCR Tesseract vol", vol)
        return json.loads(ocr.read_text(encoding="utf-8"))
    if cache.exists() and cache.stat().st_mtime >= pdf.stat().st_mtime:
        return json.loads(cache.read_text(encoding="utf-8"))
    doc = fitz.open(pdf)
    pages = []
    for i in range(doc.page_count):
        lines = extract_page_lines(doc[i])
        body, notes = split_body_notes(lines)
        pages.append({"page": i + 1, "body": body, "notes": notes})
        if (i + 1) % 100 == 0:
            print(f"  vol {vol:02d} page {i+1}/{doc.page_count}")
    doc.close()
    EXTRACT.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")
    return pages


class Store:
    def __init__(self):
        self.books = {
            s: {"esperado": e, "caps": {}}
            for s, _n, _a, _t, e in BOOKS
        }

    def add(self, slug, ch, vn, text, titulo, notas):
        if not slug or not ch or not vn:
            return
        meta = self.books[slug]
        if ch < 1 or ch > meta["esperado"] + 3 or vn < 1 or vn > 180:
            return
        text = normalize_body(re.sub(r"\(\s*\d{1,2}\s*\)", "", text))
        text = re.sub(r"\(\*\)", "", text).strip()
        text = strip_leaks(text)
        if len(text) < 2:
            return
        cap = meta["caps"].setdefault(ch, {"titulo": "", "v": {}})
        if titulo and not cap["titulo"]:
            cap["titulo"] = re.sub(r"\s+", " ", titulo).title()
        prev = cap["v"].get(vn)
        if not prev:
            cap["v"][vn] = {"t": text, "notas": list(notas)}
            return
        if len(text) > len(prev["t"]) + 8:
            # provavelmente continuacao mais completa
            if text.startswith(prev["t"][:20]) or prev["t"] in text:
                prev["t"] = text
            else:
                prev["t"] = normalize_body(prev["t"] + " " + text)
        elif text not in prev["t"]:
            prev["t"] = normalize_body(prev["t"] + " " + text)
        seen = {n["n"] for n in prev["notas"]}
        for n in notas:
            if n["n"] not in seen and n["t"]:
                prev["notas"].append(n)
                seen.add(n["n"])

    def add_notes(self, slug, ch, vn, notas):
        """Liga notas que o OCR leu no rodapé, mesmo sem (n) no versículo."""
        if not slug or not ch or not vn or not notas:
            return
        cap = self.books.get(slug, {}).get("caps", {}).get(ch)
        if not cap:
            return
        prev = cap["v"].get(vn)
        if not prev:
            return
        seen = {n["n"] for n in prev["notas"]}
        for n in notas:
            if n["n"] not in seen and n.get("t"):
                prev["notas"].append(n)
                seen.add(n["n"])


def parse_capitulo_num(ln: str) -> int | None:
    """Reconhece CAPÍTULO mesmo com OCR (CaríruLo dO, CAPÍTULO 2/, Caríruro)."""
    folded = re.sub(r"[\s.]", "", fold(ln))
    if not folded.startswith(("CAP", "CAR")):
        return None

    def decode_num(raw: str) -> int | None:
        if raw in ("DO", "D0", "4O", "4o"):
            return 40
        raw = raw.replace("/", "7").replace("O", "0").replace("I", "1").replace("L", "1")
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= 180:
                return n
        return None

    m = re.search(r"(?:CAPITULO|CARITULO|CARIRULO)(\d{1,3})$", folded)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 180:
            return n
    m = re.match(r"^C[A-Z]{5,12}(\d{1,3})$", folded)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 180:
            return n
    m = re.search(r"CAPITULO([0-9OIDSB/L]{1,3})$", folded)
    if m:
        n = decode_num(m.group(1))
        if n is not None:
            return n
    m = re.match(r"^C[A-Z]{5,12}([0-9OIDSB/L]{2,3})$", folded) or re.match(
        r"^C[A-Z]{5,12}([0-9OIDSB/L])$", folded
    )
    if m:
        return decode_num(m.group(1))
    return None


def normalize_verse_prefix(ln: str) -> str:
    """I3 / l2 / Il / i no início da linha (I e l lidos como 1)."""
    ln = re.sub(r"^[IlÍ](\d)", r"1\1", ln)
    ln = re.sub(r"^(?:Il|Íl|I1|lI)\s+", "1 ", ln)
    ln = re.sub(r"^[iIlÍl]\s+(?=[A-ZÁÉÍÓÚÀÂÃÄÊÔÕÜ])", "1 ", ln)
    return ln


def unglue_pagenum(ln: str) -> str:
    """'22 Epistola ... Coríntios 8, 2-10' → remove o 22 colado pelo OCR."""
    m = re.match(r"^(\d{2,3})\s+(.+)$", ln)
    if not m:
        return ln
    rest = m.group(2)
    if re.search(r"\d{1,3}-?\s*,\s*\d", rest) and re.search(
        r"Ep[ií]stola|Salmo|C[aâ]ntico|Macabeus|Reis|Paralip", rest, re.I
    ):
        return rest
    return ln


def looks_like_chapter_title(ln: str) -> bool:
    letters = re.sub(r"[^A-Za-zÀ-ÿ]", "", ln)
    if len(letters) < 8:
        return False
    upp = sum(1 for c in letters if c.isupper())
    return upp / len(letters) >= 0.72


def is_front_matter(body: list[str]) -> bool:
    blob = fold(" ".join(body[:12]))
    if "ABREVIATURAS" in blob and "SINAIS" in blob:
        return True
    if "EXPLICACAO DAS ABREVIATURAS" in blob or "KXPLICACAO DAS ABREVIATURAS" in blob:
        return True
    if "NIHIL OBSTAT" in blob or blob.startswith("IMPRIMATUR"):
        return True
    if blob.startswith("BIBLIA SAGRADA") and (
        "ABREVIATUR" in blob or "CONTENDO" in blob or "ANO SANTO" in blob
        or "VOLUME" in blob or len(body) <= 3
    ):
        return True
    return False


def is_end_matter(body: list[str], page: int) -> bool:
    if not body or page < 250:
        return False
    blob = fold(" ".join(body[:8]))
    if "INDICE DAS GRAVURAS" in blob or (page > 350 and "GRAVURAS" in blob):
        return True
    if page > 300 and ("INDICE" in fold(body[0]) or RE_INDEX.search(body[0])):
        return True
    return False


def looks_like_book_intro(body: list[str], current: str | None) -> bool:
    """Introdução do livro seguinte (Tobias, Baruc, Joel…) ainda no volume anterior."""
    if not body:
        return False
    head = fold(" ".join(body[:8]))
    if "INTRODUCAO" not in head:
        return False
    first = fold(body[0])
    names: list[tuple[str, str]] = []
    for slug, nome, *_rest in BOOKS:
        names.append((slug, fold(nome)))
        if slug in DISPLAY:
            names.append((slug, fold(DISPLAY[slug])))
    for slug, nm in names:
        if slug == current:
            continue
        token = re.sub(r"^(?:I|II|III)\s+", "", nm).strip()
        if len(token) >= 4 and token[:6] in first:
            return True
    if current != "baruc" and ("BARUG" in first or "BARUC" in first):
        return True
    if len(body[0]) <= 48 and ("AUTOR" in head or "EPOCA" in head or "DIVISAO" in head):
        return True
    return False


RE_RUN_HDR = re.compile(
    r"(?:G[eêé]nesis|[ÊE]xodo|Lev[ií]tico|N[uú]meros|Deuteron[oô]mio|Josu[eé]|Ju[ií]zes|"
    r"Rute|(?:[I1-4]|II|III|IV)\s*(?:Samuel|Reis|Paralip\w*|Esdras|Macabeus|Cor[ií]ntios)|"
    r"Neemias|Tobias|Judite|Ester|S\s*a[il]\s*m[oe]|Prov[eé]rbios|Eclesiastes|C[aâ]ntico|"
    r"Sabedoria|Eclesi[aá]stico|Isa[ií]as|Jeremias|Lamenta[cç][oõ]es|"
    r"Ora[cç][aã]o\s+de\s+Jeremias|Baruc|Ezequiel|Daniel|Jonas|Joel|Am[oó]s|"
    r"Mateus|Marcos|Lucas|Jo[aã]o|Atos|Romanos|G[aá]latas|Ef[eé]sios|Filipenses|"
    r"Colossenses|Hebreus|Tiago|Apocalipse|2\s*Esdras|Ep[ií]stola[^\d,]{0,48})"
    r"\s+\d{1,3}\s*[,:]\s*\d{1,3}(?:\s*[-–—:]\s*\d{1,3})?",
    re.I,
)


def strip_leaks(text: str) -> str:
    """Tira cabeçalhos de página, imprimatur e introduções colados no versículo."""
    text = RE_RUN_HDR.sub(" ", text)
    text = re.split(r"\bNIHIL\s+OBSTAT\b", text, flags=re.I)[0]
    text = re.split(r"\bIMPRIMATUR\b", text, flags=re.I)[0]
    text = re.split(r"\bINTRODU[CÇ][AÃ]O\b", text, flags=re.I)[0]
    text = re.split(r"\bParte\s+[—\u2013\u2014\-]\s*\d", text, flags=re.I)[0]
    text = re.sub(r"\.\s+\d{1,3}$", ".", text)
    return normalize_body(text)


def is_junk_line(ln: str) -> bool:
    f = fold(ln)
    if RE_PAGE_NUM.match(ln) or re.match(r"^[\-\u2014\u2013]\s*\d{1,3}\s*[\-\u2014\u2013]$", ln):
        return True
    if RE_TABLE.search(ln):
        return True
    if "ABREVIATURAS" in f and "SINAIS" in f:
        return True
    if "EXPLICACAO DAS ABREVIATURAS" in f or "KXPLICACAO DAS ABREVIATURAS" in f:
        return True
    if "NIHIL OBSTAT" in f or f.startswith("IMPRIMATUR"):
        return True
    if f.startswith("BIBLIA SAGRADA") and len(ln) < 80:
        return True
    if re.search(r"\bquilos\b|Tell-el-|aproximadamente\s+\d", ln, re.I):
        return True
    if "MEDIDA D" in f and "EXTENS" in f:
        return True
    if re.match(r"^(GRAMAS|METROS|LOG\.?)$", f.strip()):
        return True
    # linhas de tabela: quase só números e unidades
    letters = re.sub(r"[^A-Za-zÀ-ÿ]", "", ln)
    digits = re.findall(r"\d", ln)
    if letters and len(letters) <= 4 and len(digits) >= 4:
        return True
    if re.search(
        r"Calmet|Menochio|Bossuet|Glaire|Duhamel|Corn[eé]lio a Lapide|Vigouroux",
        ln,
        re.I,
    ) and not re.match(r"^\d{1,3}\s", ln):
        return True
    return False


_NOTE_CONT = re.compile(
    r"^(e|é|o|a|os|as|um|uma|de|do|da|dos|das|que|porque|para|com|não|nem|se|"
    r"lhe|lhes|me|te|nos|vos|em|no|na|por|mais|mas|como|quando|ou|ao|à|aos|às|"
    r"nossa|nosso|nossas|nossos|este|esta|isto|esse|essa|isso|ele|ela|eles|elas|"
    r"eu|tu|nós|vós|seu|sua|seus|suas|meu|minha|já|então|depois|ainda|também|"
    r"até|sem|sob|entre|sobre|sôbre|pela|pelo|pelos|pelas|assim|pois|logo)\b",
    re.I,
)


def is_note_fragment(ln: str) -> bool:
    """Nota de rodapé que o OCR meteu no corpo (começa a meio da palavra)."""
    if not ln or ln[0].isupper() or ln[0].isdigit():
        return False
    if _NOTE_CONT.match(ln):
        return False
    return len(ln) > 24


def should_append_line(ln: str) -> bool:
    if not ln or is_junk_line(ln) or is_running_header(ln) or is_note_fragment(ln):
        return False
    if ln[0].islower() and len(ln) > 55 and not re.match(
        r"^(e|é|mas|porque|que|para|quando|depois)\b", ln, re.I
    ):
        return False
    return True


def is_bare_capitulo(ln: str) -> bool:
    folded = re.sub(r"[\s.]", "", fold(ln))
    return bool(re.match(r"^CA(?:PITULO|RITULO|RIRULO|RIRUTRO|PITVLO)$", folded))


def looks_like_scripture(text: str) -> bool:
    t = (text or "").strip()
    if len(t) < 12 or is_junk_line(t):
        return False
    letters = re.sub(r"[^A-Za-zÀ-ÿ]", "", t)
    return len(letters) >= 8


def is_running_header(ln: str) -> bool:
    core = unglue_pagenum(ln)
    if not (10 <= len(core) <= 110):
        return False
    if re.search(r"Pereira|Calmet|Bossuet|Vigouroux|Menochio", core, re.I):
        return False
    return bool(re.search(r"\d{1,3}-?\s*[,:]\s*\d", core))


def header_chapters(ln: str, current: str | None = None, expected: dict | None = None) -> list[int]:
    """Capítulos no cabeçalho, com dígitos espaçados, hífen de OCR ou 153→15."""
    ln = unglue_pagenum(ln)
    out: list[int] = []
    max_ch = expected[current] if current and expected else 200
    for m in re.finditer(r"(\d[\d\s]{0,8})-?\s*,", ln):
        digits = re.sub(r"\s+", "", m.group(1))
        if not digits.isdigit():
            continue
        n = int(digits)
        if n > max_ch and len(digits) >= 3:
            cand = int(digits[:2]) if int(digits[:2]) <= max_ch else int(digits[0])
            if 1 <= cand <= max_ch:
                n = cand
        if 1 <= n <= 200:
            out.append(n)
    return out


def advance_chapter(current: str | None, chapter: int, hc: int, expected: dict, max_jump: int = 2) -> int:
    """Só avança 1–2 capítulos. Recuos e saltos (índice, OCR) são ignorados."""
    if not current or not (1 <= hc <= expected[current] + 1):
        return chapter
    if hc == chapter:
        return hc
    if chapter < hc <= chapter + max_jump:
        return hc
    if chapter == 0 and 1 <= hc <= 2:
        return hc
    return chapter


def header_matches_book(ln: str, current: str | None) -> bool:
    if not current:
        return False
    core = unglue_pagenum(ln)
    for slug, rx in HEADER_RX:
        if slug == current and rx.search(core):
            return True
    # cabeçalho sem o número do livro: "Epístola ... aos Coríntios 8, 2-10"
    fallback = {
        "1-corintios": r"Cor[ií]ntios",
        "2-corintios": r"Cor[ií]ntios",
        "1-tessalonicenses": r"Tessalonic",
        "2-tessalonicenses": r"Tessalonic",
        "1-timoteo": r"Tim[oó]teo",
        "2-timoteo": r"Tim[oó]teo",
        "1-pedro": r"Pedro",
        "2-pedro": r"Pedro",
        "1-joao": r"Jo[\u00e3a]o",
        "2-joao": r"Jo[\u00e3a]o",
        "3-joao": r"Jo[\u00e3a]o",
        "1-macabeus": r"Macabeus",
        "2-macabeus": r"Macabeus",
        "1-samuel": r"(?:Reis|Samuel)",
        "2-samuel": r"(?:Reis|Samuel)",
        "1-reis": r"Reis",
        "2-reis": r"Reis",
        "1-cronicas": r"Paralip",
        "2-cronicas": r"Paralip",
    }
    rx = fallback.get(current)
    return bool(rx and re.search(rx, core, re.I))


def peek_first_verse_num(lines: list[str]) -> int | None:
    for ln in lines[:16]:
        if parse_capitulo_num(ln) or RE_SALMO.match(ln) or looks_like_chapter_title(ln) or is_junk_line(ln) or is_running_header(ln):
            continue
        if RE_VERSE_ONLY.match(ln):
            continue
        ln2 = normalize_verse_prefix(ln)
        vm = RE_VERSE.match(ln2)
        if vm:
            return int(vm.group(1))
    return None


def maybe_wrap_chapter(current, chapter, verse, last_vn, header_chs, expected, rest: str) -> int:
    # Versículo 3 não envolve: em capítulos curtos (Jonas 2) o 3 ainda é do mesmo capítulo.
    if not (last_vn and verse < last_vn and verse <= 2 and current):
        return chapter
    if verse == last_vn + 1:
        return chapter
    if not looks_like_scripture(rest):
        return chapter
    nxtc = [c for c in header_chs if chapter < c <= chapter + 2]
    if nxtc:
        return nxtc[0]
    if last_vn >= 4 and chapter < expected[current]:
        return chapter + 1
    return chapter


def apply_running_header(chapter, header_chs, first_verse, last_vn, current, expected) -> int:
    """Não salta de capítulo no meio de uma página que ainda termina o capítulo anterior."""
    if not header_chs:
        return chapter
    if len(header_chs) >= 2:
        return chapter
    hc = header_chs[0]
    if hc == chapter:
        return chapter
    # A página ainda acaba o capítulo anterior.
    if last_vn and first_verse and first_verse >= last_vn:
        return chapter
    if last_vn and first_verse and first_verse > 3 and first_verse < last_vn and hc == chapter + 1:
        return advance_chapter(current, chapter, hc, expected)
    # Capítulo novo: o primeiro versículo é 1–2 e o anterior já ia adiantado.
    if first_verse in (1, 2) and last_vn >= 5 and hc == chapter + 1:
        return advance_chapter(current, chapter, hc, expected)
    # Cabeçalho do capítulo seguinte sem número de versículo visível (título).
    if first_verse is None and last_vn >= 8 and hc == chapter + 1:
        return advance_chapter(current, chapter, hc, expected)
    if last_vn == 0 and 1 <= hc <= (expected.get(current, 0) or 0) + 1:
        return advance_chapter(current, chapter, hc, expected)
    return chapter


def parse_bible(vol_pages: dict[int, list]) -> Store:
    store = Store()
    current = None
    chapter = 0
    verse = 0
    last_vn = 0
    title = ""
    collecting = False
    header_chs: list[int] = []
    expected = {s: e for s, _n, _a, _t, e in BOOKS}

    def set_chapter(newc: int, collect: bool = True):
        nonlocal chapter, verse, last_vn, title, collecting
        if newc != chapter:
            last_vn = 0
            verse = 0
            title = ""
        chapter = newc
        collecting = collect
        if collect:
            verse = 0
            last_vn = 0
            title = ""

    pending_start = None

    for vol in range(1, 13):
        pages = vol_pages.get(vol) or []
        if vol not in VOLUME_CONTINUES:
            current = None
            set_chapter(0, True)
            header_chs = []
            pending_start = None
        for p in pages:
            page = p["page"]
            body = [clean(x) for x in p["body"] if clean(x)]
            if is_end_matter(body, page):
                break
            if is_front_matter(body):
                continue
            if (vol, page) in ANCHORS:
                nxt = ANCHORS[(vol, page)]
                if nxt != current:
                    current = nxt
                    set_chapter(0, True)
                    header_chs = []
                    pending_start = None
            if (vol, page) in CHAPTER_STARTS:
                pending_start = CHAPTER_STARTS[(vol, page)]
                current = pending_start[0]
            if looks_like_book_intro(body, current) and (vol, page) not in ANCHORS and (vol, page) not in CHAPTER_STARTS:
                current = None
                set_chapter(0, True)
                pending_start = None
                continue
            if not current or not body:
                continue
            page_notes = parse_notes(p["notes"])
            used_notes: set[int] = set()

            def notes_for(line: str) -> list[dict]:
                refs = [int(x) for x in RE_FN_INLINE.findall(line)]
                out = [{"n": n, "t": page_notes.get(n, "")} for n in refs if page_notes.get(n)]
                used_notes.update(x["n"] for x in out)
                return out

            page_last = last_vn
            for ln in reversed(body):
                vm = RE_VERSE.match(normalize_verse_prefix(ln))
                if vm:
                    page_last = int(vm.group(1))
                    break
            for nln in p.get("notes") or []:
                nln2 = normalize_verse_prefix(clean(nln))
                vm = RE_VERSE.match(nln2)
                if not vm:
                    continue
                vn = int(vm.group(1))
                rest = vm.group(2) or ""
                if not looks_like_scripture(rest):
                    continue
                if re.search(r"quilos|aproximadamente\s+\d|Tell-el-|2m,?\s*\d", rest, re.I):
                    continue
                if page_last and vn > page_last + 2 and vn > 5:
                    continue
                body.append(nln2)

            first = body[0]
            if is_running_header(first) and header_matches_book(first, current):
                header_chs = header_chapters(first, current, expected)
                first_v = peek_first_verse_num(body[1:])
                newc = apply_running_header(chapter, header_chs, first_v, last_vn, current, expected)
                if newc != chapter:
                    set_chapter(newc, False)
                body = body[1:]
            elif is_running_header(first):
                body = body[1:]

            if pending_start and pending_start[0] == current:
                want = pending_start[1]
                first_v = peek_first_verse_num(body)
                if first_v in (1, 2, 3) and chapter in (0, want - 1, want):
                    set_chapter(want, True)
                    pending_start = None
                elif chapter == want:
                    set_chapter(want, True)
                    pending_start = None

            j = 0
            while j < len(body):
                ln = body[j]
                if is_junk_line(ln):
                    j += 1
                    continue
                if is_running_header(ln):
                    if header_matches_book(ln, current):
                        chs = header_chapters(ln, current, expected)
                        first_v = peek_first_verse_num(body[j + 1 :])
                        newc = apply_running_header(chapter, chs, first_v, last_vn, current, expected)
                        if newc != chapter:
                            set_chapter(newc, False)
                        header_chs = chs or header_chs
                    j += 1
                    continue
                capn = parse_capitulo_num(ln)
                if capn is None and is_bare_capitulo(ln):
                    if pending_start and pending_start[0] == current:
                        capn = pending_start[1]
                    elif chapter:
                        capn = chapter + 1
                if capn is not None:
                    if pending_start and pending_start[0] == current:
                        want = pending_start[1]
                        if capn == want or capn == want - 9:
                            set_chapter(want, True)
                            pending_start = None
                            j += 1
                            continue
                    set_chapter(advance_chapter(current, chapter, capn, expected), True)
                    j += 1
                    continue
                sm = RE_SALMO.match(ln)
                if sm and current == "salmos":
                    digits = re.sub(r"\s+", "", sm.group(1))
                    if digits.isdigit():
                        hc = int(digits)
                        if pending_start and pending_start[0] == "salmos" and hc == pending_start[1]:
                            set_chapter(hc, True)
                            pending_start = None
                        else:
                            set_chapter(advance_chapter(current, chapter, hc, expected), True)
                    j += 1
                    continue
                # número isolado do capítulo + título em maiúsculas
                only = RE_VERSE_ONLY.match(ln)
                if only and j + 1 < len(body) and parse_capitulo_num(body[j + 1]) is not None:
                    j += 1
                    continue
                if only and j + 1 < len(body):
                    n = int(only.group(1))
                    nxt = body[j + 1]
                    if current and 1 <= n <= expected[current] + 1:
                        if looks_like_chapter_title(nxt) or (
                            n in (chapter, chapter + 1, max(chapter, 1))
                            and not RE_VERSE.match(nxt)
                            and not nxt[:1].isdigit()
                        ):
                            set_chapter(advance_chapter(current, chapter, n, expected) if chapter else n, True)
                            j += 1
                            continue
                ln = re.sub(r"^[\.\u2013\u2014]\s+", "", ln)
                if last_vn == 7:
                    ln = re.sub(r"^[S&]\s+(?=[A-ZÁÉÍÓÚÀÂÃÄÊÔÕÜ])", "8 ", ln)
                ln = normalize_verse_prefix(ln)
                # número no meio de um título em maiúsculas (ex. "34. DESTE SALMO...")
                if collecting:
                    stripped = re.sub(r"^\d{1,3}[.\-:]?\s+", "", ln)
                    if stripped != ln and looks_like_chapter_title(stripped):
                        title = (title + " " + stripped).strip()
                        j += 1
                        continue
                vm = RE_VERSE.match(ln)
                if vm:
                    rest = (vm.group(2) or "").strip()
                    verse_n = int(vm.group(1))
                    if is_junk_line(rest) or (is_running_header(ln) and header_matches_book(ln, current)):
                        j += 1
                        continue
                    if verse_n == chapter and len(rest) <= 4:
                        j += 1
                        continue
                    if last_vn == 0 and 10 <= verse_n <= 19 and str(verse_n).startswith("1"):
                        verse_n = 1
                    if chapter == 0 and verse_n == 1:
                        set_chapter(1, False)
                    newc = maybe_wrap_chapter(current, chapter, verse_n, last_vn, header_chs, expected, rest)
                    if newc != chapter:
                        set_chapter(newc, False)
                    if not looks_like_scripture(rest) and len(rest) < 40:
                        j += 1
                        continue
                    collecting = False
                    verse = verse_n
                    last_vn = verse
                    store.add(current, chapter or 1, verse, rest, title, notes_for(ln))
                    title = ""
                    j += 1
                    continue
                if RE_VERSE_ONLY.match(ln) and j + 1 < len(body):
                    nxt = body[j + 1]
                    if looks_like_chapter_title(nxt):
                        n = int(re.match(r"(\d{1,3})", ln).group(1))
                        if current and 1 <= n <= expected[current] + 1:
                            set_chapter(advance_chapter(current, chapter, n, expected) if chapter else n, True)
                        j += 1
                        continue
                    if not RE_VERSE.match(nxt) and not is_junk_line(nxt):
                        collecting = False
                        verse_n = int(re.match(r"(\d{1,3})", ln).group(1))
                        if last_vn == 0 and 10 <= verse_n <= 19 and str(verse_n).startswith("1"):
                            verse_n = 1
                        if chapter == 0 and verse_n == 1:
                            set_chapter(1, False)
                        newc = maybe_wrap_chapter(current, chapter, verse_n, last_vn, header_chs, expected, nxt)
                        if newc != chapter:
                            set_chapter(newc, False)
                        verse = verse_n
                        last_vn = verse
                        store.add(current, chapter or 1, verse, nxt, title, notes_for(nxt))
                        title = ""
                        j += 2
                        continue
                if collecting and looks_like_chapter_title(ln) and not ln[:1].isdigit():
                    title = (title + " " + ln).strip()
                    j += 1
                    continue
                if collecting and chapter and not verse and not looks_like_chapter_title(ln) and not parse_capitulo_num(ln) and not ln[:1].isdigit() and len(ln) > 18:
                    collecting = False
                    verse = 1
                    last_vn = 1
                    store.add(current, chapter, 1, ln, title, notes_for(ln))
                    title = ""
                    j += 1
                    continue
                if current and chapter and not verse and not collecting:
                    if len(ln) > 18 and not looks_like_chapter_title(ln) and not parse_capitulo_num(ln):
                        verse = 1
                        last_vn = 1
                        store.add(current, chapter, 1, ln, title, notes_for(ln))
                        title = ""
                        j += 1
                        continue
                if verse and current and not collecting and not is_junk_line(ln) and not is_running_header(ln):
                    store.add(current, chapter or 1, verse, ln, "", notes_for(ln))
                j += 1
            leftover = [{"n": n, "t": t} for n, t in sorted(page_notes.items()) if n not in used_notes]
            if leftover and current and chapter and last_vn:
                store.add_notes(current, chapter, last_vn, leftover)
    return store


def parse_dictionary(pages: list[dict]) -> list[dict]:
    entries = []
    lemma = ""
    buf = []
    def flush():
        nonlocal lemma, buf
        txt = normalize_body(" ".join(buf))
        if lemma and len(txt) > 20:
            entries.append({"lemma": lemma, "t": txt})
        lemma, buf = "", []

    for p in pages:
        if p["page"] < 8:
            continue
        if any(RE_INDEX.search(x) for x in p["body"][:4]) and p["page"] > 300:
            break
        for ln in p["body"] + p["notes"]:
            ln = clean(ln)
            if not ln or RE_PAGE_NUM.match(ln):
                continue
            # verbete: linha curta em maiusculas
            letters = re.sub(r"[^A-Za-zÀ-ÿ]", "", ln)
            if letters and letters == letters.upper() and 3 <= len(ln) <= 48 and not ln[:1].isdigit():
                flush()
                lemma = ln.title()
                continue
            if lemma:
                buf.append(ln)
    flush()
    return entries


def parse_intro(pages: list[dict], titulo: str) -> dict:
    paras = []
    buf = []
    for p in pages:
        if p["page"] < 6:
            continue
        if any(RE_INDEX.search(x) for x in p["body"][:4]) and p["page"] > 400:
            break
        for ln in p["body"]:
            ln = clean(ln)
            if not ln or RE_PAGE_NUM.match(ln) or "BIBLIA" in fold(ln)[:20]:
                continue
            if ln.endswith("-") or ln.endswith("\u00ad"):
                buf.append(ln[:-1])
                continue
            buf.append(ln)
            if ln.endswith(".") and sum(len(x) for x in buf) > 180:
                paras.append(normalize_body(" ".join(buf)))
                buf = []
    if buf:
        paras.append(normalize_body(" ".join(buf)))
    return {"id": titulo, "titulo": titulo, "paragrafos": paras}


def export_all(store: Store, dicionario, intros):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "livros").mkdir(exist_ok=True)
    catalog = []
    total_v = 0
    total_n = 0
    search = []

    for slug, nome, abbrev, test, expected in BOOKS:
        nome = DISPLAY.get(slug, nome)
        meta = store.books[slug]
        caps = []
        vc = 0
        nc = 0
        miss = []
        for n in range(1, expected + 1):
            ch = meta["caps"].get(n)
            if not ch or not ch["v"]:
                miss.append(n)
                caps.append({"n": n, "titulo": "", "versiculos": []})
                continue
            verses = []
            for vn in sorted(ch["v"]):
                item = ch["v"][vn]
                notas = [x for x in item.get("notas", []) if x.get("t")]
                verses.append({"n": vn, "t": item["t"], "notas": notas})
                vc += 1
                nc += len(notas)
                search.append({
                    "b": slug, "n": nome, "a": abbrev, "c": n, "v": vn,
                    "t": item["t"], "k": "verso",
                })
                for note in notas:
                    search.append({
                        "b": slug, "n": nome, "a": abbrev, "c": n, "v": vn,
                        "t": note["t"], "k": "nota",
                    })
            caps.append({"n": n, "titulo": ch.get("titulo") or "", "versiculos": verses})
        payload = {
            "id": slug, "nome": nome, "abbrev": abbrev,
            "testamento": test, "capitulos": caps,
        }
        (OUT / "livros" / f"{slug}.json").write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        catalog.append({
            "id": slug, "nome": nome, "abbrev": abbrev, "testamento": test,
            "capitulos": expected, "versiculos": vc, "notas": nc,
        })
        total_v += vc
        total_n += nc
        print(f"{nome:24} {expected-len(miss):3}/{expected:<3} v={vc:4} notas={nc:4} miss={miss[:10]}")

    (OUT / "catalog.json").write_text(
        json.dumps({
            "traducao": "Figueiredo",
            "ano": 1950,
            "fonte": "documentos/",
            "canone": "Catolico Romano (73 livros)",
            "livros": catalog,
            "versiculos": total_v,
            "notas": total_n,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT / "dicionario.json").write_text(
        json.dumps({"fonte": "volume 13", "verbetes": dicionario}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    (OUT / "introducoes.json").write_text(
        json.dumps(intros, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    for item in dicionario:
        search.append({"b": "dicionario", "n": "Dicionario", "a": "Dic", "c": 0, "v": 0, "t": item["lemma"] + " — " + item["t"][:500], "k": "dicionario"})
    (OUT / "search.json").write_text(
        json.dumps(search, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"\nTOTAL versos={total_v} notas={total_n} verbetes={len(dicionario)} search={len(search)}")
    copy_to_web()


def copy_to_web():
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    (WEB_DATA / "livros").mkdir(exist_ok=True)
    WEB_PUBLIC.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT / "catalog.json", WEB_DATA / "catalog.json")
    shutil.copy2(OUT / "catalog.json", WEB_PUBLIC / "catalog.json")
    shutil.copy2(OUT / "search.json", WEB_PUBLIC / "search.json")
    shutil.copy2(OUT / "dicionario.json", WEB_DATA / "dicionario.json")
    shutil.copy2(OUT / "dicionario.json", WEB_PUBLIC / "dicionario.json")
    shutil.copy2(OUT / "introducoes.json", WEB_DATA / "introducoes.json")
    for f in (OUT / "livros").glob("*.json"):
        shutil.copy2(f, WEB_DATA / "livros" / f.name)
    print("copiado para web/data e web/public/data")


def main():
    mapping, skip = find_pdfs()
    print("PDFs Figueiredo:", sorted(mapping))
    print("Outros (nao republicados por direitos de autor):", skip)
    vol_pages = {}
    for vol in range(1, 17):
        if vol not in mapping:
            print("FALTA volume", vol)
            continue
        print("Extraindo volume", vol, mapping[vol].name[:70])
        vol_pages[vol] = extract_volume(vol, mapping[vol])
    store = parse_bible(vol_pages)
    dicionario = parse_dictionary(vol_pages.get(13, []))
    intros = [
        parse_intro(vol_pages.get(14, []), "Introducao geral I"),
        parse_intro(vol_pages.get(15, []), "Introducao geral II"),
        parse_intro(vol_pages.get(16, []), "Introducao geral III"),
    ]
    export_all(store, dicionario, intros)


if __name__ == "__main__":
    main()
