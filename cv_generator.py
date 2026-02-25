"""
CV Generator — Europa Pass Style
Barcha muammolar hal qilingan versiya:
- Sidebar matnlar truncate/wrap qilinadi
- Shrift bir xil (Helvetica)
- O'lchamlar to'g'ri (10-11pt)
- Rasm aylana ichida
"""

import os
from io import BytesIO
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

PAGE_W, PAGE_H = A4          # 595 x 842 pt
SB_W   = 63 * mm             # sidebar kengligi
MN_X   = SB_W                # main ustun boshlanishi
MN_W   = PAGE_W - SB_W
PAD    = 7 * mm              # ichki bo'shliq

# ── Ranglar ───────────────────────────────────────────────────────────────────
BG     = colors.HexColor('#1B3A6B')   # sidebar fon
ACCENT = colors.HexColor('#2761AB')   # asosiy ko'k
GOLD   = colors.HexColor('#E9B949')   # oltin
WHITE  = colors.white
DARK   = colors.HexColor('#1C1C1C')
GRAY   = colors.HexColor('#5A5A5A')
LGRAY  = colors.HexColor('#E8EEF6')   # bo'limlar orasidagi chiziq

# ── Shriftlar ─────────────────────────────────────────────────────────────────
RG = 'Helvetica'
BD = 'Helvetica-Bold'
IT = 'Helvetica-Oblique'

# ── Razmlar ───────────────────────────────────────────────────────────────────
S_NAME = 19
S_SEC  = 11
S_JOB  = 10
S_BODY = 9.5
S_SM   = 8.5
S_SB_T = 7.5   # sidebar title
S_SB_V = 8.5   # sidebar value


# ─── Yordamchi: matnni chop etish, sidebar uchun (overflow = truncate) ────────

def sb_draw(c, text, font, size, x, y, max_w):
    """Matnni max_w ga sig'masa qisqartiradi"""
    text = str(text)
    if c.stringWidth(text, font, size) <= max_w:
        c.drawString(x, y, text)
        return
    while text and c.stringWidth(text + '...', font, size) > max_w:
        text = text[:-1]
    c.drawString(x, y, text + '...')


def sb_wrap(c, text, font, size, x, y, max_w, lh):
    """Matnni qatorlarga bo'lib chiqaradi, sidebar uchun"""
    words = str(text).split()
    line  = ''
    for w in words:
        t = (line + ' ' + w).strip()
        if c.stringWidth(t, font, size) <= max_w:
            line = t
        else:
            c.drawString(x, y, line)
            y  -= lh
            line = w
    if line:
        c.drawString(x, y, line)
        y -= lh
    return y


def mn_wrap(c, text, font, size, x, y, max_w, lh, color=DARK):
    """Main ustun uchun word wrap"""
    c.setFillColor(color)
    c.setFont(font, size)
    words = str(text).split()
    line  = ''
    for w in words:
        t = (line + ' ' + w).strip()
        if c.stringWidth(t, font, size) <= max_w:
            line = t
        else:
            c.drawString(x, y, line)
            y  -= lh
            line = w
    if line:
        c.drawString(x, y, line)
        y -= lh
    return y


# ─── Til darajasi doiralari ───────────────────────────────────────────────────

def lang_dots(level):
    m = {'a1':1,'a2':2,'b1':3,'b2':4,'c1':5,'c2':6,
         'native':6,'ona tili':6,'родной':6,'beginner':1,
         'elementary':2,'intermediate':3,'upper intermediate':4,
         'advanced':5,'proficient':6}
    return m.get(level.strip().lower(), 3)

def draw_dots(c, x, y, filled, total=5):
    r, gap = 2.5, 7
    for i in range(total):
        c.setFillColor(GOLD if i < filled else colors.HexColor('#334F7A'))
        c.circle(x + i*gap, y, r, fill=1, stroke=0)


# ─── Parse funksiyalari ───────────────────────────────────────────────────────

def pe(lst):
    r=[]
    for item in lst:
        p=[x.strip() for x in item.split('|')]
        r.append({'degree':p[0] if p else '','institution':p[1] if len(p)>1 else '',
                  'years':p[2] if len(p)>2 else '','gpa':p[3] if len(p)>3 else ''})
    return r

def pw(lst):
    r=[]
    for item in lst:
        p=[x.strip() for x in item.split('|')]
        r.append({'position':p[0] if p else '','company':p[1] if len(p)>1 else '',
                  'years':p[2] if len(p)>2 else '','description':p[3] if len(p)>3 else ''})
    return r

