#!/usr/bin/env python3
"""Builds the animated SVGs used by the profile README.

No dependencies.  Run:  python3 tools/build.py
Output lands in ./assets.  Everything is seeded, so a rebuild is byte-identical
unless you change something below.

GitHub strips scripts from READMEs, so every bit of motion here is CSS
keyframes inside the SVG.  Nothing loads from the network.
"""
import html
import os
import random

R = random.Random(0xC0DE)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

BG = "#0d1117"
PANEL = "#0a0d12"
RED = "#f2444c"
DEEP = "#c2202a"
BONE = "#e6dedb"
CYAN = "#18d8f0"
DIM = "#3a2a33"
GREY = "#6e7681"
MONO = 'ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace'
SANS = '"Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif'

BLOG = "https://www.undefinedbehaviors.com"

esc = html.escape


def n(v):
    """Short number formatting for attributes."""
    return f"{v:.1f}".rstrip("0").rstrip(".")


def svg(w, h, label, css, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{esc(label)}" '
        f'xml:space="preserve"><title>{esc(label)}</title>'
        f"<style>{css}</style>{body}</svg>\n"
    )


def write(name, data):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
    print(f"{name:16} {len(data) / 1024:6.1f} KB")


# --------------------------------------------------------------------------
# 1. glitch.svg : the header
# --------------------------------------------------------------------------

GLYPH = {
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
}

TYPED = [
    "offensive security / content engineer",
    "warning: the behavior of this profile is undefined",
    "side effects may include nasal demons",
    "mea culpa.",
]


