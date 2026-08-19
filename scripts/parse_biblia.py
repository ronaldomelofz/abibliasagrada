# -*- coding: utf-8 -*-
from __future__ import annotations
import json, re, unicodedata
from pathlib import Path

EXTRACT = Path(r'E:\\PROJETOS-CURSOR\\BIBLIA\\_extract')
OUT = Path(r'E:\\PROJETOS-CURSOR\\BIBLIA\\data')

def u(*codes):
    return ''.join(chr(c) if isinstance(c, int) else c for c in codes)

GENESIS = 'G' + '\u00ea' + 'nesis'
EXODO = '\u00ca' + 'xodo'
LEV = 'Lev' + '\u00ed' + 'tico'
NUM = 'N' + '\u00fa' + 'meros'
DEUT = 'Deuteron' + '\u00f4' + 'mio'
JOS = 'Josu' + '\u00e9'
JUI = 'Ju' + '\u00ed' + 'zes'
PAR = 'Paralip' + '\u00f4' + 'menos'
JO = 'J' + '\u00f3'
PROV = 'Prov' + '\u00e9' + 'rbios'
CANT = 'C' + '\u00e2' + 'ntico dos C' + '\u00e2' + 'nticos'
ECLO = 'Eclesi' + '\u00e1' + 'stico'
ISA = 'Isa' + '\u00ed' + 'as'
LAM = 'Lamenta' + '\u00e7' + '\u00f5' + 'es'
OSE = 'Os' + '\u00e9' + 'ias'
AMOS = 'Am' + '\u00f3' + 's'
MIQ = 'Miqu' + '\u00ea' + 'ias'
JOAO = 'Jo' + '\u00e3' + 'o'
COR = 'Cor' + '\u00ed' + 'ntios'
EFE = 'Ef' + '\u00e9' + 'sios'
GAL = 'G' + '\u00e1' + 'latas'
FIL = 'Fil' + '\u00ea' + 'mon'
APO = 'Ap' + '\u00f3' + 'stolos'

