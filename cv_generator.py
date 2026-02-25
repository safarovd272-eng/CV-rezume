"""
CV Generator — Europa Pass International Style
Canvas asosida pixel-perfect dizayn
Shrift: Helvetica (bir xil), o'lcham: 9.5-11pt
"""

import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

# ── O'lchamlar ────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
SIDEBAR_W      = 65 * mm
MAIN_X         = SIDEBAR_W
MAIN_W         = PAGE_W - SIDEBAR_W
MARGIN         = 8 * mm

# ── Ranglar ───────────────────────────────────────────────────────────────────
C_BLUE   = colors.HexColor('#1A3C6E')
C_ACCENT = colors.HexColor('#2E6DB4')
C_GOLD   = colors.HexColor('#E8B84B')
C_WHITE  = colors.white
C_DARK   = colors.HexColor('#1A1A1A')
C_GRAY   = colors.HexColor('#555555')

# ── Shrift (HAMMASI Helvetica) ────────────────────────────────────────────────
F_REG  = 'Helvetica'
F_BOLD = 'Helvetica-Bold'
F_IT   = 'Helvetica-Oblique'

SZ_NAME    = 20
SZ_SECTION = 11
SZ_ROLE    = 10
SZ_BODY    = 9.5
SZ_SMALL   = 8.5
SZ_SB_SEC  = 8
SZ_SB_VAL  = 8.5


def level_dots(level):
    m = {'a1':1,'a2':2,'b1':3,'b2':4,'c1':5,'c2':6,
         'native':6,'ona tili':6,'родной':6,
         'beginner':1,'elementary':2,'intermediate':3,
         'upper intermediate':4,'advanced':5,'proficient':6}
    return m.get(level.strip().lower(), 3)


def draw_lang_bar(c, x, y, filled, total=6):
    dot_r, gap = 2.2, 6
    for i in range(total):
        cx = x + i * gap
        c.setFillColor(C_GOLD if i < filled else colors.HexColor('#3A5A8A'))
        c.circle(cx, y, dot_r, fill=1, stroke=0)


def wrap_text(c, text, font, size, max_w, x, y, line_h):
    words = str(text).split()
    line  = ''
    for word in words:
        test = line + ' ' + word if line else word
        if c.stringWidth(test, font, size) <= max_w:
            line = test
        else:
            c.drawString(x, y, line)
            y -= line_h
            line = word
    if line:
        c.drawString(x, y, line)
        y -= line_h
    return y


# ─── Sidebar helpers ──────────────────────────────────────────────────────────

def sidebar_section(c, title, y):
    y -= 10 * mm
    c.setFillColor(C_GOLD)
    c.setFont(F_BOLD, SZ_SB_SEC)
    c.drawString(MARGIN, y, title.upper())
    y -= 3.5
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(0.5)
    c.line(MARGIN, y, SIDEBAR_W - MARGIN, y)
    return y - 5


def sidebar_item(c, label, value, y):
    if not value:
        return y
    c.setFillColor(C_GOLD)
    c.setFont(F_BOLD, 7)
    c.drawString(MARGIN, y, label.upper())
    y -= 3.5 * mm
    c.setFillColor(C_WHITE)
    c.setFont(F_REG, SZ_SB_VAL)
    y = wrap_text(c, value, F_REG, SZ_SB_VAL, SIDEBAR_W - MARGIN*2, MARGIN, y, 3.8*mm)
    return y


# ─── Main helpers ─────────────────────────────────────────────────────────────

def main_section(c, title, y):
    y -= 7 * mm
    c.setFillColor(C_ACCENT)
    c.rect(MAIN_X, y - 1*mm, 3, 5*mm, fill=1, stroke=0)
    c.setFillColor(C_DARK)
    c.setFont(F_BOLD, SZ_SECTION)
    c.drawString(MAIN_X + MARGIN, y, title.upper())
    y -= 2.5 * mm
    c.setStrokeColor(C_ACCENT)
    c.setLineWidth(1)
    c.line(MAIN_X + MARGIN, y, PAGE_W - MARGIN, y)
    return y - 4 * mm


def entry_header(c, left, right, y):
    c.setFillColor(C_DARK)
    c.setFont(F_BOLD, SZ_ROLE)
    c.drawString(MAIN_X + MARGIN, y, left)
    c.setFillColor(C_GRAY)
    c.setFont(F_IT, SZ_SMALL)
    rw = c.stringWidth(right, F_IT, SZ_SMALL)
    c.drawString(PAGE_W - MARGIN - rw, y, right)
    return y - 4.5 * mm