def glitch():
    W, H = 1200, 400
    word = "RABBITBONG"
    rows = [""] * 7
    for i, ch in enumerate(word):
        for r in range(7):
            rows[r] += GLYPH[ch][r] + ("." if i < len(word) - 1 else "")
    cols = len(rows[0])
    PW, PH = 18, 24
    TX, TY = (W - cols * PW) / 2, 98

    # Each pixel row is drawn as two scanline bars, so the title has 14
    # independent slices that can tear sideways.
    defs = []
    for r in range(7):
        runs, x = [], 0
        while x < cols:
            if rows[r][x] == "#":
                x0 = x
                while x < cols and rows[r][x] == "#":
                    x += 1
                runs.append((x0, x - x0))
            else:
                x += 1
        for k in range(2):
            y = TY + r * PH + k * 12
            rects = "".join(
                f'<rect x="{n(TX + a * PW)}" y="{n(y)}" width="{b * PW}" height="10"/>'
                for a, b in runs
            )
            defs.append(f'<g id="s{r * 2 + k}">{rects}</g>')

    timing = [(R.uniform(3.3, 8.9), -R.uniform(0, 9)) for _ in range(14)]
    layers = []
    for cls, fill in (("lc", CYAN), ("lr", RED), ("lb", BONE)):
        uses = "".join(
            f'<use href="#s{s}" style="animation:g{s % 5} {n(d)}s step-end {n(o)}s infinite"/>'
            for s, (d, o) in enumerate(timing)
        )
        layers.append(f'<g class="{cls}" fill="{fill}">{uses}</g>')

    # background: a wall of hex, with a few bytes that will not sit still
    noise = []
    for i in range(13):
        toks = [R.choice(["??"] + [f"{R.randrange(256):02x}"] * 24) for _ in range(44)]
        noise.append(
            f'<text x="10" y="{26 + i * 30}" textLength="1180" class="nz">{" ".join(toks)}</text>'
        )
    hot = []
    for _ in range(22):
        col, row = R.randrange(44), R.randrange(13)
        hot.append(
            f'<text x="{n(10 + col * 3 * 1180 / 131)}" y="{26 + row * 30}" class="hot" '
            f'fill="{R.choice([RED, RED, CYAN])}" '
            f'style="animation-duration:{n(R.uniform(1.7, 5.3))}s;animation-delay:-{n(R.uniform(0, 5))}s">'
            f"{R.randrange(256):02x}</text>"
        )

    # stuck pixels around the title
    dead = []
    for _ in range(14):
        cx, cy = R.randrange(-2, cols + 2), R.randrange(-1, 8)
        dead.append(
            f'<rect x="{n(TX + cx * PW)}" y="{n(TY + cy * PH + R.choice([0, 12]))}" width="{PW}" height="10" '
            f'fill="{R.choice([RED, CYAN, BONE])}" class="dead" '
            f'style="animation-duration:{n(R.uniform(2.1, 6.7))}s;animation-delay:-{n(R.uniform(0, 6))}s"/>'
        )

    tears = "".join(
        f'<rect class="tear" width="{W}" height="{h}" fill="{c}" '
        f'style="animation:t{i} {d}s step-end -{o}s infinite"/>'
        for i, (h, c, d, o) in enumerate(
            [(4, CYAN, 5.1, 0.4), (9, RED, 7.3, 2.2), (2, BONE, 3.7, 1.1), (14, DEEP, 9.7, 5.0)]
        )
    )

    # typed lines: one <text> per character so the layout never depends on
    # which monospace font the viewer happens to have
    PITCH, X0, Y0 = 13.2, TX + 4 * 13.2, 334
    typed = []
    for li, line in enumerate(TYPED):
        t0 = li * 4 + 0.15
        chars = "".join(
            f'<text x="{n(X0 + i * PITCH)}" y="{Y0}" class="ch" '
            f'style="animation-delay:{t0 + i * 0.04:.2f}s">{esc(c)}</text>'
            for i, c in enumerate(line)
            if c != " "
        )
        cur = (
            f'<rect x="{n(X0 + len(line) * PITCH + 3)}" y="{Y0 - 18}" width="11" height="22" '
            f'fill="{RED}" class="cur" style="animation-delay:{t0 + len(line) * 0.04:.2f}s"/>'
        )
        typed.append(
            f'<g class="ln ln{li}" style="animation-delay:{li * 4}s">{chars}{cur}</g>'
        )

    css = f"""
text{{font:bold 15px {MONO};white-space:pre}}
.nz{{fill:#1c2531}}
.hot{{opacity:0;animation:hot 3s step-end infinite}}
.dead{{opacity:0;animation:dead 4s step-end infinite}}
.lc{{transform:translate(5px,0);opacity:.9;animation:ca 5.3s step-end infinite}}
.lr{{transform:translate(-5px,0);opacity:.9;animation:cb 4.1s step-end infinite}}
.lb{{animation:fk 6.7s step-end infinite}}
.ti{{transform-origin:600px 180px;animation:big 11s step-end infinite}}
.tear{{opacity:0}}
.hud{{font-size:16px;fill:{GREY}}}
.ub{{font-size:27px;fill:{RED}}}
.stop{{fill:{RED};animation:bl 1.3s step-end infinite}}
.pr{{font-size:22px;fill:{RED}}}
.ch{{font-size:22px;fill:{BONE};opacity:0;animation:ch 16s step-end infinite}}
.ln{{opacity:0;animation:win 16s step-end infinite}}
.cur{{opacity:0;animation:cur 16s step-end infinite}}
.roll{{animation:roll 7s linear infinite}}
@keyframes g0{{0%,100%{{transform:translateX(0)}}37%{{transform:translateX(-30px)}}38.2%{{transform:translateX(16px)}}39.4%{{transform:translateX(0)}}}}
@keyframes g1{{0%,100%{{transform:translateX(0)}}71%{{transform:translateX(44px)}}72%{{transform:translateX(-12px)}}73.5%{{transform:translateX(0)}}}}
@keyframes g2{{0%,100%{{transform:translateX(0)}}12%{{transform:translateX(-18px)}}13%{{transform:translateX(0)}}58%{{transform:translateX(60px)}}59%{{transform:translateX(0)}}}}
@keyframes g3{{0%,100%{{transform:translateX(0)}}86%{{transform:translateX(-52px)}}87.5%{{transform:translateX(8px)}}88.5%{{transform:translateX(0)}}}}
@keyframes g4{{0%,100%{{transform:translateX(0)}}24%{{transform:translateX(22px)}}25.5%{{transform:translateX(0)}}49%{{transform:translateX(-8px)}}50%{{transform:translateX(0)}}93%{{transform:translateX(36px)}}94%{{transform:translateX(0)}}}}
@keyframes ca{{0%,100%{{transform:translate(5px,0)}}30%{{transform:translate(16px,-2px)}}31.2%{{transform:translate(5px,0)}}71%{{transform:translate(-10px,3px)}}72.4%{{transform:translate(5px,0)}}}}
@keyframes cb{{0%,100%{{transform:translate(-5px,0)}}44%{{transform:translate(-18px,2px)}}45.5%{{transform:translate(-5px,0)}}83%{{transform:translate(9px,-3px)}}84%{{transform:translate(-5px,0)}}}}
@keyframes fk{{0%,100%{{opacity:1}}52%{{opacity:.55}}52.8%{{opacity:1}}53.6%{{opacity:.2}}54.2%{{opacity:1}}}}
@keyframes big{{0%,100%{{transform:none}}61%{{transform:translate(-14px,0) skewX(-9deg)}}61.9%{{transform:translate(18px,3px) skewX(5deg)}}62.7%{{transform:translate(-4px,-2px)}}63.3%{{transform:none}}}}
@keyframes hot{{0%,100%{{opacity:0}}40%{{opacity:.85}}52%{{opacity:0}}60%{{opacity:.5}}64%{{opacity:0}}}}
@keyframes dead{{0%,100%{{opacity:0}}70%{{opacity:.9}}74%{{opacity:0}}77%{{opacity:.9}}86%{{opacity:0}}}}
@keyframes t0{{0%,100%{{opacity:0}}12%{{opacity:.7;transform:translateY(131px)}}13.2%{{opacity:0}}55%{{opacity:.5;transform:translateY(247px)}}56.5%{{opacity:0}}}}
@keyframes t1{{0%,100%{{opacity:0}}33%{{opacity:.45;transform:translateY(176px)}}34%{{opacity:0}}80%{{opacity:.6;transform:translateY(64px)}}81%{{opacity:0}}}}
@keyframes t2{{0%,100%{{opacity:0}}20%{{opacity:.8;transform:translateY(301px)}}22%{{opacity:0}}67%{{opacity:.8;transform:translateY(118px)}}68.5%{{opacity:0}}}}
@keyframes t3{{0%,100%{{opacity:0}}61%{{opacity:.35;transform:translateY(205px)}}62.5%{{opacity:0}}}}
@keyframes bl{{0%,100%{{opacity:1}}50%{{opacity:.2}}}}
@keyframes ch{{0%{{opacity:1}}24.5%,100%{{opacity:0}}}}
@keyframes win{{0%{{opacity:1}}23%,100%{{opacity:0}}}}
@keyframes cur{{0%,6%,12%,18%{{opacity:1}}3%,9%,15%,21%,100%{{opacity:0}}}}
@keyframes roll{{from{{transform:translateY(-120px)}}to{{transform:translateY(400px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.ln0,.ln0 .ch{{opacity:1}}}}
"""
    body = f"""<defs>
<clipPath id="r"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<pattern id="sc" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".4"/></pattern>
<linearGradient id="rg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".055"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="vg" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>
{"".join(defs)}
</defs>
<g clip-path="url(#r)">
<rect width="{W}" height="{H}" fill="{BG}"/>
{"".join(noise)}{"".join(hot)}
<rect width="{W}" height="{H}" fill="url(#vg)"/>
<text x="{n(TX)}" y="56" class="ub">UB//</text>
<text x="{n(TX + 78)}" y="55" class="hud">undefined behaviors</text>
<text x="{n(W - TX)}" y="55" text-anchor="end" class="hud stop">STOP 0xC0000005 :: STATUS_ACCESS_VIOLATION</text>
<g class="ti">{"".join(dead)}{"".join(layers)}</g>
<text x="{n(TX)}" y="334" class="pr">kd&gt;</text>
{"".join(typed)}
<text x="{n(W - TX)}" y="334" text-anchor="end" class="hud">pid 0x52414242 :: ring 0</text>
{tears}
<rect class="roll" width="{W}" height="120" fill="url(#rg)"/>
<rect width="{W}" height="{H}" fill="url(#sc)"/>
</g>"""
    write(
        "glitch.svg",
        svg(W, H, "RABBITBONG. UB// undefined behaviors. offensive security / content engineer.", css, body),
    )


