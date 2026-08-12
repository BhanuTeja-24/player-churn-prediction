# -*- coding: utf-8 -*-
"""Builds the churn-prediction dissertation into the university template.

Mechanism adapted from the previously-working build used for another project on
this machine: parse word/document.xml at paragraph level, drop the blue guidance
notes and placeholders, then splice content in after each matching heading. The
template's own styles are never touched, so the mandated fonts, spacing, margins
and justification are inherited rather than re-applied.

Differences from the earlier version:
  * tables are supplied inline from report_content.TABLES (curated for print)
    rather than dumped from raw result CSVs, which carry far too many columns
  * figures are pulled straight from the pipeline's outputs/figures directory
"""
import re
import os
import sys
import shutil
import zipfile
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import report_content as C

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)

TEMPLATE = r'D:\Final year project\Report\MSc Project Report Template.docx'
FIGDIR = os.path.join(PROJECT, 'outputs', 'figures')
OUT = os.path.join(HERE, f"{C.AUTHOR.replace(' ', '_')}_MSc_Project_Report.docx")

EMU_PER_IN = 914400
MAX_W_IN = 5.9          # usable width inside the template's margins

_media = []             # (filename, bytes) queued for word/media/
_rels = []              # (rId, target) relationship entries for those images
_fig_n = [0]
_tab_n = [0]


def para(text, style='Normal'):
    return (f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
            f'<w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')


def figure(fname, caption):
    """Inline image plus a numbered caption driven by a real SEQ field.

    The SEQ field matters: a caption typed as plain text will not be picked up
    by the template's automatic List of Figures.
    """
    from PIL import Image
    src = os.path.join(FIGDIR, fname)
    with Image.open(src) as im:
        pw, ph = im.size
    w_in = MAX_W_IN
    h_in = MAX_W_IN * ph / pw
    if h_in > 7.0:                       # keep tall figures on a single page
        h_in = 7.0
        w_in = 7.0 * pw / ph
    cx, cy = int(w_in * EMU_PER_IN), int(h_in * EMU_PER_IN)

    idx = len(_media) + 2                # image1.png already exists in template
    newname = f'image{idx}.png'
    with open(src, 'rb') as fh:
        _media.append((newname, fh.read()))
    rid = f'rIdFig{idx}'
    _fig_n[0] += 1

    drawing = (
        '<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
        '<wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:docPr id="{100 + idx}" name="Figure {_fig_n[0]}"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>'
        '</wp:cNvGraphicFramePr>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:nvPicPr><pic:cNvPr id="{100 + idx}" name="{newname}"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        '<pic:spPr><a:xfrm><a:off x="0" y="0"/>'
        f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
    )
    cap = ('<w:p><w:pPr><w:pStyle w:val="Caption"/><w:jc w:val="center"/></w:pPr>'
           '<w:r><w:t xml:space="preserve">Figure </w:t></w:r>'
           '<w:fldSimple w:instr=" SEQ Figure \\* ARABIC ">'
           f'<w:r><w:t>{_fig_n[0]}</w:t></w:r></w:fldSimple>'
           f'<w:r><w:t xml:space="preserve">: {escape(caption)}</w:t></w:r></w:p>')

    _rels.append((rid, newname))
    return drawing + cap


def table(key, caption):
    """Render one of report_content.TABLES as a Word table, caption above."""
    rows = C.TABLES[key]
    ncol = max(len(r) for r in rows)
    total = int(MAX_W_IN * 1440)
    colw = total // ncol
    _tab_n[0] += 1

    def cell(text, header=False):
        shade = '<w:shd w:val="clear" w:color="auto" w:fill="D9E2F3"/>' if header else ''
        bold = '<w:rPr><w:b/></w:rPr>' if header else ''
        return (f'<w:tc><w:tcPr><w:tcW w:w="{colw}" w:type="dxa"/>{shade}</w:tcPr>'
                f'<w:p><w:pPr><w:spacing w:after="0"/></w:pPr>'
                f'<w:r>{bold}<w:t xml:space="preserve">{escape(str(text))}</w:t></w:r></w:p></w:tc>')

    xml = ['<w:p><w:pPr><w:pStyle w:val="Caption"/></w:pPr>'
           '<w:r><w:t xml:space="preserve">Table </w:t></w:r>'
           '<w:fldSimple w:instr=" SEQ Table \\* ARABIC ">'
           f'<w:r><w:t>{_tab_n[0]}</w:t></w:r></w:fldSimple>'
           f'<w:r><w:t xml:space="preserve">: {escape(caption)}</w:t></w:r></w:p>']
    xml.append('<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/>'
               f'<w:tblW w:w="{total}" w:type="dxa"/>'
               '<w:tblBorders>'
               + ''.join(f'<w:{e} w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
                         for e in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))
               + '</w:tblBorders></w:tblPr>')
    xml.append('<w:tblGrid>' + ''.join(f'<w:gridCol w:w="{colw}"/>'
                                       for _ in range(ncol)) + '</w:tblGrid>')
    for i, r in enumerate(rows):
        r = list(r) + [''] * (ncol - len(r))
        trPr = '<w:trPr><w:tblHeader/></w:trPr>' if i == 0 else ''
        xml.append('<w:tr>' + trPr + ''.join(cell(c, i == 0) for c in r) + '</w:tr>')
    xml.append('</w:tbl>')
    xml.append(para(''))     # spacer, else the next paragraph glues to the table
    return ''.join(xml)