def entry_sub(c, text, y):
    c.setFillColor(C_GRAY)
    c.setFont(F_IT, SZ_SMALL)
    c.drawString(MAIN_X + MARGIN, y, text)
    return y - 4 * mm


def body_text(c, text, y, indent=0):
    if not text: return y
    c.setFillColor(C_DARK)
    c.setFont(F_REG, SZ_BODY)
    max_w = MAIN_W - MARGIN*2 - indent
    y = wrap_text(c, text, F_REG, SZ_BODY, max_w, MAIN_X + MARGIN + indent, y, 4.5*mm)
    return y


def bullet_text(c, text, y):
    c.setFillColor(C_ACCENT)
    c.setFont(F_BOLD, SZ_BODY)
    c.drawString(MAIN_X + MARGIN, y, chr(149))
    return body_text(c, text, y, indent=4*mm)


# ─── Parse funksiyalari ────────────────────────────────────────────────────────

def parse_education(lst):
    r = []
    for item in lst:
        p = [x.strip() for x in item.split('|')]
        r.append({'degree':p[0] if p else '','institution':p[1] if len(p)>1 else '',
                  'years':p[2] if len(p)>2 else '','gpa':p[3] if len(p)>3 else ''})
    return r

def parse_work(lst):
    r = []
    for item in lst:
        p = [x.strip() for x in item.split('|')]
        r.append({'position':p[0] if p else '','company':p[1] if len(p)>1 else '',
                  'years':p[2] if len(p)>2 else '','description':p[3] if len(p)>3 else ''})
    return r

def parse_skills(lst):
    r = []
    for item in lst:
        if ':' in item:
            cat, sk = item.split(':',1)
            r.append({'category':cat.strip(),'skills':sk.strip()})
    return r

def parse_languages(lst):
    r = []
    for item in lst:
        p = [x.strip() for x in item.split('|')]
        if len(p) >= 2:
            r.append({'language':p[0],'level':p[1]})
    return r

def parse_certificates(lst):
    r = []
    for item in lst:
        p = [x.strip() for x in item.split('|')]
        r.append({'name':p[0] if p else '','org':p[1] if len(p)>1 else '','year':p[2] if len(p)>2 else ''})
    return r


# ─── ASOSIY PDF ───────────────────────────────────────────────────────────────