# --------------------------------------------------------------------------
# 2. bugcheck.svg : red screen of death
# --------------------------------------------------------------------------

# QR for https://www.undefinedbehaviors.com/ (version 3, EC level M).
# Generated once with the `qrcode` npm package and decoded back with jsQR.
QR = [
    "11111110001110011011101111111", "10000010000010000000001000001",
    "10111010111000101001001011101", "10111010111100000100001011101",
    "10111010101101110111101011101", "10000010100101111010001000001",
]


def load_qr():
    """The full matrix lives in tools/qr.txt so this file stays readable."""
    with open(os.path.join(ROOT, "tools", "qr.txt"), encoding="utf-8") as f:
        rows = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    assert rows[: len(QR)] == QR and all(len(r) == len(rows) for r in rows)
    return rows


def bugcheck():
    W, H = 1200, 664
    # signed char: 127 + 1 is undefined behavior, and here is what it looks like
    frames = ["0", "9", "23", "41", "64", "87", "99", "99", "99", "100",
              "113", "127", "-128", "-128", "-127", "NaN"]
    STEP = 60
    nums = "".join(
        f'<text x="170" y="{424 + i * STEP}" text-anchor="end" class="p">{f}</text>'
        for i, f in enumerate(frames)
    )

    qr = load_qr()
    M, QX, QY = 5, 86, 458
    side = (len(qr) + 8) * M
    mods = []
    for y, row in enumerate(qr):
        x = 0
        while x < len(row):
            if row[x] == "1":
                x0 = x
                while x < len(row) and row[x] == "1":
                    x += 1
                mods.append(
                    f'<rect x="{QX + (x0 + 4) * M}" y="{QY + (y + 4) * M}" '
                    f'width="{(x - x0) * M}" height="{M}"/>'
                )
            else:
                x += 1

    css = f"""
text{{font:400 19px {SANS};fill:#f6ecea}}
.rb{{font:bold 58px {MONO};white-space:pre}}
.p{{font-size:30px}}
.wm{{font:bold 250px {MONO};fill:#000;opacity:.13}}
.b{{font-weight:700}}
.all{{animation:j 7s step-end infinite}}
.e1{{animation:e1 5.2s step-end infinite}}
.e2{{opacity:0;animation:e2 5.2s step-end infinite}}
.ear{{transform-origin:214px 128px;animation:ear 3.9s step-end infinite}}
.cnt{{animation:cnt {len(frames) * 0.7:.1f}s steps({len(frames)}) infinite}}
.tear{{opacity:0}}
@keyframes j{{0%,100%{{transform:none}}47%{{transform:translate(-9px,0)}}47.7%{{transform:translate(6px,1px)}}48.4%{{transform:none}}83%{{transform:translate(4px,0)}}83.5%{{transform:none}}}}
@keyframes e1{{0%,100%{{opacity:1}}62%{{opacity:0}}68%{{opacity:1}}}}
@keyframes e2{{0%,100%{{opacity:0}}62%{{opacity:1}}68%{{opacity:0}}}}
@keyframes ear{{0%,100%{{transform:none}}40%{{transform:rotate(-4deg)}}43%{{transform:none}}46%{{transform:rotate(-4deg)}}49%{{transform:none}}}}
@keyframes cnt{{to{{transform:translateY(-{len(frames) * STEP}px)}}}}
@keyframes t0{{0%,100%{{opacity:0}}27%{{opacity:.3;transform:translateY(300px)}}28%{{opacity:0}}47%{{opacity:.35;transform:translateY(96px)}}48.4%{{opacity:0}}}}
@keyframes t1{{0%,100%{{opacity:0}}47%{{opacity:.5;transform:translateY(388px)}}48.4%{{opacity:0}}90%{{opacity:.4;transform:translateY(212px)}}91%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""
    body = f"""<defs>