BOOKS = [
    ('genesis', GENESIS, 'Gn', 'at', 50),
    ('exodo', EXODO, 'Ex', 'at', 40),
    ('levitico', LEV, 'Lv', 'at', 27),
    ('numeros', NUM, 'Nm', 'at', 36),
    ('deuteronomio', DEUT, 'Dt', 'at', 34),
    ('josue', JOS, 'Js', 'at', 24),
    ('juizes', JUI, 'Jz', 'at', 21),
    ('rute', 'Rute', 'Rt', 'at', 4),
    ('1-samuel', 'I Samuel', '1Sm', 'at', 31),
    ('2-samuel', 'II Samuel', '2Sm', 'at', 24),
    ('1-reis', 'I Reis', '1Rs', 'at', 22),
    ('2-reis', 'II Reis', '2Rs', 'at', 25),
    ('1-cronicas', 'I ' + PAR, '1Cr', 'at', 29),
    ('2-cronicas', 'II ' + PAR, '2Cr', 'at', 36),
    ('esdras', 'Esdras', 'Esd', 'at', 10),
    ('neemias', 'Neemias', 'Ne', 'at', 13),
    ('tobias', 'Tobias', 'Tb', 'at', 14),
    ('judite', 'Judite', 'Jt', 'at', 16),
    ('ester', 'Ester', 'Est', 'at', 16),
    ('jo', JO, 'Jo', 'at', 42),
    ('salmos', 'Salmos', 'Sl', 'at', 150),
    ('proverbios', PROV, 'Pr', 'at', 31),
    ('eclesiastes', 'Eclesiastes', 'Ecl', 'at', 12),
    ('cantico', CANT, 'Ct', 'at', 8),
    ('sabedoria', 'Sabedoria', 'Sb', 'at', 19),
    ('eclesiastico', ECLO, 'Eclo', 'at', 51),
    ('isaias', ISA, 'Is', 'at', 66),
    ('jeremias', 'Jeremias', 'Jr', 'at', 52),
    ('lamentacoes', LAM, 'Lm', 'at', 5),
    ('baruc', 'Baruc', 'Br', 'at', 6),
    ('ezequiel', 'Ezequiel', 'Ez', 'at', 48),
    ('daniel', 'Daniel', 'Dn', 'at', 14),
    ('oseias', OSE, 'Os', 'at', 14),
    ('joel', 'Joel', 'Jl', 'at', 3),
    ('amos', AMOS, 'Am', 'at', 9),
    ('abdias', 'Abdias', 'Ab', 'at', 1),
    ('jonas', 'Jonas', 'Jn', 'at', 4),
    ('miqueias', MIQ, 'Mq', 'at', 7),
    ('naum', 'Naum', 'Na', 'at', 3),
    ('habacuc', 'Habacuc', 'Hab', 'at', 3),
    ('sofonias', 'Sofonias', 'Sf', 'at', 3),
    ('ageu', 'Ageu', 'Ag', 'at', 2),
    ('zacarias', 'Zacarias', 'Zc', 'at', 14),
    ('malaquias', 'Malaquias', 'Ml', 'at', 4),
    ('1-macabeus', 'I Macabeus', '1Mc', 'at', 16),
    ('2-macabeus', 'II Macabeus', '2Mc', 'at', 15),
    ('mateus', 'Mateus', 'Mt', 'nt', 28),
    ('marcos', 'Marcos', 'Mc', 'nt', 16),
    ('lucas', 'Lucas', 'Lc', 'nt', 24),
    ('joao', JOAO, 'Jo', 'nt', 21),
    ('atos', 'Atos dos ' + APO, 'At', 'nt', 28),
    ('romanos', 'Romanos', 'Rm', 'nt', 16),
    ('1-corintios', 'I ' + COR, '1Cor', 'nt', 16),
    ('2-corintios', 'II ' + COR, '2Cor', 'nt', 13),
    ('galatas', GAL, 'Gl', 'nt', 6),
    ('efesios', EFE, 'Ef', 'nt', 6),
    ('filipenses', 'Filipenses', 'Fl', 'nt', 4),
    ('colossenses', 'Colossenses', 'Cl', 'nt', 4),
    ('1-tessalonicenses', 'I Tessalonicenses', '1Ts', 'nt', 5),
    ('2-tessalonicenses', 'II Tessalonicenses', '2Ts', 'nt', 3),
    ('1-timoteo', 'I Tim' + '\u00f3' + 'teo', '1Tm', 'nt', 6),
    ('2-timoteo', 'II Tim' + '\u00f3' + 'teo', '2Tm', 'nt', 4),
    ('tito', 'Tito', 'Tt', 'nt', 3),
    ('filemom', FIL, 'Fm', 'nt', 1),
    ('hebreus', 'Hebreus', 'Hb', 'nt', 13),
    ('tiago', 'Tiago', 'Tg', 'nt', 5),
    ('1-pedro', 'I Pedro', '1Pd', 'nt', 5),
    ('2-pedro', 'II Pedro', '2Pd', 'nt', 3),
    ('1-joao', 'I ' + JOAO, '1Jo', 'nt', 5),
    ('2-joao', 'II ' + JOAO, '2Jo', 'nt', 1),
    ('3-joao', 'III ' + JOAO, '3Jo', 'nt', 1),
    ('judas', 'Judas', 'Jd', 'nt', 1),
    ('apocalipse', 'Apocalipse', 'Ap', 'nt', 22),
]

ANCHORS = {
    (1,29):'genesis',(1,219):'exodo',(1,375):'levitico',
    (2,5):'numeros',(2,145):'deuteronomio',(2,273):'josue',(2,357):'juizes',(2,446):'rute',
    (3,9):'1-samuel',(3,117):'2-samuel',(3,205):'1-reis',(3,308):'2-reis',(3,411):'1-cronicas',
    (4,5):'2-cronicas',(4,121):'esdras',(4,155):'neemias',(4,205):'tobias',(4,241):'judite',(4,287):'ester',(4,337):'jo',
    (5,17):'salmos',(5,381):'proverbios',
    (6,5):'proverbios',(6,53):'eclesiastes',(6,87):'cantico',(6,123):'sabedoria',(6,191):'eclesiastico',(6,391):'isaias',
    (7,205):'jeremias',(7,413):'lamentacoes',
    (8,13):'baruc',(8,45):'ezequiel',(8,261):'daniel',(8,345):'oseias',
    (9,7):'joel',(9,21):'amos',(9,41):'abdias',(9,51):'jonas',(9,61):'miqueias',(9,79):'naum',(9,89):'habacuc',(9,101):'sofonias',(9,113):'ageu',(9,123):'zacarias',(9,161):'malaquias',(9,177):'1-macabeus',(9,291):'2-macabeus',
    (10,21):'mateus',(10,197):'marcos',(10,287):'lucas',
    (11,21):'joao',(11,161):'atos',(11,317):'romanos',(11,389):'1-corintios',
    (12,7):'2-corintios',(12,49):'galatas',(12,71):'efesios',(12,95):'filipenses',(12,111):'colossenses',(12,127):'1-tessalonicenses',(12,141):'2-tessalonicenses',(12,153):'1-timoteo',(12,177):'2-timoteo',(12,191):'tito',(12,203):'filemom',(12,215):'hebreus',(12,271):'tiago',(12,297):'1-pedro',(12,319):'2-pedro',(12,333):'1-joao',(12,351):'2-joao',(12,357):'3-joao',(12,363):'judas',(12,373):'apocalipse',
}

