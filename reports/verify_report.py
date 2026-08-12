# -*- coding: utf-8 -*-
"""Checks the built report against the template's mandatory requirements.

Verifies: guidance notes removed, per-section word budgets, figure/table caption
numbering, embedded images, and that no first-person pronouns slipped in.
"""
import os
import re
import sys
import zipfile
import docx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import report_content as C

PATH = os.path.join(HERE, f"{C.AUTHOR.replace(' ', '_')}_MSc_Project_Report.docx")

LIMITS = {
    'Abstract': 500,
    'Introduction': 1000,
    'Literature – Technology Review': 1500,
    'Implementation': 3000,
    'Evaluation and Results': 2000,
    'Conclusion': 1500,
}
# headings that close a counted section without opening a new counted one
STOP = {'References', 'Appendix A: Project Proposal'}

d = docx.Document(PATH)

# ---- guidance notes -------------------------------------------------------
leftover = [p.text.strip()[:70] for p in d.paragraphs
            if p.style.name == 'Guidance notes' and p.text.strip()]
print(f'guidance-note paragraphs remaining : {len(leftover)}')
for t in leftover[:5]:
    print('   !', t)

placeholders = [p.text.strip() for p in d.paragraphs
                if re.fullmatch(r'insert\s+(your\s+)?text\s+here[.:]?',
                                p.text.strip(), re.I)]
print(f'"insert text here" placeholders    : {len(placeholders)}')

# ---- word counts per section ---------------------------------------------
counts, current = {}, None
for p in d.paragraphs:
    s, t = p.style.name, p.text.strip()
    if s in ('Heading 1', 'Heading back matter'):
        key = t.replace('—', '–').strip()
        current = key if (key in LIMITS or key in STOP) else (
            current if key not in STOP else None)
        if key in LIMITS:
            counts.setdefault(key, 0)
        elif key in STOP:
            current = None
        continue
    if current in LIMITS and s in ('Normal', 'Heading 2', 'Body Text'):
        counts[current] = counts.get(current, 0) + len(t.split())

print('\nsection word counts (body text, excluding tables and captions):')
total = 0
for k, lim in LIMITS.items():
    n = counts.get(k, 0)
    if k != 'Abstract':
        total += n
    flag = 'OVER' if n > lim else 'ok'
    print(f'  {k:34s} {n:5d} / {lim:5d}   {flag}')
print(f'  {"MAIN BODY TOTAL (excl. abstract)":34s} {total:5d} / 10000')

# ---- captions -------------------------------------------------------------
caps = [p.text.strip() for p in d.paragraphs if p.style.name == 'Caption']
figs = [c for c in caps if c.startswith('Figure')]
tabs = [c for c in caps if c.startswith('Table')]
print(f'\nfigure captions: {len(figs)}   table captions: {len(tabs)}')
for c in figs + tabs:
    print('   ', c[:88])

# ---- embedded media -------------------------------------------------------
with zipfile.ZipFile(PATH) as z:
    media = [n for n in z.namelist() if n.startswith('word/media/')]
    rels = z.read('word/_rels/document.xml.rels').decode('utf-8')
    doc_xml = z.read('word/document.xml').decode('utf-8')
print(f'\nembedded media files: {len(media)}')
missing_rel = [m.split("/")[-1] for m in media
               if m.split("/")[-1] not in rels]
print(f'media without a relationship entry: {missing_rel}')
print(f'drawing elements in document.xml  : {doc_xml.count("<w:drawing>")}')
print(f'tables in document.xml            : {doc_xml.count("<w:tbl>")}')

# ---- first person ---------------------------------------------------------
BAD = re.compile(r'\b(I|we|my|our|us|me|I\'ve|we\'ve|I\'m)\b')
hits = []
for p in d.paragraphs:
    if p.style.name in ('Normal', 'Heading 2', 'Body Text'):
        for m in BAD.finditer(p.text):
            hits.append((m.group(0), p.text.strip()[:75]))
print(f'\nfirst-person hits: {len(hits)}')
for w, t in hits[:10]:
    print(f'   [{w}] {t}')

# ---- references -----------------------------------------------------------
body = '\n'.join(p.text for p in d.paragraphs)
cited = sorted({int(n) for n in re.findall(r'\[(\d{1,2})\]', body)})
print(f'\nreference entries: {len(C.REFERENCES)}')
print(f'citation markers used: {cited}')
uncited = [i for i in range(1, len(C.REFERENCES) + 1) if i not in cited]
print(f'never cited in text: {uncited}')