<clipPath id="r"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<clipPath id="w"><rect x="60" y="388" width="116" height="48"/></clipPath>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#b3182a"/><stop offset="1" stop-color="#7a0e17"/></linearGradient>
<pattern id="sc" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".16"/></pattern>
</defs>
<g clip-path="url(#r)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<text x="{W - 60}" y="262" text-anchor="end" class="wm">UB//</text>
<g class="all">
<text x="214" y="124" text-anchor="middle" class="rb ear">(\\_/)</text>
<text x="214" y="184" text-anchor="middle" class="rb e1">(x.x)</text>
<text x="214" y="184" text-anchor="middle" class="rb e2">(x.-)</text>
<text x="214" y="244" text-anchor="middle" class="rb">(")(")</text>
<text x="86" y="318" class="p">Your profile ran into a problem it caused on purpose.</text>
<text x="86" y="360" class="p">We're just collecting some error info, and then we'll do it again.</text>
<g clip-path="url(#w)"><g class="cnt">{nums}</g></g>
<text x="176" y="424" class="p">% complete</text>
<text x="{QX + side + 30}" y="496">For more information about this issue and possible fixes, visit</text>
<text x="{QX + side + 30}" y="524" class="b">{BLOG}</text>
<text x="{QX + side + 30}" y="572">If you call a support person, give them this info:</text>
<text x="{QX + side + 30}" y="600">Stop code: <tspan class="b">MEA_CULPA</tspan></text>
<text x="{QX + side + 30}" y="628">What failed: <tspan class="b">undefinedbehaviors.sys</tspan></text>
</g>
<rect class="tear" width="{W}" height="6" fill="#fff" style="animation:t0 7s step-end infinite"/>
<rect class="tear" width="{W}" height="16" fill="#000" style="animation:t1 7s step-end infinite"/>
<rect width="{W}" height="{H}" fill="url(#sc)"/>
<rect x="{QX}" y="{QY}" width="{side}" height="{side}" fill="#f6ecea"/>
<g fill="#22050a">{"".join(mods)}</g>
</g>"""
    write(
        "bugcheck.svg",
        svg(W, H, "Red screen of death. Your profile ran into a problem it caused on purpose. "
                  "Stop code: MEA_CULPA. What failed: undefinedbehaviors.sys. "
                  f"The QR code goes to {BLOG}", css, body),
    )


# --------------------------------------------------------------------------
# 3. hexdump.svg : `db` over the bio.  The hex is real; decode it.
# --------------------------------------------------------------------------

BIO = ("UB// undefined behaviors :: offensive security / content engineer :: "
       "i write exploits, then i write about them :: mea culpa.")
# The ASCII column refuses to show this part.  The bytes are still there.
SECRET = "you read hex for fun. same."


def hexdump():
    W = 1200
    pad = lambda s: s + b"\0" * (-len(s) % 16)
    data = pad(BIO.encode()) + pad(SECRET.encode())
    hidden_from = len(pad(BIO.encode())) // 16
    nrows = len(data) // 16
    P, X0, Y0, DY = 13, 54, 132, 31
    XH, XA = X0 + 19 * P, X0 + 68 * P
    H = Y0 + nrows * DY + 58

    def bx(i):  # x of byte i within a row
        return XH + i * 3 * P

    rows = []
    for r in range(nrows):
        chunk = data[r * 16:(r + 1) * 16]
        hx = " ".join(f"{b:02x}" for b in chunk[:8]) + "-" + " ".join(f"{b:02x}" for b in chunk[8:])
        if r >= hidden_from:
            asc, acls = "." * 16, "dim"
        else:
            asc, acls = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk), "asc"
        y = Y0 + r * DY
        rows.append(
            f'<g class="row" style="animation-delay:{0.3 + r * 0.16:.2f}s">'
            f'<text x="{X0}" y="{y}" textLength="{17 * P}" class="ad">ffffb001`c0de{r * 16:04x}</text>'
            f'<text x="{XH}" y="{y}" textLength="{47 * P}" class="hx">{hx}</text>'
            f'<text x="{XA}" y="{y}" textLength="{16 * P}" class="{acls}">{esc(asc)}</text></g>'
        )

    # bytes that read back as ?? now and then
    cor = []
    cells = R.sample([(r, c) for r in range(nrows) for c in range(16)], 16)
    for k, (r, c) in enumerate(cells):
        y = Y0 + r * DY
        cor.append(
            f'<g class="cor" style="animation:co{k % 3} {n(R.uniform(4.5, 11))}s step-end {n(R.uniform(3, 9))}s infinite">'
            f'<rect x="{bx(c) - 2}" y="{y - 21}" width="{2 * P + 4}" height="28" fill="{PANEL}"/>'
            f'<text x="{bx(c)}" y="{y}" textLength="{2 * P}" class="bad">??</text>'
            f'<rect x="{XA + c * P - 1}" y="{y - 21}" width="{P + 2}" height="28" fill="{PANEL}"/>'
            f'<text x="{XA + c * P}" y="{y}" class="bad">?</text></g>'
        )

    # something is walking the buffer
    hops = [(R.randrange(nrows), R.randrange(16)) for _ in range(25)]
    kf = "".join(
        f"{i * 4}%{{transform:translate({bx(c) - 4}px,{Y0 + r * DY - 22}px)}}"
        for i, (r, c) in enumerate(hops)
    )
    yl = Y0 + nrows * DY + 8
    css = f"""