HEADER = [
    ('genesis', r'^G[e\u00e9\u00ea]nesis\b'),
    ('exodo', r'^[\u00caE]xodo\b'),
    ('levitico', r'^Lev[i\u00ed]tico\b'),
    ('numeros', r'^N[u\u00fa]meros\b'),
    ('deuteronomio', r'^Deuteron'),
    ('josue', r'^Josu[e\u00e9]\b'),
    ('juizes', r'^Ju[i\u00ed]zes\b'),
    ('rute', r'^Rute\b'),
    ('1-samuel', r'^(?:1|I)\s*(?:Reis|Samuel)\b'),
    ('2-samuel', r'^(?:2|II)\s*(?:Reis|Samuel)\b'),
    ('1-reis', r'^(?:3|III)\s*Reis\b'),
    ('2-reis', r'^(?:4|IV)\s*Reis\b'),
    ('1-cronicas', r'^(?:1|I)\s*Paralip'),
    ('2-cronicas', r'^(?:2|II)\s*Paralip'),
    ('esdras', r'^Esdras\b'),
    ('neemias', r'^Neemias\b'),
    ('tobias', r'^Tobias\b'),
    ('judite', r'^Judite\b'),
    ('ester', r'^Ester\b'),
    ('jo', r'^J[\u00f3o]\s+\d'),
    ('salmos', r'^Salmo(?:s)?\b'),
    ('proverbios', r'^Prov[e\u00e9]rbios\b'),
    ('eclesiastes', r'^Eclesiastes\b'),
    ('cantico', r'^C[\u00e2a]ntico'),
    ('sabedoria', r'^Sabedoria\b'),
    ('eclesiastico', r'^Eclesi[\u00e1a]stico\b'),
    ('isaias', r'^Isa[i\u00ed]as\b'),
    ('jeremias', r'^Jeremias\b'),
    ('lamentacoes', r'^Lamenta'),
    ('baruc', r'^Baruc\b'),
    ('ezequiel', r'^Ezequiel\b'),
    ('daniel', r'^Daniel\b'),
    ('oseias', r'^Os[e\u00e9]ias\b'),
    ('joel', r'^Joel\b'),
    ('amos', r'^Am[o\u00f3]s\b'),
    ('abdias', r'^Abd[i\u00ed]as\b'),
    ('jonas', r'^Jonas\b'),
    ('miqueias', r'^Miqu[e\u00ea]ias\b'),
    ('naum', r'^Naum\b'),
    ('habacuc', r'^Habacuc\b'),
    ('sofonias', r'^Sofonias\b'),
    ('ageu', r'^Ageu\b'),
    ('zacarias', r'^Zacarias\b'),
    ('malaquias', r'^Malaquias\b'),
    ('1-macabeus', r'^(?:1|I)\s*Macabeus\b'),
    ('2-macabeus', r'^(?:2|II)\s*Macabeus\b'),
    ('mateus', r'(?:Evangelho\s+de\s+S\.?\s*)?Mateus\b'),
    ('marcos', r'(?:Evangelho\s+de\s+S\.?\s*)?Marcos\b'),
    ('lucas', r'(?:Evangelho\s+de\s+S\.?\s*)?Lucas\b'),
    ('joao', r'(?:Evangelho\s+de\s+S\.?\s*)?Jo[\u00e3a]o\b'),
    ('atos', r'^Atos\b'),
    ('romanos', r'^Romanos\b'),
    ('1-corintios', r'^(?:1|I)\s*Cor'),
    ('2-corintios', r'^(?:2|II)\s*Cor'),
    ('galatas', r'^G[a\u00e1]latas\b'),
    ('efesios', r'^Ef[e\u00e9]sios\b'),
    ('filipenses', r'^Filipenses\b'),
    ('colossenses', r'^Colossenses\b'),
    ('1-tessalonicenses', r'^(?:1|I)\s*Tessal'),
    ('2-tessalonicenses', r'^(?:2|II)\s*Tessal'),
    ('1-timoteo', r'^(?:1|I)\s*Tim'),
    ('2-timoteo', r'^(?:2|II)\s*Tim'),
    ('tito', r'^Tito\b'),
    ('filemom', r'^Fil[e\u00ea]mon\b'),
    ('hebreus', r'^Hebreus\b'),
    ('tiago', r'^Tiago\b'),
    ('1-pedro', r'^(?:1|I)\s*Pedro'),
    ('2-pedro', r'^(?:2|II)\s*Pedro'),
    ('1-joao', r'^(?:1|I)\s*Jo[\u00e3a]o'),
    ('2-joao', r'^(?:2|II)\s*Jo[\u00e3a]o'),
    ('3-joao', r'^(?:3|III)\s*Jo[\u00e3a]o'),
    ('judas', r'^Judas\b'),
    ('apocalipse', r'^Apocalipse\b'),
]
HEADER = [(s, re.compile(p, re.I)) for s,p in HEADER]