def psk(lst):
    r=[]
    for item in lst:
        if ':' in item:
            cat,sk=item.split(':',1)
            r.append({'cat':cat.strip(),'sk':sk.strip()})
    return r

def pl(lst):
    r=[]
    for item in lst:
        p=[x.strip() for x in item.split('|')]
        if len(p)>=2:
            r.append({'lang':p[0],'level':p[1]})
    return r

def pc(lst):
    r=[]
    for item in lst:
        p=[x.strip() for x in item.split('|')]
        r.append({'name':p[0] if p else '','org':p[1] if len(p)>1 else '','year':p[2] if len(p)>2 else ''})
    return r


# ─── ASOSIY PDF ───────────────────────────────────────────────────────────────

def generate_pdf(data: dict, output_path: str):
    c = rl_canvas.Canvas(output_path, pagesize=A4)

    # =====================================================================
    # SIDEBAR
    # =====================================================================
    c.setFillColor(BG)
    c.rect(0, 0, SB_W, PAGE_H, fill=1, stroke=0)

    # ── RASM ─────────────────────────────────────────────────────────────
    first = data.get('first_name','')
    last  = data.get('last_name','')
    photo = data.get('photo')
    sz    = 48 * mm
    px    = (SB_W - sz) / 2
    py    = PAGE_H - sz - 10*mm
    cxp   = px + sz/2
    cyp   = py + sz/2

    if photo and os.path.exists(photo):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(photo).convert('RGB')
            w, h = img.size
            m = min(w, h)
            img = img.crop(((w-m)//2,(h-m)//2,(w+m)//2,(h+m)//2))
            img = img.resize((320, 320))
            buf = BytesIO()
            img.save(buf, 'JPEG', quality=92)
            buf.seek(0)
            c.saveState()
            path = c.beginPath()
            path.circle(cxp, cyp, sz/2)
            c.clipPath(path, stroke=0, fill=0)
            c.drawImage(buf, px, py, width=sz, height=sz,
                        preserveAspectRatio=True, mask='auto')
            c.restoreState()
        except Exception:
            c.setFillColor(ACCENT)
            c.circle(cxp, cyp, sz/2, fill=1, stroke=0)
            initials = (first[:1]+last[:1]).upper()
            c.setFillColor(GOLD)
            c.setFont(BD, 26)
            tw = c.stringWidth(initials, BD, 26)
            c.drawString(cxp-tw/2, cyp-9, initials)
    else:
        c.setFillColor(ACCENT)
        c.circle(cxp, cyp, sz/2, fill=1, stroke=0)
        initials = (first[:1]+last[:1]).upper()
        c.setFillColor(GOLD)
        c.setFont(BD, 26)
        tw = c.stringWidth(initials, BD, 26)
        c.drawString(cxp-tw/2, cyp-9, initials)

    # Aylana chegara
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.5)
    c.circle(cxp, cyp, sz/2, fill=0, stroke=1)

    sb_y = py - 7*mm
    sb_max = SB_W - PAD*2   # sidebar matn maksimal kengligi

    def sb_sec(title, y):
        y -= 9*mm
        c.setFillColor(GOLD)
        c.setFont(BD, S_SB_T)
        c.drawString(PAD, y, title.upper())
        y -= 3
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.line(PAD, y, SB_W-PAD, y)
        return y - 4.5

    def sb_lbl(label, y):
        c.setFillColor(colors.HexColor('#9BB8D4'))
        c.setFont(BD, 6.5)
        c.drawString(PAD, y, label.upper())
        return y - 3.5*mm

    def sb_val(text, y):
        if not text: return y
        c.setFillColor(WHITE)
        c.setFont(RG, S_SB_V)
        y = sb_wrap(c, text, RG, S_SB_V, PAD, y, sb_max, 3.8*mm)
        return y - 1.5*mm

    # ── CONTACT ───────────────────────────────────────────────────────────
    sb_y = sb_sec('Contact', sb_y)
    for lbl, key in [('Email','email'),('Phone','phone'),('Address','address')]:
        v = data.get(key,'')
        if v:
            sb_y = sb_lbl(lbl, sb_y)
            sb_y = sb_val(v, sb_y)
    for lbl, key in [('LinkedIn','linkedin'),('GitHub','github'),('Website','website')]:
        v = data.get(key,'')
        if v:
            sb_y = sb_lbl(lbl, sb_y)
            sb_y = sb_val(v, sb_y)

    # ── PERSONAL ──────────────────────────────────────────────────────────
    sb_y = sb_sec('Personal', sb_y)
    if data.get('dob'):
        sb_y = sb_lbl('Date of Birth', sb_y)
        sb_y = sb_val(data['dob'], sb_y)
    if data.get('nationality'):
        sb_y = sb_lbl('Nationality', sb_y)
        sb_y = sb_val(data['nationality'], sb_y)

    # ── LANGUAGES ─────────────────────────────────────────────────────────
    langs = pl(data.get('lang_list',[]))
    if langs:
        sb_y = sb_sec('Languages', sb_y)
        for lg in langs:
            c.setFillColor(WHITE)
            c.setFont(BD, 9)
            sb_draw(c, lg['lang'], BD, 9, PAD, sb_y, sb_max)
            sb_y -= 3.8*mm
            c.setFillColor(GOLD)
            c.setFont(IT, 8)
            c.drawString(PAD, sb_y, lg['level'])
            dots = lang_dots(lg['level'])
            draw_dots(c, PAD + 24*mm, sb_y + 1.5, min(dots,5))
            sb_y -= 6*mm

    # ── SKILLS ────────────────────────────────────────────────────────────
    skills = psk(data.get('skills_list',[]))
    if skills:
        sb_y = sb_sec('Skills', sb_y)
        for sk in skills:
            c.setFillColor(GOLD)
            c.setFont(BD, 7.5)
            c.drawString(PAD, sb_y, sk['cat'].upper())
            sb_y -= 3.5*mm
            c.setFillColor(WHITE)
            c.setFont(RG, S_SB_V)
            sb_y = sb_wrap(c, sk['sk'], RG, S_SB_V, PAD, sb_y, sb_max, 3.8*mm)
            sb_y -= 2*mm

    # =====================================================================
    # MAIN USTUN
    # =====================================================================

    # Yuqori sariq chiziq
    c.setFillColor(GOLD)
    c.rect(MN_X, PAGE_H - 36*mm, 4, 36*mm, fill=1, stroke=0)

    # ── ISMO ─────────────────────────────────────────────────────────────
    mn_y = PAGE_H - 11*mm
    c.setFillColor(BG)
    c.setFont(BD, S_NAME)
    name_str = first.upper()
    c.drawString(MN_X + PAD, mn_y, name_str)
    nw = c.stringWidth(name_str + ' ', BD, S_NAME)
    c.setFillColor(ACCENT)
    c.drawString(MN_X + PAD + nw, mn_y, last.upper())
    mn_y -= 6*mm

    # ── OBJECTIVE ─────────────────────────────────────────────────────────
    obj = data.get('objective','')
    if obj:
        mn_y = mn_wrap(c, obj, IT, S_BODY,
                       MN_X+PAD, mn_y, MN_W-PAD*2, 4.5*mm, GRAY)
    mn_y -= 3*mm

    mn_max = MN_W - PAD*2

    def mn_sec(title, y):
        y -= 6*mm
        # Section chiziq
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.5)
        c.line(MN_X+PAD, y+1*mm, MN_X+PAD+4*mm, y+1*mm)
        c.setFillColor(DARK)
        c.setFont(BD, S_SEC)
        c.drawString(MN_X+PAD+5.5*mm, y, title.upper())
        y -= 2*mm
        c.setStrokeColor(LGRAY)
        c.setLineWidth(0.8)
        c.line(MN_X+PAD, y, PAGE_W-PAD, y)
        return y - 4*mm

    def mn_entry(title, subtitle, years, desc, y):
        # Sarlavha + yil
        c.setFillColor(DARK)
        c.setFont(BD, S_JOB)
        c.drawString(MN_X+PAD, y, title)
        c.setFillColor(GRAY)
        c.setFont(IT, S_SM)
        rw = c.stringWidth(years, IT, S_SM)
        c.drawString(PAGE_W-PAD-rw, y, years)
        y -= 4.5*mm

        # Subtitle (kompaniya / muassasa)
        if subtitle:
            c.setFillColor(ACCENT)
            c.setFont(BD, S_SM)
            c.drawString(MN_X+PAD, y, subtitle)
            y -= 4*mm

        # Tavsif
        if desc:
            for line in desc.split(','):
                line = line.strip()
                if not line: continue
                c.setFillColor(ACCENT)
                c.setFont(BD, S_BODY)
                c.drawString(MN_X+PAD, y, '•')
                y = mn_wrap(c, line, RG, S_BODY,
                            MN_X+PAD+4.5*mm, y, mn_max-4.5*mm, 4.5*mm, DARK)

        y -= 2*mm
        return y

    # ── EDUCATION ─────────────────────────────────────────────────────────
    edu = pe(data.get('education_list',[]))
    if edu:
        mn_y = mn_sec('Education', mn_y)
        for e in edu:
            yr = e['years'] + (f'  GPA: {e["gpa"]}' if e.get('gpa') else '')
            mn_y = mn_entry(e['degree'], e['institution'], yr, '', mn_y)

    # ── WORK EXPERIENCE ───────────────────────────────────────────────────
    work = pw(data.get('work_list',[]))
    if work:
        mn_y = mn_sec('Work Experience', mn_y)
        for w in work:
            mn_y = mn_entry(w['position'], w['company'], w['years'], w['description'], mn_y)

    # ── CERTIFICATES ──────────────────────────────────────────────────────
    certs = pc(data.get('cert_list',[]))
    if certs:
        mn_y = mn_sec('Certificates', mn_y)
        for cert in certs:
            nm = cert['name'] + (f'  —  {cert["org"]}' if cert.get('org') else '')
            yr = cert.get('year','')
            c.setFillColor(DARK)
            c.setFont(BD, S_BODY)
            c.drawString(MN_X+PAD, mn_y, nm)
            if yr:
                c.setFillColor(GRAY)
                c.setFont(IT, S_SM)
                rw = c.stringWidth(yr, IT, S_SM)
                c.drawString(PAGE_W-PAD-rw, mn_y, yr)
            mn_y -= 5*mm

    # ── HOBBIES ───────────────────────────────────────────────────────────
    hobbies = data.get('hobbies','')
    if hobbies:
        mn_y = mn_sec('Interests', mn_y)
        mn_y = mn_wrap(c, hobbies, RG, S_BODY, MN_X+PAD, mn_y, mn_max, 4.5*mm, DARK)

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
    for sec in doc.sections:
        sec.top_margin    = Cm(0)
        sec.bottom_margin = Cm(1)
        sec.left_margin   = Cm(0)
        sec.right_margin  = Cm(0)
        sec.page_width    = Cm(21)
        sec.page_height   = Cm(29.7)

    CBLU = RGBColor(27,58,107)
    CACC = RGBColor(39,97,171)
    CGLD = RGBColor(233,185,73)
    CWHT = RGBColor(255,255,255)
    CDRK = RGBColor(28,28,28)
    CGRY = RGBColor(90,90,90)

    def hex_fill(cell, hx):
        tcPr = cell._tc.get_or_add_tcPr()
        shd  = OxmlElement('w:shd')
        shd.set(qn('w:val'),'clear')
        shd.set(qn('w:color'),'auto')
        shd.set(qn('w:fill'), hx)
        tcPr.append(shd)

    def set_w(cell, twips):
        tcPr = cell._tc.get_or_add_tcPr()
        tcW  = tcPr.find(qn('w:tcW'))
        if tcW is None:
            tcW = OxmlElement('w:tcW')
            tcPr.append(tcW)
        tcW.set(qn('w:w'), str(twips))
        tcW.set(qn('w:type'), 'dxa')

    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl.allow_autofit = False
    sc = tbl.cell(0,0)
    mc = tbl.cell(0,1)
    set_w(sc, 3570)
    set_w(mc, 8250)
    hex_fill(sc,'1B3A6B')
    hex_fill(mc,'FFFFFF')
    sc.vertical_alignment = WD_ALIGN_VERTICAL.TOP
    mc.vertical_alignment = WD_ALIGN_VERTICAL.TOP

    def rn(p, text, size, bold=False, italic=False, color=CWHT):
        r = p.add_run(text)
        r.font.name  = 'Calibri'
        r.font.size  = Pt(size)
        r.font.bold  = bold
        r.font.italic= italic
        r.font.color.rgb = color
        return r

    def sp(cell, text='', size=9, bold=False, italic=False,
           color=CWHT, sb=0, sa=1, indent=0.4,
           align=WD_ALIGN_PARAGRAPH.LEFT):
        p = cell.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(sb)
        p.paragraph_format.space_after  = Pt(sa)
        p.paragraph_format.left_indent  = Cm(indent)
        if text:
            rn(p, text, size, bold, italic, color)
        return p

    def sb_section(title):
        p = sp(sc, title.upper(), size=8, bold=True, color=CGLD, sb=8, sa=1)
        pPr = p._p.get_or_add_pPr()
        pBdr= OxmlElement('w:pBdr')
        bot = OxmlElement('w:bottom')
        bot.set(qn('w:val'),'single')
        bot.set(qn('w:sz'),'4')
        bot.set(qn('w:space'),'1')
        bot.set(qn('w:color'),'E9B949')
        pBdr.append(bot)
        pPr.append(pBdr)

    def sb_lbl(text):
        sp(sc, text.upper(), size=6.5, bold=True, color=RGBColor(155,184,212), sb=3, sa=0)

    def sb_val(text):
        if text:
            sp(sc, text, size=9, color=CWHT, sa=2)

    # Sidebar — initials
    first = data.get('first_name','')
    last  = data.get('last_name','')
    initials = (first[:1]+last[:1]).upper()
    sp(sc, initials, size=32, bold=True, color=CGLD,
       sb=18, sa=6, align=WD_ALIGN_PARAGRAPH.CENTER, indent=0)

    sb_section('Contact')
    for lbl,key in [('Email','email'),('Phone','phone'),('Address','address'),
                     ('LinkedIn','linkedin'),('GitHub','github'),('Website','website')]:
        v=data.get(key,'')
        if v:
            sb_lbl(lbl)
            sb_val(v)

    sb_section('Personal')
    for lbl,key in [('Date of Birth','dob'),('Nationality','nationality')]:
        v=data.get(key,'')
        if v:
            sb_lbl(lbl)
            sb_val(v)

    langs = pl(data.get('lang_list',[]))
    if langs:
        sb_section('Languages')
        for lg in langs:
            sp(sc, lg['lang'], size=9, bold=True, color=CWHT, sb=3, sa=0)
            dots = lang_dots(lg['level'])
            bar  = '●'*min(dots,5) + '○'*(5-min(dots,5))
            sp(sc, f"{lg['level']}  {bar}", size=8, italic=True, color=CGLD, sa=2)

    skills = psk(data.get('skills_list',[]))
    if skills:
        sb_section('Skills')
        for sk in skills:
            sp(sc, sk['cat'].upper(), size=7.5, bold=True, color=CGLD, sb=3, sa=0)
            sp(sc, sk['sk'], size=9, color=CWHT, sa=2)

    # ── MAIN ──────────────────────────────────────────────────────────────
    mc.paragraphs[0].clear()

    def mp(text='', size=10, bold=False, italic=False,
           color=CDRK, sb=0, sa=2, indent=0.5,
           align=WD_ALIGN_PARAGRAPH.LEFT):
        p = mc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(sb)
        p.paragraph_format.space_after  = Pt(sa)
        p.paragraph_format.left_indent  = Cm(indent)
        if text:
            rn(p, text, size, bold, italic, color)
        return p

    def mn_section(title):
        p = mp(title.upper(), size=11, bold=True, color=CACC, sb=10, sa=2)
        pPr = p._p.get_or_add_pPr()
        pBdr= OxmlElement('w:pBdr')
        bot = OxmlElement('w:bottom')
        bot.set(qn('w:val'),'single')
        bot.set(qn('w:sz'),'6')
        bot.set(qn('w:space'),'1')
        bot.set(qn('w:color'),'2761AB')
        pBdr.append(bot)
        pPr.append(pBdr)

    # ISM
    p = mc.paragraphs[0]
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.left_indent  = Cm(0.5)
    rn(p, first.upper()+' ', S_NAME, bold=True, color=CBLU)
    rn(p, last.upper(),      S_NAME, bold=True, color=CACC)

    if data.get('objective'):
        mp(data['objective'], size=9.5, italic=True, color=CGRY, sa=6)

    edu = pe(data.get('education_list',[]))
    if edu:
        mn_section('Education')
        for e in edu:
            p = mp(sb=4, sa=1)
            rn(p, e['degree'], 10, bold=True, color=CDRK)
            if e.get('years'):
                rn(p, f"  {e['years']}", 8.5, italic=True, color=CGRY)
            mp(e['institution'], size=9, italic=True, color=CGRY, sa=4)

    work = pw(data.get('work_list',[]))
    if work:
        mn_section('Work Experience')
        for w in work:
            p = mp(sb=4, sa=1)
            rn(p, w['position'], 10, bold=True, color=CDRK)
            if w.get('years'):
                rn(p, f"  {w['years']}", 8.5, italic=True, color=CGRY)
            mp(w['company'], size=9, italic=True, color=CGRY, sa=2)
            if w.get('description'):
                for desc in w['description'].split(','):
                    desc=desc.strip()
                    if desc:
                        mp(f'• {desc}', size=9.5, color=CDRK, sa=1, indent=0.8)

    certs = pc(data.get('cert_list',[]))
    if certs:
        mn_section('Certificates')
        for cert in certs:
            t = cert['name']
            if cert.get('org'):  t += f' — {cert["org"]}'
            if cert.get('year'): t += f'  ({cert["year"]})'
            mp(f'• {t}', size=9.5, color=CDRK, sb=2, sa=1, indent=0.8)

    if data.get('hobbies'):
        mn_section('Interests')
        mp(data['hobbies'], size=9.5, color=CDRK, sa=2)

    doc.save(output_path)