def generate_pdf(data: dict, output_path: str):
    c = canvas.Canvas(output_path, pagesize=A4)

    # ── Sidebar fon ────────────────────────────────────────────────────────────
    c.setFillColor(C_BLUE)
    c.rect(0, 0, SIDEBAR_W, PAGE_H, fill=1, stroke=0)

    # ── Foto ───────────────────────────────────────────────────────────────────
    first = data.get('first_name', '')
    last  = data.get('last_name', '')
    photo = data.get('photo')
    size  = 46 * mm
    px    = (SIDEBAR_W - size) / 2
    py    = PAGE_H - size - 12 * mm
    cx    = px + size/2
    cy    = py + size/2

    if photo and os.path.exists(photo):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(photo).convert('RGB')
            w, h = img.size
            m = min(w, h)
            img = img.crop(((w-m)//2,(h-m)//2,(w+m)//2,(h+m)//2))
            img = img.resize((300, 300))
            buf = BytesIO()
            img.save(buf, format='JPEG')
            buf.seek(0)
            c.saveState()
            path = c.beginPath()
            path.circle(cx, cy, size/2)
            c.clipPath(path, stroke=0, fill=0)
            c.drawImage(buf, px, py, width=size, height=size,
                        preserveAspectRatio=True, mask='auto')
            c.restoreState()
        except Exception:
            pass
    else:
        c.setFillColor(C_ACCENT)
        c.circle(cx, cy, size/2, fill=1, stroke=0)
        initials = (first[:1] + last[:1]).upper()
        c.setFillColor(C_GOLD)
        c.setFont(F_BOLD, 26)
        tw = c.stringWidth(initials, F_BOLD, 26)
        c.drawString(cx - tw/2, cy - 9, initials)

    # Aylana chegara
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(2.5)
    c.circle(cx, cy, size/2, fill=0, stroke=1)

    sidebar_y = py - 6 * mm

    # ── CONTACT ────────────────────────────────────────────────────────────────
    sidebar_y = sidebar_section(c, 'Contact', sidebar_y)
    for label, key in [('Email','email'),('Phone','phone'),('Address','address'),
                        ('LinkedIn','linkedin'),('GitHub','github'),('Website','website')]:
        sidebar_y = sidebar_item(c, label, data.get(key,''), sidebar_y)

    # ── PERSONAL ───────────────────────────────────────────────────────────────
    sidebar_y = sidebar_section(c, 'Personal', sidebar_y)
    sidebar_y = sidebar_item(c, 'Date of Birth', data.get('dob',''), sidebar_y)
    sidebar_y = sidebar_item(c, 'Nationality', data.get('nationality',''), sidebar_y)

    # ── LANGUAGES ──────────────────────────────────────────────────────────────
    lang_list = parse_languages(data.get('lang_list', []))
    if lang_list:
        sidebar_y = sidebar_section(c, 'Languages', sidebar_y)
        for lang in lang_list:
            c.setFillColor(C_WHITE)
            c.setFont(F_BOLD, SZ_SB_VAL)
            c.drawString(MARGIN, sidebar_y, lang['language'])
            c.setFillColor(C_GOLD)
            c.setFont(F_IT, 7.5)
            c.drawString(MARGIN, sidebar_y - 3.5*mm, lang['level'])
            draw_lang_bar(c, MARGIN + 22*mm, sidebar_y - 3.5*mm + 1.5, level_dots(lang['level']))
            sidebar_y -= 9 * mm

    # ── SKILLS ─────────────────────────────────────────────────────────────────
    skills_list = parse_skills(data.get('skills_list', []))
    if skills_list:
        sidebar_y = sidebar_section(c, 'Skills', sidebar_y)
        for sk in skills_list:
            c.setFillColor(C_GOLD)
            c.setFont(F_BOLD, 7.5)
            c.drawString(MARGIN, sidebar_y, sk['category'].upper())
            sidebar_y -= 3.5 * mm
            c.setFillColor(C_WHITE)
            c.setFont(F_REG, SZ_SB_VAL)
            sidebar_y = wrap_text(c, sk['skills'], F_REG, SZ_SB_VAL,
                                  SIDEBAR_W - MARGIN*2, MARGIN, sidebar_y, 3.8*mm)
            sidebar_y -= 2 * mm

    # ═════════════════════════════════════════════════════════════════════════
    # MAIN USTUN
    # ═════════════════════════════════════════════════════════════════════════

    # Header sariq chiziq
    c.setFillColor(C_ACCENT)
    c.rect(MAIN_X, PAGE_H - 40*mm, 3.5, 40*mm, fill=1, stroke=0)

    # ISM
    main_y = PAGE_H - 13 * mm
    c.setFillColor(C_BLUE)
    c.setFont(F_BOLD, SZ_NAME)
    fw = c.stringWidth(first.upper() + ' ', F_BOLD, SZ_NAME)
    c.drawString(MAIN_X + MARGIN, main_y, first.upper() + ' ')
    c.setFillColor(C_ACCENT)
    c.drawString(MAIN_X + MARGIN + fw, main_y, last.upper())

    main_y -= 7 * mm

    # Objective
    obj = data.get('objective','')
    if obj:
        c.setFillColor(C_GRAY)
        c.setFont(F_IT, SZ_BODY)
        main_y = wrap_text(c, obj, F_IT, SZ_BODY,
                           MAIN_W - MARGIN*2, MAIN_X + MARGIN, main_y, 4.5*mm)
    main_y -= 3 * mm

    # EDUCATION
    edu_list = parse_education(data.get('education_list', []))
    if edu_list:
        main_y = main_section(c, 'Education', main_y)
        for edu in edu_list:
            yr = edu['years'] + (f'  |  GPA: {edu["gpa"]}' if edu.get('gpa') else '')
            main_y = entry_header(c, edu['degree'], yr, main_y)
            main_y = entry_sub(c, edu['institution'], main_y)
            main_y -= 2 * mm

    # WORK
    work_list = parse_work(data.get('work_list', []))
    if work_list:
        main_y = main_section(c, 'Work Experience', main_y)
        for job in work_list:
            main_y = entry_header(c, job['position'], job['years'], main_y)
            main_y = entry_sub(c, job['company'], main_y)
            if job.get('description'):
                for desc in job['description'].split(','):
                    desc = desc.strip()
                    if desc:
                        main_y = bullet_text(c, desc, main_y)
            main_y -= 2 * mm

    # CERTIFICATES
    cert_list = parse_certificates(data.get('cert_list', []))
    if cert_list:
        main_y = main_section(c, 'Certificates', main_y)
        for cert in cert_list:
            name_p = cert['name'] + (f' — {cert["org"]}' if cert.get('org') else '')
            main_y = entry_header(c, name_p, cert.get('year',''), main_y)
        main_y -= 2 * mm

    # HOBBIES
    hobbies = data.get('hobbies','')
    if hobbies:
        main_y = main_section(c, 'Interests', main_y)
        main_y = body_text(c, hobbies, main_y)

    c.save()


# ─── DOCX ─────────────────────────────────────────────────────────────────────

def generate_docx(data: dict, output_path: str):
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    doc = Document()
    for section in doc.sections:
        section.top_margin    = Cm(0)
        section.bottom_margin = Cm(1)
        section.left_margin   = Cm(0)
        section.right_margin  = Cm(0)
        section.page_width    = Cm(21)
        section.page_height   = Cm(29.7)

    EU_BLUE = RGBColor(26,60,110)
    ACCENT  = RGBColor(46,109,180)
    GOLD    = RGBColor(232,184,75)
    WHITE   = RGBColor(255,255,255)
    DARK    = RGBColor(26,26,26)
    GRAY    = RGBColor(85,85,85)

    def hex_fill(cell, hex_color):
        tcPr = cell._tc.get_or_add_tcPr()
        shd  = OxmlElement('w:shd')
        shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto')
        shd.set(qn('w:fill'), hex_color)
        tcPr.append(shd)

    def set_w(cell, twips):
        tcPr = cell._tc.get_or_add_tcPr()
        tcW  = tcPr.find(qn('w:tcW'))
        if tcW is None:
            tcW = OxmlElement('w:tcW'); tcPr.append(tcW)
        tcW.set(qn('w:w'), str(twips)); tcW.set(qn('w:type'), 'dxa')

    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl.allow_autofit = False
    sc = tbl.cell(0,0); mc = tbl.cell(0,1)
    set_w(sc, 3685); set_w(mc, 8135)
    hex_fill(sc,'1A3C6E'); hex_fill(mc,'FFFFFF')
    sc.vertical_alignment = WD_ALIGN_VERTICAL.TOP
    mc.vertical_alignment = WD_ALIGN_VERTICAL.TOP

    def s_para(text='', size=9, bold=False, italic=False, color=WHITE,
               align=WD_ALIGN_PARAGRAPH.LEFT, sb=0, sa=2):
        p = sc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(sb)
        p.paragraph_format.space_after  = Pt(sa)
        p.paragraph_format.left_indent  = Cm(0.45)
        if text:
            r = p.add_run(text)
            r.font.name='Calibri'; r.font.size=Pt(size)
            r.font.bold=bold; r.font.italic=italic
            r.font.color.rgb=color
        return p

    def s_section(title):
        p = s_para(title.upper(), size=8, bold=True, color=GOLD, sb=8, sa=1)
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bot  = OxmlElement('w:bottom')
        bot.set(qn('w:val'),'single'); bot.set(qn('w:sz'),'4')
        bot.set(qn('w:space'),'1'); bot.set(qn('w:color'),'E8B84B')
        pBdr.append(bot); pPr.append(pBdr)

    first = data.get('first_name',''); last = data.get('last_name','')
    initials = (first[:1]+last[:1]).upper()
    s_para(initials, size=30, bold=True, color=GOLD,
           align=WD_ALIGN_PARAGRAPH.CENTER, sb=16, sa=6)

    s_section('Contact')
    for label, key in [('Email','email'),('Phone','phone'),('Address','address'),
                        ('LinkedIn','linkedin'),('GitHub','github'),('Website','website')]:
        v = data.get(key,'')
        if v:
            s_para(label.upper(), size=7, bold=True, color=GOLD, sb=3, sa=1)
            s_para(v, size=9, color=WHITE, sa=2)

    s_section('Personal')
    for label, key in [('Date of Birth','dob'),('Nationality','nationality')]:
        v = data.get(key,'')
        if v:
            s_para(label.upper(), size=7, bold=True, color=GOLD, sb=3, sa=1)
            s_para(v, size=9, color=WHITE, sa=2)

    lang_list = parse_languages(data.get('lang_list',[]))
    if lang_list:
        s_section('Languages')
        for lang in lang_list:
            dots = level_dots(lang['level'])
            bar  = 'ā' * dots + 'ā' * (6-dots)
            s_para(lang['language'], size=9, bold=True, color=WHITE, sb=3, sa=1)
            s_para(f"{lang['level']}  {'●'*dots}{'○'*(6-dots)}", size=8, italic=True, color=GOLD, sa=2)

    skills_list = parse_skills(data.get('skills_list',[]))
    if skills_list:
        s_section('Skills')
        for sk in skills_list:
            s_para(sk['category'].upper(), size=7.5, bold=True, color=GOLD, sb=3, sa=1)
            s_para(sk['skills'], size=9, color=WHITE, sa=2)

    # ── Main ──────────────────────────────────────────────────────────────────
    mc.paragraphs[0].clear()

    def m_para(text='', size=10, bold=False, italic=False,
               color=DARK, align=WD_ALIGN_PARAGRAPH.LEFT,
               sb=0, sa=2, indent=0):
        p = mc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(sb)
        p.paragraph_format.space_after  = Pt(sa)
        p.paragraph_format.left_indent  = Cm(0.5 + indent)
        if text:
            r = p.add_run(text)
            r.font.name='Calibri'; r.font.size=Pt(size)
            r.font.bold=bold; r.font.italic=italic
            r.font.color.rgb=color
        return p

    def m_section(title):
        p = m_para(title.upper(), size=11, bold=True, color=ACCENT, sb=10, sa=2)
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bot  = OxmlElement('w:bottom')
        bot.set(qn('w:val'),'single'); bot.set(qn('w:sz'),'6')
        bot.set(qn('w:space'),'1'); bot.set(qn('w:color'),'2E6DB4')
        pBdr.append(bot); pPr.append(pBdr)

    # NAME
    p = mc.paragraphs[0]
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.left_indent  = Cm(0.5)
    r1 = p.add_run(first.upper() + ' ')
    r1.font.name='Calibri'; r1.font.size=Pt(20)
    r1.font.bold=True; r1.font.color.rgb=EU_BLUE
    r2 = p.add_run(last.upper())
    r2.font.name='Calibri'; r2.font.size=Pt(20)
    r2.font.bold=True; r2.font.color.rgb=ACCENT

    if data.get('objective'):
        m_para(data['objective'], size=9.5, italic=True, color=GRAY, sa=6)

    edu_list = parse_education(data.get('education_list',[]))
    if edu_list:
        m_section('Education')
        for edu in edu_list:
            p = m_para(sb=4, sa=1)
            r1 = p.add_run(edu['degree'])
            r1.font.name='Calibri'; r1.font.size=Pt(10)
            r1.font.bold=True; r1.font.color.rgb=DARK
            if edu.get('years'):
                r2 = p.add_run(f"  {edu['years']}")
                r2.font.name='Calibri'; r2.font.size=Pt(8.5)
                r2.font.italic=True; r2.font.color.rgb=GRAY
            m_para(edu['institution'], size=9, italic=True, color=GRAY, sa=4)

    work_list = parse_work(data.get('work_list',[]))
    if work_list:
        m_section('Work Experience')
        for job in work_list:
            p = m_para(sb=4, sa=1)
            r1 = p.add_run(job['position'])
            r1.font.name='Calibri'; r1.font.size=Pt(10)
            r1.font.bold=True; r1.font.color.rgb=DARK
            if job.get('years'):
                r2 = p.add_run(f"  {job['years']}")
                r2.font.name='Calibri'; r2.font.size=Pt(8.5)
                r2.font.italic=True; r2.font.color.rgb=GRAY
            m_para(job['company'], size=9, italic=True, color=GRAY, sa=2)
            if job.get('description'):
                for desc in job['description'].split(','):
                    desc = desc.strip()
                    if desc:
                        m_para(f'• {desc}', size=9.5, color=DARK, sa=1, indent=0.3)

    cert_list = parse_certificates(data.get('cert_list',[]))
    if cert_list:
        m_section('Certificates')
        for cert in cert_list:
            t = cert['name']
            if cert.get('org'): t += f' — {cert["org"]}'
            if cert.get('year'): t += f' ({cert["year"]})'
            m_para(f'• {t}', size=9.5, color=DARK, sb=2, sa=2, indent=0.3)

    if data.get('hobbies'):
        m_section('Interests')
        m_para(data['hobbies'], size=9.5, color=DARK, sa=2)

    doc.save(output_path)