RE_PAGE_NUM = re.compile(r'^[\-\u2014\u2013]?\s*\d{1,3}\s*[\-\u2014\u2013]?\s*$')
RE_FN = re.compile(r'^\(\s*\d+\s*\)\s*$|^\(\s*\d+\s*\)\s+\S|^\(\*\)\s*$')
RE_CH = re.compile(r'Cap[i\u00ed]tulo\s+(\d{1,3})|CAP[I\u00cd]TULO\s+(\d{1,3})', re.I)
RE_SALMO = re.compile(r'^Salmo\s+(\d{1,3})\b', re.I)
RE_VERSE = re.compile(r'^(\d{1,3})[.\-:\u2013\u2014]?\s+(.*\S.*)$')
RE_VERSE_ONLY = re.compile(r'^(\d{1,3})\s*[.\-:]?\s*$')
RE_RUNNING = re.compile(r'(Mateus|Marcos|Lucas|Jo[\u00e3a]o|Atos|Romanos|G[e\u00e9\u00ea]nesis|Exodo|Salmo)', re.I)
RE_CAPS = re.compile(r'^[A-Z\u00c0-\u00dc]{3,}.*')
RE_INDEX = re.compile(r'INDICE|I N D I C E', re.I)

def fold(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c)).upper()

def clean(s):
    return re.sub(r'[ \t]+', ' ', s.replace('\u00ad','').replace('\xa0',' ')).strip()

def is_noise(ln):
    if not ln or RE_PAGE_NUM.match(ln): return True
    u = fold(ln)
    if 'BIBLIA SAGRADA' in u or u.startswith('ANO SANTO'): return True
    if 'EDITORA CUPOLO' in u or 'NIHIL OBSTAT' in u: return True
    if ln in {'.','-','\u2014','*','\u2605'}: return True
    return False

def normalize(text):
    text = text.replace('\u00ad','')
    text = re.sub(r'\(\s*\d+\s*\)', '', text)
    text = re.sub(r'\(\*\)', '', text)
    text = re.sub(r'\bd,e\b','de', text)
    text = re.sub(r'\bd,o\b','do', text)
    text = re.sub(r'\bd,a\b','da', text)
    text = re.sub(r'\bn,o\b','no', text)
    text = re.sub(r'\s+', ' ', text)
    return text.replace(' ,',',').replace(' .','.').strip(' -\u2014')

class Store:
    def __init__(self):
        self.books = {s:{'nome':n,'abbrev':a,'testamento':t,'esperado':e,'caps':{}} for s,n,a,t,e in BOOKS}
    def add(self, slug, ch, vn, text, titulo=''):
        if not slug or not ch or not vn: return
        meta = self.books[slug]
        if ch<1 or ch>meta['esperado']+3 or vn<1 or vn>180: return
        text = normalize(text)
        if len(text)<2: return
        cap = meta['caps'].setdefault(ch, {'titulo':'', 'v':{}})
        if titulo and not cap['titulo']:
            cap['titulo'] = titulo.title()
        prev = cap['v'].get(vn,'')
        if len(text) > len(prev):
            cap['v'][vn] = text
    def append(self, slug, ch, vn, extra):
        extra = normalize(extra)
        if not extra or not slug: return
        cap = self.books[slug]['caps'].get(ch)
        if not cap or vn not in cap['v']: return
        cap['v'][vn] = normalize(cap['v'][vn] + ' ' + extra)