text{{font:500 21px {MONO};white-space:pre}}
.tt{{font-size:15px;fill:{GREY}}}
.pr{{fill:{RED};font-weight:700}}
.cmd{{fill:{BONE}}}
.ad{{fill:{GREY}}}
.hx{{fill:#b8aeac}}
.asc{{fill:{BONE}}}
.dim{{fill:{DIM}}}
.bad{{fill:{RED};font-weight:700}}
.row{{opacity:0;animation:in .01s linear forwards}}
.cor{{opacity:0}}
.rd{{opacity:0;animation:rd 12s step-end 2.4s infinite}}
.cur{{animation:bl 1s step-end infinite}}
@keyframes in{{to{{opacity:1}}}}
@keyframes co0{{0%,100%{{opacity:0}}63%{{opacity:1}}66%{{opacity:0}}70%{{opacity:1}}79%{{opacity:0}}}}
@keyframes co1{{0%,100%{{opacity:0}}18%{{opacity:1}}31%{{opacity:0}}}}
@keyframes co2{{0%,100%{{opacity:0}}40%{{opacity:1}}42%{{opacity:0}}44%{{opacity:1}}46%{{opacity:0}}48%{{opacity:1}}55%{{opacity:0}}}}
@keyframes rd{{{kf}0%,100%{{opacity:1}}}}
@keyframes bl{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.row{{opacity:1}}}}
"""
    body = f"""<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{PANEL}" stroke="#2a1a20"/>
<path d="M.5 44h{W - 1}" stroke="#2a1a20"/>
<circle cx="28" cy="22" r="6" fill="{RED}"/><circle cx="50" cy="22" r="6" fill="{DIM}"/><circle cx="72" cy="22" r="6" fill="{DIM}"/>
<text x="{W / 2}" y="27" text-anchor="middle" class="tt">rabbitbong.dmp :: kd</text>
<text x="{X0}" y="{Y0 - DY - 8}" class="pr">kd&gt;</text>
<text x="{X0 + 5 * P}" y="{Y0 - DY - 8}" class="cmd">db rabbitbong L{len(data):x}</text>
{"".join(rows)}{"".join(cor)}
<rect class="rd" width="{2 * P + 8}" height="30" rx="3" fill="{CYAN}" fill-opacity=".12" stroke="{CYAN}" stroke-width="1.5"/>
<text x="{X0}" y="{yl + 22}" class="pr">kd&gt;</text>
<rect class="cur" x="{X0 + 5 * P}" y="{yl + 3}" width="12" height="24" fill="{RED}"/>"""
    write(
        "hexdump.svg",
        svg(W, H, f"Debugger hex dump of the bio. ASCII column reads: {BIO} "
                  "The last two rows are not shown in ASCII; decode the hex.", css, body),
    )


# --------------------------------------------------------------------------
# 4. rabbit-run.svg : footer.  The process is still running.
# --------------------------------------------------------------------------

TAPE = [
    "segmentation fault (core dumped)", "free(): invalid pointer",
    "it works on my machine", "STATUS_ACCESS_VIOLATION", "here be nasal demons",
    "double free or corruption (!prev)", "signed overflow is a lifestyle",
    "mea culpa",
]


def rabbit_run():
    W, H = 1200, 118
    P = 10.2
    line = "".join(f"{t}  //  " for t in TAPE)
    tw = len(line) * P
    spans = "".join(f'{esc(t)}  <tspan class="sl">//</tspan>  ' for t in TAPE)
    tape = "".join(
        f'<text x="{n(i * tw)}" y="100" textLength="{n(tw)}" class="tp">{spans}</text>'
        for i in range(2 + int(W // tw))
    )
    css = f"""
text{{font:bold 17px {MONO};white-space:pre}}
.tp{{fill:{GREY}}}
.sl,.rb{{fill:{RED}}}
.tape{{animation:tape {n(tw / 26)}s linear infinite}}
.hx{{animation:hx 15s linear infinite}}
.hy{{animation:hy .34s ease-out infinite alternate}}
.ey{{animation:bk 3.1s step-end infinite}}
@keyframes tape{{to{{transform:translateX(-{n(tw)}px)}}}}
@keyframes hx{{from{{transform:translateX(-90px)}}to{{transform:translateX(1260px)}}}}
@keyframes hy{{to{{transform:translateY(-16px)}}}}
@keyframes bk{{0%,100%{{opacity:1}}92%{{opacity:0}}95%{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.hx{{transform:translateX(560px)}}}}
"""
    body = f"""<path d="M0 72h{W}" stroke="{GREY}" stroke-width="1.5" stroke-dasharray="2 9" opacity=".7"/>
<g class="hx"><g class="hy">
<text x="0" y="42" class="rb">(\\_/)</text>
<text x="0" y="62" class="rb">(   )</text>
<text x="0" y="62" class="rb ey"> o.o</text>
</g></g>
<g class="tape">{tape}</g>"""
    write("rabbit-run.svg", svg(W, H, "A rabbit hopping over a ticker tape of error messages. The process is still running.", css, body))


if __name__ == "__main__":
    glitch()
    bugcheck()
    hexdump()
    rabbit_run()
