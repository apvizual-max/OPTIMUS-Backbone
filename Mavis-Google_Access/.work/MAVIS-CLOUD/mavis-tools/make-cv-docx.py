#!/usr/bin/env python3
# CV-uri 1 pagina, ATS-friendly: o singura coloana, font standard, fara tabele
# ATS-ul citeste documente simple. Tabelele si coloanele multiple stric parsarea.
import os, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = '/workspace/ALEX-KIT/CV-URI'
os.makedirs(OUT, exist_ok=True)

NAVY  = RGBColor(0x1A, 0x1A, 0x2E)
GREY  = RGBColor(0x55, 0x55, 0x60)
RULE  = 'BFBFBF'

def set_margins(doc):
    for s in doc.sections:
        s.top_margin = Cm(1.4); s.bottom_margin = Cm(1.2)
        s.left_margin = Cm(1.7); s.right_margin = Cm(1.7)

def rule(doc, color=RULE, size=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = Pt(2)
    pPr = p._p.get_or_add_pPr()
    b = OxmlElement('w:pBdr'); bot = OxmlElement('w:bottom')
    bot.set(qn('w:val'), 'single'); bot.set(qn('w:sz'), str(size))
    bot.set(qn('w:space'), '0'); bot.set(qn('w:color'), color)
    b.append(bot); pPr.append(b)

def para(doc, text, size=10, bold=False, color=None, before=0, after=4,
         align=None, caps=False, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    if align: p.alignment = align
    r = p.add_run(text)
    r.font.size = Pt(size); r.bold = bold; r.italic = italic
    r.font.name = 'Calibri'
    if color is not None: r.font.color.rgb = color
    if caps: r.font.all_caps = True
    return p

def section(doc, title):
    para(doc, title.upper(), size=10.5, bold=True, color=NAVY, before=8, after=2)
    rule(doc)

def bullets(doc, items, size=10):
    for it in items:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.left_indent = Cm(0.5)
        r = p.add_run(it)
        r.font.size = Pt(size); r.font.name = 'Calibri'

def build(target, meta):
    doc = Document()
    set_margins(doc)
    st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10)
    st.paragraph_format.space_after = Pt(3)

    # antet
    para(doc, 'ALEXANDRU POPESCU', size=20, bold=True, color=NAVY, after=1)
    para(doc, 'ART DIRECTOR  ·  AI-AUGMENTED DESIGN', size=10, bold=True, color=GREY, after=2)
    para(doc, 'Bucharest, Romania  ·  ap-id.ro  ·  portfolio available on request',
         size=9, color=GREY, after=6)

    # rolul la care aplica
    para(doc, 'APPLYING FOR: ' + target, size=9.5, bold=True, color=NAVY, before=4, after=8)
    rule(doc, '1A1A2E', 10)

    section(doc, 'Professional Summary')
    para(doc, meta['summary'], size=10, after=2)

    section(doc, 'Core Competencies')
    bullets(doc, meta['expertise'][:8])

    section(doc, 'Key Achievements')
    for a in meta['achievements']:
        a = a.replace('**', '')            # markdown bold -> bold real in Word
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(4)
        if ':' in a and a.index(':') < 60:
            head, rest = a.split(':', 1)
            r1 = p.add_run(head + ':'); r1.bold = True; r1.font.size = Pt(10); r1.font.name='Calibri'
            r2 = p.add_run(rest); r2.font.size = Pt(10); r2.font.name = 'Calibri'
        else:
            r = p.add_run(a); r.font.size = Pt(10); r.font.name = 'Calibri'

    section(doc, 'Design & Production')
    para(doc, 'Adobe Creative Cloud (Photoshop, Illustrator, InDesign, After Effects, Premiere)  ·  '
              'Figma design systems  ·  Comfy UI & Adobe Firefly  ·  Runway  ·  CapCut', size=9.5, after=2)

    section(doc, 'Selected Clients')
    para(doc, 'Microsoft  ·  Nikon  ·  Yokogawa  ·  H&M  ·  Erste Group  ·  Intesa Sanpaolo  ·  '
              'Aiper  ·  Pure Electric  ·  Veeam  ·  ASSA ABLOY', size=9.5, after=2)

    para(doc, 'Proof of work provided on request.', size=8.5, color=GREY, before=8, italic=True)

    # --- pagina 2: scrisoarea de intentie ---
    doc.add_page_break()
    para(doc, 'ALEXANDRU POPESCU', size=11, bold=True, color=NAVY, after=1)
    para(doc, 'Bucharest, Romania  ·  ap-id.ro', size=9, color=GREY, after=10)
    rule(doc, '1A1A2E', 10)

    para(doc, 'COVER LETTER', size=13, bold=True, color=NAVY, before=2, after=8)
    para(doc, meta['salutation'], size=10.5, after=8)

    for block in meta['letter']:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(7)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(block); r.font.size = Pt(10); r.font.name = 'Calibri'

    para(doc, meta['signoff'], size=10, before=6, after=6)
    para(doc, 'Proof of work provided on request.', size=8.5, color=GREY, before=8, italic=True)

    path = os.path.join(OUT, target.replace(' ', '-').replace('/', '-') + '-CV.docx')
    doc.save(path)
    return path

if __name__ == '__main__':
    data = json.load(open('/workspace/ALEX-KIT/cv-data.json'))
    for t, meta in data.items():
        print('OK  ' + build(t, meta))