def parse():
    store = Store()
    current = None
    chapter = 0
    verse = 0
    title = ''
    collecting = False
    expected = {s:e for s,_,_,_,e in BOOKS}
    for vol in range(1,13):
        raw = (EXTRACT / f'vol_{vol:02d}.txt').read_text(encoding='utf-8')
        chunks = re.split(r'\n===== PAGE (\d+) =====\n', raw)
        i = 1
        while i < len(chunks)-1:
            page = int(chunks[i]); content = chunks[i+1]; i += 2
            lines = [clean(x) for x in content.splitlines() if clean(x)]
            if any(RE_INDEX.search(x) for x in lines[:6]) and page>300:
                break
            if any('GRAVURAS' in fold(x) for x in lines[:8]) and page > 350:
                break
            if (vol,page) in ANCHORS:
                nxt = ANCHORS[(vol,page)]
                if nxt != current:
                    current = nxt
                    chapter = 1
                    verse = 0
                    title = ''
                    collecting = True
            body = []
            for ln in lines:
                if RE_FN.match(ln):
                    break
                if ln.startswith('(*)') and len(body)>3:
                    break
                if not is_noise(ln):
                    body.append(ln)
            if not body or not current:
                continue
            # running header
            first = body[0]
            for slug, rx in HEADER:
                if rx.search(first) and re.search(r'\d{1,3}\s*,', first):
                    body = body[1:]
                    m = re.search(r'(\d{1,3})', first)
                    if slug == current and m:
                        hc = int(m.group(1))
                        if 1 <= hc <= expected[current]+1 and hc != chapter:
                            chapter = hc
                            verse = 0
                            collecting = False
                    break
            j = 0
            while j < len(body):
                ln = body[j]
                if re.search(r'\d{1,3}\s*,\s*\d', ln) and len(ln) < 48:
                    j += 1
                    continue
                folded_sp = re.sub(r'\s+','',fold(ln))
                cm = RE_CH.search(ln) or (re.search(r'CAPITULO(\d{1,3})', folded_sp))
                if cm:
                    num = cm.group(1) or (cm.group(2) if cm.lastindex and cm.lastindex>=2 else None)
                    if not num:
                        mm = re.search(r'(\d{1,3})', ln)
                        num = mm.group(1) if mm else None
                    if num:
                        chapter = int(num)
                        verse = 0
                        collecting = True
                        title = ''
                        j += 1
                        continue
                sm = RE_SALMO.match(ln)
                if sm and current=='salmos':
                    chapter = int(sm.group(1)); verse=0; collecting=True; title=''; j+=1; continue
                vm = RE_VERSE.match(ln)
                if vm:
                    collecting=False
                    verse=int(vm.group(1))
                    store.add(current, chapter or 1, verse, vm.group(2), title)
                    title=''; j+=1; continue
                if RE_VERSE_ONLY.match(ln) and j+1 < len(body):
                    nxt=body[j+1]
                    if not RE_VERSE.match(nxt):
                        collecting=False
                        verse=int(re.match(r'(\d{1,3})', ln).group(1))
                        store.add(current, chapter or 1, verse, nxt, title)
                        title=''; j+=2; continue
                if collecting and ln == fold(ln) and len(ln)>8 and not ln[0].isdigit():
                    title = (title+' '+ln).strip(); j+=1; continue
                if verse and current and not collecting:
                    store.append(current, chapter or 1, verse, ln)
                j += 1
    return store

def export(store):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'livros').mkdir(exist_ok=True)
    catalog=[]; total=0
    for slug,nome,abbrev,test,expected in BOOKS:
        meta=store.books[slug]
        caps=[]; vc=0; miss=[]
        for n in range(1, expected+1):
            ch=meta['caps'].get(n)
            if not ch or not ch['v']:
                miss.append(n)
                caps.append({'n':n,'titulo':'','versiculos':[]})
                continue
            verses=[{'n':k,'t':ch['v'][k]} for k in sorted(ch['v'])]
            vc += len(verses)
            caps.append({'n':n,'titulo':ch.get('titulo') or '','versiculos':verses})
        payload={'id':slug,'nome':nome,'abbrev':abbrev,'testamento':test,'capitulos':caps}
        (OUT/'livros'/f'{slug}.json').write_text(json.dumps(payload, ensure_ascii=False, separators=(',',':')), encoding='utf-8')
        catalog.append({'id':slug,'nome':nome,'abbrev':abbrev,'testamento':test,'capitulos':expected,'versiculos':vc})
        total += vc
        print(f'{nome:24} {expected-len(miss):3}/{expected:<3} v={vc:4} miss={miss[:15]}')
    (OUT/'catalog.json').write_text(json.dumps({'traducao':'Figueiredo','ano':1950,'livros':catalog}, ensure_ascii=False, indent=2), encoding='utf-8')
    print('TOTAL', total)
    print('vazios', [c['nome'] for c in catalog if c['versiculos']<8])

if __name__=='__main__':
    export(parse())