def block(items):
    """Strings become paragraphs. '3.1 Title' becomes a Heading 2,
    [[FIG:file|caption]] an image, [[TAB:key|caption]] a table."""
    out = []
    for t in items:
        mf = re.match(r'^\[\[FIG:([^|]+)\|(.+)\]\]$', t)
        mt = re.match(r'^\[\[TAB:([^|]+)\|(.+)\]\]$', t)
        if mf:
            out.append(figure(mf.group(1), mf.group(2)))
        elif mt:
            out.append(table(mt.group(1), mt.group(2)))
        elif re.match(r'^\d\.\d\s+[A-Z]', t) and len(t) < 90:
            out.append(para(re.sub(r'^\d\.\d\s+', '', t), 'Heading2'))
        else:
            out.append(para(t))
    return ''.join(out)


def justify_normal(styles_xml):
    """Justify body text by adding <w:jc w:val="both"/> to the Normal style.

    The template mandates justified paragraphs in its guidance notes but ships
    without any justification set, so this closes that gap. Applying it at the
    style level rather than per paragraph leaves headings and centred figure
    captions - which carry their own styles or explicit alignment - untouched.
    In the OOXML schema jc follows spacing/ind inside pPr, hence the position.
    """
    m = re.search(r'<w:style [^>]*w:styleId="Normal".*?</w:style>', styles_xml, re.S)
    if not m or '<w:jc ' in m.group(0):
        return styles_xml
    style = m.group(0)
    if '<w:pPr>' in style:
        fixed = re.sub(r'(<w:spacing[^/]*/>)', r'\1<w:jc w:val="both"/>', style, count=1)
        if fixed == style:                      # pPr present but no spacing element
            fixed = style.replace('<w:pPr>', '<w:pPr><w:jc w:val="both"/>', 1)
    else:
        fixed = style.replace('<w:qFormat/>', '<w:qFormat/><w:pPr><w:jc w:val="both"/></w:pPr>', 1)
    return styles_xml.replace(style, fixed, 1)


def toc_field(kind):
    """A real Table of Figures / Tables field. The template leaves these headings
    empty, so without this there is nothing for Word to populate on refresh."""
    return ('<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> TOC \\h \\z \\c "{kind}" </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            '<w:r><w:t xml:space="preserve">Select this list and press F9 to populate it.</w:t></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')


# ---------------------------------------------------------------- assembly ---
# Order matters: figures and tables are numbered as these blocks are built, so
# this dict must be constructed in the order the sections appear in the report.
AFTER = {}
AFTER['Abstract'] = block(C.ABSTRACT)
AFTER['Acknowledgements'] = block(C.ACKNOWLEDGEMENTS)
AFTER['List of Figures'] = toc_field('Figure')
AFTER['List of Tables'] = toc_field('Table')
AFTER['Introduction'] = block(C.CH1_INTRO)
AFTER['Problem Description, Context and Motivation'] = block(C.CH1_PROBLEM)
AFTER['Objectives'] = block(C.CH1_OBJECTIVES)
AFTER['Methodology'] = block(C.CH1_METHODOLOGY)
AFTER['Legal, Social, Ethical and Professional Considerations'] = block(C.CH1_LEGAL)
AFTER['Background'] = block(C.CH1_BACKGROUND)
AFTER['Structure of Report'] = block(C.CH1_STRUCTURE)
AFTER['Literature - Technology Review'] = block(C.CH2_INTRO)
AFTER['Literature Review'] = block(C.CH2_LIT)
AFTER['Technology Review'] = block(C.CH2_TECH)
AFTER['Summary'] = block(C.CH2_SUMMARY)
AFTER['Implementation'] = block(C.CH3_IMPL)
AFTER['Evaluation and Results'] = block(C.CH4_EVAL)
AFTER['Related Works'] = block(C.CH4_RELATED)
AFTER['Conclusion'] = block(C.CH5_CONC)
AFTER['Future Work'] = block(C.CH5_FUTURE)
AFTER['Reflection'] = block(C.CH5_REFLECT)
AFTER['References'] = ''.join(para(r) for r in C.REFERENCES)
for _k, _v in C.APPENDICES.items():
    AFTER[_k] = block(_v)

SIGN_OFF = (para(f'Name: {C.AUTHOR}')
            + para('Date: ______________________')
            + para('Signature: ______________________')
            + para(''))
BEFORE = {'Acknowledgements': SIGN_OFF}

# title-page fields the template leaves for the student to complete
FILL = [
    ('Project Report Title', C.TITLE),
    ('Your Name', C.AUTHOR),
    ('Computing /Data Science /Web Development', 'Data Science'),
    ('Subtitle if required', C.SUBTITLE),
]


def main():
    zin = zipfile.ZipFile(TEMPLATE)
    doc = zin.read('word/document.xml').decode('utf-8')

    # Fill the title-page fields. Word splits text across several <w:r> runs, so
    # a phrase visible in the document is often not contiguous in the XML. Match
    # on the paragraph's combined text, then rewrite its runs as one.
    def fill_titles(xml):
        def repl(m):
            p = m.group(0)
            text = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)).strip()
            for placeholder, value in FILL:
                if text == placeholder:
                    pPr = re.search(r'<w:pPr>.*?</w:pPr>', p, re.S)
                    rPr = re.search(r'<w:rPr>.*?</w:rPr>', p, re.S)
                    return ('<w:p>' + (pPr.group(0) if pPr else '')
                            + '<w:r>' + (rPr.group(0) if rPr else '')
                            + f'<w:t xml:space="preserve">{escape(value)}</w:t></w:r></w:p>')
            return p
        return re.sub(r'<w:p[ >].*?</w:p>', repl, xml, flags=re.S)

    doc = fill_titles(doc)

    parts = re.split(r'(<w:p[ >].*?</w:p>)', doc, flags=re.S)

    used, out = set(), []
    for p in parts:
        if not p.startswith('<w:p'):
            out.append(p)
            continue

        style_m = re.search(r'w:pStyle w:val="([^"]+)"', p)
        style = style_m.group(1) if style_m else 'Normal'
        text = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)).strip()

        # drop the template's blue guidance notes and every placeholder variant
        if style == 'Guidancenotes' or re.fullmatch(
                r'insert\s+(your\s+)?text\s+here[.:]?', text, re.I):
            continue

        key0 = text.replace('–', '-').replace('—', '-').strip()
        if style in ('Heading1', 'Heading2', 'Headingbackmatter') and key0 in BEFORE:
            out.append(BEFORE.pop(key0))

        out.append(p)

        if style in ('Heading1', 'Heading2', 'Headingbackmatter'):
            for k in AFTER:
                if k not in used and (key0 == k or key0.replace('-', '–') == k):
                    out.append(AFTER[k])
                    used.add(k)
                    break

    newdoc = ''.join(out)

    # The guidance boxes were tables. Deleting their paragraphs empties them but
    # leaves the borders, which render as blank boxes - strip any table that has
    # no text left at all.
    def drop_empty_tables(xml):
        def repl(m):
            body = m.group(0)
            text = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', body)).strip()
            return '' if not text else body
        return re.sub(r'<w:tbl>.*?</w:tbl>', repl, xml, flags=re.S)

    newdoc = drop_empty_tables(newdoc)

    zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == 'word/document.xml':
            data = newdoc.encode('utf-8')
        elif item.filename == 'word/styles.xml':
            data = justify_normal(data.decode('utf-8')).encode('utf-8')
        elif item.filename == 'word/_rels/document.xml.rels' and _rels:
            rels = data.decode('utf-8')
            add = ''.join(
                f'<Relationship Id="{rid}" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                f'Target="media/{name}"/>' for rid, name in _rels)
            rels = rels.replace('</Relationships>', add + '</Relationships>')
            data = rels.encode('utf-8')
        zout.writestr(item, data)
    for name, blob in _media:
        zout.writestr(f'word/media/{name}', blob)
    zout.close()
    zin.close()

    missing = [k for k in AFTER if k not in used]
    print(f'inserted {len(used)}/{len(AFTER)} sections')
    print(f'figures: {_fig_n[0]}   tables: {_tab_n[0]}')
    if missing:
        print('NOT MATCHED:', missing)
    print('written:', OUT)


if __name__ == '__main__':
    main()
