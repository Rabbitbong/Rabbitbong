#!/usr/bin/env python3
"""Generates the three pieces in the gallery README.

    python3 tools/art.py              write the three to ./assets
    python3 tools/art.py mono         write one piece by name
    python3 tools/art.py --preview D  write to D with motion forced on
                                      (ignores prefers-reduced-motion)

No dependencies.  Seeded, so a rebuild is byte-identical.
All three pieces come out of this file.
"""
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
FORCE_MOTION = False

INK = "#0c0e12"
BONE = "#e9e1d6"
PAPER = "#efe6d2"
BLACK = "#14110f"
RED = "#f2444c"
PAINT_RED = "#d7332c"


def reduced(rules=""):
    """Still frame for viewers who asked their OS for less motion."""
    if FORCE_MOTION:
        return ""
    return f"@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}{rules}}}"


def svg(w, h, title, css, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{title}"><title>{title}</title><style>{css}</style>{body}</svg>\n'
    )


def write(name, data):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(data)
    print(f"{name:34} {len(data) / 1024:6.1f} KB")


# --------------------------------------------------------------------------
# (off the wall)  Everything I almost said
#
# Replaced as piece I by "Mono no aware".  Still buildable by name:
#     python3 tools/art.py almost
#
# One red line crosses the canvas: the sentence that got written.  At every
# step along it, the other continuations fan out, live for a moment near the
# pen, and decay into residue behind it.
# --------------------------------------------------------------------------

def almost():
    W, H = 1200, 680
    R = random.Random(11)

    def y(x):
        return 340 + 96 * math.sin(x / 190 + 0.6) + 38 * math.sin(x / 71 + 2.1) + 13 * math.sin(x / 29)

    pts = [(-40 + 8 * i, y(-40 + 8 * i)) for i in range(161)]
    main = "M" + " L".join(f"{x:.0f},{v:.1f}" for x, v in pts)

    paths, dots = [], []

    def walk(x, v, h, length, side):
        p = [(x, v)]
        for _ in range(max(2, int(length / 11))):
            h += R.gauss(0, 0.14) - side * 0.026  # bend back toward "forward"
            x += 11 * math.cos(h)
            v += 11 * math.sin(h)
            p.append((x, v))
        return p

    def emit(p):
        op = R.uniform(0.35, 0.95)
        d = "M" + " L".join(f"{x:.0f},{v:.0f}" for x, v in p)
        paths.append(f'<path d="{d}" stroke-width="{R.uniform(0.7, 1.8):.1f}" opacity="{op:.2f}"/>')
        x, v = p[-1]
        fill = f' fill="{RED}"' if R.random() < 0.13 else ""
        dots.append(f'<circle cx="{x:.0f}" cy="{v:.0f}" r="{R.uniform(1.3, 3.4):.1f}" opacity="{op:.2f}"{fill}/>')

    for i in range(2, len(pts) - 2, 3):
        x, v = pts[i]
        tang = math.atan2(pts[i + 1][1] - pts[i - 1][1], pts[i + 1][0] - pts[i - 1][0])
        for _ in range(R.randint(4, 9)):
            side = R.choice((-1, 1))
            length = min(330, R.lognormvariate(4.45, 0.62))
            p = walk(x, v, tang + side * math.radians(R.uniform(12, 84)), length, side)
            emit(p)
            if R.random() < 0.4 and len(p) > 4:  # alternatives have alternatives
                j = R.randrange(2, len(p) - 1)
                h = math.atan2(p[j][1] - p[j - 1][1], p[j][0] - p[j - 1][0])
                s2 = R.choice((-1, 1))
                emit(walk(*p[j], h + s2 * math.radians(R.uniform(22, 62)), length * R.uniform(0.3, 0.6), s2))

    # the pen: x moves linearly, y follows the line
    DRAW = 70  # percent of the cycle spent writing
    kf = "".join(
        f"{DRAW * k / 44:.2f}%{{transform:translate({-40 + 1320 * k / 44:.0f}px,{y(-40 + 1320 * k / 44):.1f}px)}}"
        for k in range(45)
    )
    still_x = 760
    css = f"""
.all{{animation:fade 20s linear infinite}}
.wp{{transform:translateX({still_x}px);animation:wp 20s linear infinite}}
.pen{{transform:translate({still_x}px,{y(still_x):.1f}px);animation:pen 20s linear infinite}}
.halo{{animation:halo 1.6s ease-in-out infinite alternate}}
@keyframes wp{{0%{{transform:translateX(-40px)}}{DRAW}%,100%{{transform:translateX(1280px)}}}}
@keyframes pen{{{kf}100%{{transform:translate(1280px,{y(1280):.1f}px)}}}}
@keyframes fade{{0%,88%{{opacity:1}}97%,100%{{opacity:0}}}}
@keyframes halo{{from{{opacity:.35}}to{{opacity:.9}}}}
{reduced()}
"""
    body = f"""<defs>
<linearGradient id="wg"><stop offset="0" stop-color="#fff"/><stop offset=".965" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="bg"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".72" stop-color="#fff"/><stop offset=".95" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="vg" cx=".5" cy=".5" r=".8"><stop offset=".5" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".7"/></radialGradient>
<radialGradient id="hg"><stop offset="0" stop-color="{RED}" stop-opacity=".9"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
<filter id="bl" x="-5%" y="-40%" width="110%" height="180%"><feGaussianBlur stdDeviation="7"/></filter>
<mask id="wipe" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect class="wp" x="-1320" width="1320" height="{H}" fill="url(#wg)"/></mask>
<mask id="band" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect class="wp" x="-400" width="420" height="{H}" fill="url(#bg)"/></mask>
<g id="gh"><g fill="none" stroke="{BONE}" stroke-linecap="round" stroke-linejoin="round">{"".join(paths)}</g><g fill="{BONE}">{"".join(dots)}</g></g>
</defs>
<rect width="{W}" height="{H}" rx="4" fill="{INK}"/>
<g class="all">
<use href="#gh" opacity=".25" mask="url(#wipe)"/>
<use href="#gh" mask="url(#band)"/>
<g mask="url(#wipe)" fill="none" stroke="{RED}" stroke-linecap="round" stroke-linejoin="round">
<path d="{main}" stroke-width="9" opacity=".55" filter="url(#bl)"/>
<path d="{main}" stroke-width="3.4"/>
</g>
<g class="pen"><circle class="halo" r="34" fill="url(#hg)"/><circle r="5.5" fill="#fff"/></g>
</g>
<rect width="{W}" height="{H}" rx="4" fill="url(#vg)"/>"""
    write("i-everything-i-almost-said.svg", svg(W, H, "Everything I almost said", css, body))


# --------------------------------------------------------------------------
# I.  Mono no aware
#
# The ache of things passing.  A README animation normally loops forever,
# which is the opposite of the idea, so this one does not loop.  It runs once:
# the sun goes down, every blossom lets go, the last petal falls on its own,
# and then nothing in the file moves again.  Reloading the page is the only
# way to see it bloom, and it will end again.
# --------------------------------------------------------------------------

def mono():
    W, H, HZ = 1200, 680, 452
    R = random.Random(41)
    SUMI = "#05060a"
    PINKS = ("#f6c3cc", "#fbe6e6", "#f0a9b8")
    SUNX, SUNY, SUNR = 838, 300, 176
    T_SUN, STORM, T_LAST = 125, 92, 172  # seconds

    # ---- the branch: a gnarled random walk that forks and thins
    segs, spots = [], []

    def limb(x, y, ang, w, left, depth):
        while left > 0 and w > 1.1:
            seg = R.uniform(24, 46) * (1 if depth == 0 else 0.8)
            ang += R.gauss(0, 0.2)
            if depth == 0:
                ang = max(-0.15, min(0.6, ang))
            if y > HZ - 90:
                ang -= 0.4
            if y < 26:
                ang += 0.4
            nx, ny = x + seg * math.cos(ang), y + seg * math.sin(ang)
            segs.append((x, y, nx, ny, w))
            if w < 7.5:
                spots.append((nx, ny))
            left -= seg
            w *= 0.945 if depth == 0 else 0.88
            if depth < 3 and R.random() < (0.45 if depth == 0 else 0.32):
                side = R.choice((-1, 1))
                limb(nx, ny, ang + side * R.uniform(0.45, 1.0), w * 0.6, left * R.uniform(0.4, 0.7), depth + 1)
            x, y = nx, ny
        spots.append((x, y))

    limb(-30, 64, 0.32, 25, 880, 0)
    wood = "".join(f'<path d="M{a:.0f} {b:.0f}L{c:.0f} {d:.0f}" stroke-width="{w:.1f}"/>' for a, b, c, d, w in segs)

    flowers, buds = [], []
    for x, y in spots:
        if R.random() < 0.78:
            for _ in range(R.choice((1, 1, 2, 3))):
                flowers.append((x + R.gauss(0, 9), y + R.gauss(0, 9)))
        else:
            buds.append((x + R.gauss(0, 4), y + R.gauss(0, 4), R.uniform(2.2, 3.6)))

    # ---- when each blossom lets go: a slow start, a storm, stragglers, one last
    def when():
        u = R.random()
        if u < 0.15:
            return R.uniform(-9, 60)
        if u < 0.80:
            return min(150, max(40, R.gauss(STORM, 17)))
        return R.uniform(105, 158)

    last = max(range(len(flowers)), key=lambda i: flowers[i][0])
    bloom, petals, rings, still = [], [], [], 0
    for i, (x, y) in enumerate(flowers):
        t = T_LAST if i == last else when()
        bloom.append(
            f'<g transform="translate({x:.0f} {y:.0f}) rotate({R.uniform(0, 360):.0f}) scale({R.uniform(0.75, 1.35):.2f})">'
            f'<use href="#bl" class="fw" fill="{R.choice(PINKS)}" style="animation-delay:{t:.1f}s"/></g>'
        )
        for j in range(1 if i == last else 2):
            tp = t + j * R.uniform(0.25, 0.7)
            gust = abs(tp - STORM) < 22 and i != last
            fall = 17 if i == last else R.uniform(6.5, 9.5) if gust else R.uniform(10, 15)
            x0, y0 = x + R.gauss(0, 5), y + R.gauss(0, 5)
            dx = 70 if i == last else R.uniform(180, 560) if gust else R.uniform(40, 240)
            y1 = R.uniform(HZ + 22, H - 16)
            x1, sx, sy = x0 + dx, dx / 100, (y1 - y0) / 100
            hold = ""
            if 8 < tp < 60 and still < 12:  # a few caught mid-air for the motionless version
                still += 1
                hold = f" h{still % 3}"
            petals.append(
                f'<g transform="translate({x0:.0f} {y0:.0f}) scale({sx:.3f} {sy:.3f})">'
                f'<g class="fa{hold}" style="animation-delay:{tp:.1f}s;animation-duration:{fall:.1f}s">'
                f'<g transform="scale({1 / sx:.3f} {1 / sy:.3f})">'
                f'<g class="s{R.randrange(4)}" style="animation-delay:{tp:.1f}s,{tp + fall:.1f}s;animation-duration:{fall:.1f}s,4s">'
                f'<use href="#pf" fill="{R.choice(PINKS)}" transform="rotate({R.uniform(0, 360):.0f})"/></g></g></g></g>'
            )
            if x1 < W + 10:
                rx = 92 * (0.45 + 0.9 * (y1 - HZ) / (H - HZ))
                rings.append(
                    f'<ellipse class="rp" cx="{x1:.0f}" cy="{y1 + 3:.0f}" rx="{rx:.0f}" ry="{rx * 0.2:.0f}" '
                    f'style="animation-delay:{tp + fall:.1f}s"/>'
                )
    budsvg = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#e2869a"/>' for x, y, r in buds)
    print(f"  mono: {len(flowers)} blossoms, {len(petals)} petals, {len(buds)} buds that stay")

    # ---- the sun going down, and what the water makes of it
    def glitter(cx, count, wmax, cls, fill):
        out, yb = [], HZ + 8.0
        for j in range(count):
            hgt, wdt = 3 + j * 0.9, R.uniform(wmax * 0.25, wmax) * (1 - j * 0.045)
            q = (5, 7, 11, 13)[j % 4]
            out.append(
                f'<rect class="sh" x="{cx + R.gauss(0, 14) - wdt / 2:.0f}" y="{yb:.0f}" width="{wdt:.0f}" height="{hgt:.1f}" '
                f'rx="{hgt / 2:.1f}" opacity="{0.75 - j * 0.055:.2f}" '
                f'style="animation-duration:{q}s;animation-iteration-count:{200 // q}"/>'
            )
            yb += hgt + 5 + j * 1.6
        return f'<g class="{cls}" fill="{fill}">{"".join(out)}</g>'

    MX, MY = 1046, 108
    waves = "".join(
        f'<path d="M{x:.0f} {y:.0f}h{20 + 90 * (y - HZ) / (H - HZ) * R.uniform(0.4, 1):.0f}" opacity="{R.uniform(0.05, 0.14):.2f}"/>'
        for x, y in ((R.uniform(-20, W), R.uniform(HZ + 6, H)) for _ in range(70))
    )
    stars = "".join(
        f'<circle class="st" cx="{R.uniform(0, W):.0f}" cy="{R.uniform(4, HZ - 26):.0f}" r="{R.uniform(0.7, 1.9):.1f}" '
        f'fill-opacity="{R.uniform(0.35, 0.95):.2f}" style="animation-delay:{R.uniform(98, 168):.0f}s"/>'
        for _ in range(90)
    )

    tumble = []
    for v in range(4):
        turn, rot, frames = (1, -1)[v % 2], 0, []
        for j in range(1, 7):
            rot += turn * R.uniform(50, 105)
            frames.append(
                f"{j * 14}%{{transform:translateX({(1, -1)[j % 2] * R.uniform(11, 26):.0f}px) scale(1,1) "
                f"rotate({rot:.0f}deg) scale({(1, 0.3)[j % 2]},1)}}"
            )
        tumble.append(
            f"@keyframes sw{v}{{0%{{transform:translateX(0px) scale(1,1) rotate(0deg) scale(1,1)}}{''.join(frames)}"
            f"100%{{transform:translateX(0px) scale(1,.45) rotate({rot + turn * 70:.0f}deg) scale(1,1)}}}}"
            f".s{v}{{animation:sw{v} ease-in-out 1 forwards,fo linear 1 forwards}}"
        )

    css = f"""
.fa{{opacity:0;animation:fa cubic-bezier(.35,0,.75,.9) 1 forwards}}
.fw{{animation:fw 1.6s ease-in 1 forwards}}
.rp{{fill:none;stroke:{BONE};stroke-width:1.3;vector-effect:non-scaling-stroke;opacity:0;transform-box:fill-box;transform-origin:center;animation:rp 3.8s cubic-bezier(.1,.6,.3,1) 1}}
.sun{{animation:set {T_SUN}s cubic-bezier(.45,0,.9,.7) 1 forwards}}
.glow,.bars,.rimS{{animation:out {T_SUN - 7}s ease-in 1 forwards}}
.night{{opacity:0;animation:night 150s ease-in-out 1 forwards}}
.moon,.mbars{{opacity:0;animation:in 50s ease-out 98s 1 forwards}}
.rimM{{opacity:0;animation:rim 60s linear 95s 1 forwards}}
.st{{opacity:0;animation:in 7s ease-out 1 forwards}}
.sh{{transform-box:fill-box;transform-origin:center;animation:sh ease-in-out}}
@keyframes fa{{from{{opacity:1;transform:translate(0,0)}}to{{opacity:1;transform:translate(100px,100px)}}}}
@keyframes fo{{to{{opacity:0}}}}
@keyframes fw{{to{{opacity:0;transform:scale(.3)}}}}
@keyframes rp{{from{{transform:scale(.05);opacity:.75}}to{{transform:scale(1);opacity:0}}}}
@keyframes set{{to{{transform:translateY(345px)}}}}
@keyframes out{{to{{opacity:0}}}}
@keyframes in{{to{{opacity:1}}}}
@keyframes night{{to{{opacity:.8}}}}
@keyframes rim{{to{{opacity:.6}}}}
@keyframes sh{{0%,100%{{transform:scaleX(1)}}50%{{transform:scaleX(.7)}}}}
{"".join(tumble)}
{reduced(".h0{opacity:1;transform:translate(28px,28px)}.h1{opacity:1;transform:translate(52px,52px)}.h2{opacity:1;transform:translate(76px,76px)}")}
"""
    body = f"""<desc>This animation runs once, for about three minutes, and then stops. Reload to see it again.</desc>
<defs>
<clipPath id="f"><rect width="{W}" height="{H}" rx="4"/></clipPath>
<clipPath id="sky"><rect width="{W}" height="{HZ}"/></clipPath>
<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#101833"/><stop offset=".7" stop-color="#1c2a4f"/><stop offset="1" stop-color="#2b3d6c"/></linearGradient>
<linearGradient id="wg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#18234a"/><stop offset="1" stop-color="#080c1c"/></linearGradient>
<linearGradient id="sn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e2443a"/><stop offset="1" stop-color="#b3202b"/></linearGradient>
<radialGradient id="gl"><stop offset=".45" stop-color="#d7332c" stop-opacity=".28"/><stop offset="1" stop-color="#d7332c" stop-opacity="0"/></radialGradient>
<radialGradient id="mg"><stop offset=".3" stop-color="#cfdcff" stop-opacity=".22"/><stop offset="1" stop-color="#cfdcff" stop-opacity="0"/></radialGradient>
<path id="pt" d="M0 0C-5-4-6-11-1.5-13L0-11L1.5-13C6-11 5-4 0 0Z"/>
<path id="pf" d="M0 11C-8.5 4.2-10.2-7.6-2.6-11L0-7.6L2.6-11C10.2-7.6 8.5 4.2 0 11Z"/>
<g id="bl"><use href="#pt"/><use href="#pt" transform="rotate(72)"/><use href="#pt" transform="rotate(144)"/><use href="#pt" transform="rotate(216)"/><use href="#pt" transform="rotate(288)"/><circle r="2.3" fill="#b3202b"/></g>
</defs>
<g clip-path="url(#f)">
<rect width="{W}" height="{HZ}" fill="url(#sg)"/>
<rect class="night" width="{W}" height="{HZ}" fill="#060a1a"/>
<g fill="{BONE}">{stars}</g>
<g class="moon"><circle cx="{MX}" cy="{MY}" r="110" fill="url(#mg)"/><circle cx="{MX}" cy="{MY}" r="30" fill="#eef1fb"/></g>
<g clip-path="url(#sky)"><g class="sun"><circle class="glow" cx="{SUNX}" cy="{SUNY}" r="{SUNR * 2}" fill="url(#gl)"/><circle cx="{SUNX}" cy="{SUNY}" r="{SUNR}" fill="url(#sn)"/></g></g>
<rect y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#wg)"/>
<rect class="night" y="{HZ}" width="{W}" height="{H - HZ}" fill="#04060f"/>
<path d="M0 {HZ}H{W}" stroke="#40548c" opacity=".7"/>
{glitter(SUNX, 11, 300, "bars", "#d7332c")}
{glitter(MX, 7, 90, "mbars", "#cfdcff")}
<g stroke="{BONE}" stroke-width="1.2" stroke-linecap="round">{waves}</g>
{"".join(rings)}
<g fill="none" stroke-linecap="round"><g class="rimS" stroke="#8f2f3c" opacity=".75" transform="translate(1.6 2.2)">{wood}</g><g class="rimM" stroke="#9fb4e6" transform="translate(1.5 -1.8)">{wood}</g><g stroke="{SUMI}">{wood}</g></g>
{budsvg}{"".join(bloom)}
{"".join(petals)}
<g transform="translate(1140 624) rotate(-4)"><rect x="-17" y="-17" width="34" height="34" rx="4" fill="#d7332c"/><path d="M-11-11H11V11H-11Z" fill="none" stroke="{BONE}" stroke-width="1.4" opacity=".7"/><path d="M-5 7V-6H6M-5 0H3" fill="none" stroke="{BONE}" stroke-width="3" stroke-linecap="square"/></g>
</g>"""
    write("i-mono-no-aware.svg", svg(W, H, "Mono no aware", css, body))


# --------------------------------------------------------------------------
# II.  Two readings of the same sentence
#
# Two sets of plain concentric rings drift across each other.  Nothing in the
# file describes the patterns you see; they only exist in the overlap.
# --------------------------------------------------------------------------

def moire():
    W, H = 1200, 680

    def rings(spacing, count):
        return "".join(f'<circle r="{spacing * (i + 0.5):g}"/>' for i in range(count))

    css = f"""
.b{{mix-blend-mode:difference}}
.sun{{mix-blend-mode:multiply}}
.ax{{animation:x 23s ease-in-out infinite alternate}}
.ay{{animation:y 17s ease-in-out infinite alternate}}
.bx{{animation:x 29s ease-in-out -9s infinite alternate-reverse}}
.by{{animation:y 19s ease-in-out -4s infinite alternate}}
.sx{{animation:x 41s ease-in-out -20s infinite alternate}}
.sy{{animation:y 31s ease-in-out -11s infinite alternate-reverse}}
@keyframes x{{from{{transform:translateX(-150px)}}to{{transform:translateX(150px)}}}}
@keyframes y{{from{{transform:translateY(-95px)}}to{{transform:translateY(95px)}}}}
{reduced(".ax{transform:translateX(-60px)}.by{transform:translateY(50px)}")}
"""
    body = f"""<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="4"/></clipPath></defs>
<g clip-path="url(#c)" style="isolation:isolate">
<rect width="{W}" height="{H}" fill="{PAPER}"/>
<g class="ax"><g class="ay"><g transform="translate(440 340)" fill="none" stroke="{BLACK}" stroke-width="7">{rings(14, 84)}</g></g></g>
<g class="b"><g class="bx"><g class="by"><g transform="translate(760 340)" fill="none" stroke="#fff" stroke-width="7.5">{rings(15, 80)}</g></g></g></g>
<g class="sun"><g class="sx"><g class="sy"><circle cx="600" cy="340" r="165" fill="{PAINT_RED}"/></g></g></g>
</g>"""
    write("ii-two-readings.svg", svg(W, H, "Two readings of the same sentence", css, body))


# --------------------------------------------------------------------------
# III.  The patron, from every side at once
#
# A rabbit under a red umbrella, in profile and head-on at the same time,
# standing in rain, sun and moonlight at once.  Every shape is a polygon whose
# edges were wobbled here, at build time, so it reads as cut paper.  The black
# key line exists in three slightly different versions that take turns, which
# is the oldest trick in hand-drawn animation.
# --------------------------------------------------------------------------

K = "#17130f"
NAVY, SKY, OCHRE, GREEN, LILAC = "#1c2a4f", "#a8c3d8", "#f0b632", "#3f8f6b", "#c9b8dc"
WHITE, DEEP, VERM, PINK, BLUE, VIOLET = "#fbf7ee", "#a31f24", "#ee6a2e", "#f0a3a0", "#2d5da8", "#7a5ba6"


def qb(p0, c, p1, k=12):
    """Points along a quadratic Bezier."""
    return [
        ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0],
         (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1])
        for t in (i / k for i in range(k + 1))
    ]


def arc(cx, cy, r, a0=0, a1=360, k=None):
    k = k or max(10, int(r * abs(a1 - a0) / 360 * 0.55))
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / k))) for i in range(k + 1)]


def rough(pts, amp, rnd, closed=True, step=24):
    """Subdivide a polyline and push each vertex along its normal by smooth noise."""
    P, m = [], len(pts)
    for i in range(m if closed else m - 1):
        a, b = pts[i], pts[(i + 1) % m]
        k = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        P += [(a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k) for j in range(k)]
    if not closed:
        P.append(pts[-1])
    m = len(P)
    off = [rnd.uniform(-1, 1) for _ in range(m)]
    for _ in range(2):
        off = [(off[i - 1] + 2 * off[i] + off[(i + 1) % m]) / 4 for i in range(m)]
    res = []
    for i, (x, y) in enumerate(P):
        a = P[i - 1] if (closed or i > 0) else P[i]
        b = P[(i + 1) % m] if (closed or i < m - 1) else P[i]
        tx, ty = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(tx, ty) or 1
        o = off[i] * amp * 2.2
        res.append((x - ty / ln * o, y + tx / ln * o))
    return res


def dpath(pts, closed=True):
    return "M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + ("Z" if closed else "")


class Part:
    """A group of shapes that enters together and may loop one animation."""

    def __init__(self, rnd, cls="", delay=0.0, origin=None):
        self.r, self.cls, self.delay, self.origin = rnd, cls, delay, origin
        self.fills, self.lines = [], [[], [], []]

    def _line(self, pts, closed, w):
        sw = "" if w == 7 else f' stroke-width="{w}"'
        for v in range(3):
            self.lines[v].append(f'<path d="{dpath(rough(pts, 1.5, self.r, closed), closed)}"{sw}/>')

    def shape(self, pts, fill, line=True, w=7, pattern=None, amp=2.4):
        d = dpath(rough(pts, amp, self.r))
        dx, dy = self.r.uniform(-3.5, 3.5), self.r.uniform(-3.5, 3.5)  # misregistration
        tr = f' transform="translate({dx:.1f} {dy:.1f})"'
        self.fills.append(f'<path d="{d}" fill="{fill}"{tr}/>')
        if pattern:
            self.fills.append(f'<path d="{d}" fill="url(#{pattern})"{tr}/>')
        if line:
            self._line(pts, True, w)
        return self

    def solid(self, pts, fill=K):
        self.fills.append(f'<path d="{dpath(rough(pts, 1.2, self.r))}" fill="{fill}"/>')
        return self

    def line(self, pts, w=7):
        self._line(pts, False, w)
        return self

    def raw(self, frag):
        self.fills.append(frag)
        return self

    def render(self):
        org = f' style="transform-origin:{self.origin[0]}px {self.origin[1]}px"' if self.origin else ""
        ln = "".join(f'<g class="b{v}">{"".join(self.lines[v])}</g>' for v in range(3)) if self.lines[0] else ""
        inner = f'<g class="{self.cls}"{org}>{"".join(self.fills)}{ln}</g>'
        return f'<g class="in" style="animation-delay:{self.delay:.2f}s">{inner}</g>'


def patron():
    W, H = 1200, 900
    R = random.Random(23)
    out = []

    def part(cls="", delay=0.0, origin=None):
        p = Part(R, cls, delay, origin)
        out.append(p)
        return p

    # ---- ground: five planes, three kinds of weather
    P1 = [(-40, -40), (560, -40), (430, 380), (-40, 480)]
    P2 = [(560, -40), (1240, -40), (1240, 328), (430, 380)]
    p = part("dr1", 0.0).shape(P1, NAVY)
    p.raw('<g clip-path="url(#c1)"><rect class="rn1" x="-200" y="-400" width="1000" height="1200" fill="url(#rainA)"/></g>')
    p = part("dr2", 0.1).shape(P2, SKY)
    p.raw('<g clip-path="url(#c2)"><rect class="rn2" x="200" y="-400" width="1200" height="1000" fill="url(#rainB)"/></g>')
    part("dr3", 0.2).shape([(-40, 480), (430, 380), (330, 940), (-40, 940)], OCHRE, pattern="hatch")
    part("dr2", 0.3).shape([(1240, 328), (1240, 940), (860, 940), (762, 358)], GREEN, pattern="dotsK")
    part("dr1", 0.4).shape([(430, 380), (762, 358), (860, 940), (330, 940)], LILAC)

    part("mA", 0.6).shape(arc(150, 130, 60, 90, 270), OCHRE)
    part("mB", 0.65).shape(arc(150, 146, 60, -90, 90), WHITE)
    sun = part("sun", 0.7, (1085, 118)).shape(arc(1085, 118, 46), VERM)
    for i in range(10):
        a = math.radians(i * 36 + 8)
        sun.line([(1085 + 64 * math.cos(a), 118 + 64 * math.sin(a)), (1085 + 88 * math.cos(a), 118 + 88 * math.sin(a))], 6)

    # ---- umbrella: five gores, two of them slipped
    A = (630, 60)
    b = [(240, 330), (400, 300), (560, 330), (720, 300), (880, 335), (1030, 300)]
    c = [(300, 95), (455, 105), (575, 110), (700, 108), (830, 105), (970, 95)]
    s = [(320, 275), (480, 275), (640, 275), (800, 278), (955, 278)]
    look = [(DEEP, None, (-12, 10)), ("#d7332c", None, (0, 0)), (VERM, None, (0, 0)),
            (DEEP, "dotsW", (0, 0)), (PINK, None, (16, 20))]
    for i, (col, pat, (dx, dy)) in enumerate(look):
        pts = qb(A, c[i], b[i]) + qb(b[i], s[i], b[i + 1])[1:] + qb(b[i + 1], c[i + 1], A)[1:-1]
        pts = [(x + dx, y + dy) for x, y in pts]
        part(f"go g{i}", 0.8 + i * 0.1, A).shape(pts, col, pattern=pat)
    part("", 1.3).line([(630, 64), (628, 28)], 8).solid(arc(628, 22, 8))
    part("", 1.35).line([(648, 300), (702, 615)], 10)

    # ---- body
    body = part("br", 1.5, (560, 940))
    body.shape([(478, 640), (624, 640), (642, 704), (462, 704)], WHITE)
    body.shape([(400, 668), (300, 770), (262, 940), (420, 940), (470, 700)], NAVY, pattern="pin")
    body.shape([(700, 664), (856, 760), (900, 940), (700, 940), (640, 700)], OCHRE, pattern="harl")
    body.shape([(470, 700), (556, 800), (520, 940), (420, 940)], VIOLET)
    body.shape([(640, 700), (556, 800), (600, 940), (700, 940)], NAVY)
    body.shape([(470, 700), (640, 700), (556, 800)], WHITE)
    body.shape([(556, 800), (520, 940), (600, 940)], WHITE)
    body.solid(arc(557, 852, 7)).solid(arc(558, 900, 7))
    body.shape([(556, 716), (510, 692), (510, 742)], "#d7332c")
    body.shape([(556, 716), (602, 692), (602, 742)], "#d7332c")
    body.solid(arc(556, 716, 10))

    # ---- head (everything from here to HEAD_END nods together)
    out.append('<g class="in" style="animation-delay:1.9s"><g class="hd" style="transform-origin:550px 660px">')
    part("eR", 0.0, (596, 384)).shape([(560, 384), (600, 190), (664, 198), (632, 388)], OCHRE)
    part("fl", 0.1, (632, 196)).shape([(600, 190), (664, 198), (806, 252), (764, 304)], BLUE, pattern="stripes")
    ear = part("eL", 0.2, (472, 388))
    ear.shape(qb((440, 392), (368, 240), (430, 104)) + qb((430, 104), (502, 230), (506, 382))[1:], WHITE)
    ear.shape(qb((454, 372), (404, 250), (436, 150)) + qb((436, 150), (480, 250), (486, 368))[1:], PINK, w=5)

    face = part("", 0.3)
    face.shape([(545, 352), (455, 372), (388, 448), (350, 522), (392, 572), (432, 640), (552, 662)], WHITE)
    face.shape([(455, 372), (388, 448), (470, 468)], SKY, w=5)
    face.shape([(392, 572), (432, 640), (552, 662), (500, 586)], PINK, w=5)
    face.shape([(545, 352), (640, 366), (702, 452), (692, 560), (640, 640), (552, 662)], OCHRE)
    face.shape([(702, 452), (692, 560), (640, 640), (612, 530)], GREEN, w=5)
    face.shape(arc(668, 530, 20), "#d7332c", line=False)
    part("ns", 0.5).shape([(350, 522), (386, 496), (388, 546)], PINK, w=6)

    # profile eye, frontal eye: they do not agree about anything
    almond = qb((402, 462), (440, 424), (482, 458)) + qb((482, 458), (440, 490), (402, 462))[1:-1]
    eye = part("", 0.6).shape(almond, WHITE, w=6)
    eye.line([(416, 446), (405, 428)], 4).line([(439, 438), (436, 418)], 4).line([(462, 442), (471, 424)], 4)
    part("lkA", 0.65).shape(arc(444, 458, 14), BLUE, w=4).solid(arc(444, 458, 7))
    part("lidA", 0.65).shape(almond, WHITE, w=6).line(qb((406, 462), (442, 474), (478, 459)), 4)
    part("", 0.7).shape(arc(628, 446, 32), WHITE, w=6)
    part("lkB", 0.75).shape(arc(628, 446, 17), GREEN, w=4).solid(arc(628, 446, 8)).solid(arc(622, 440, 3), WHITE)
    part("lidB", 0.75).shape(arc(628, 446, 33), OCHRE, w=6).line(qb((598, 448), (628, 466), (658, 448)), 5)
    part("bw", 0.8).line(qb((588, 402), (630, 372), (674, 406)), 10)

    mouth = part("", 0.9).solid([(530, 528), (566, 528), (548, 552)])
    mouth.line([(548, 552), (549, 578)], 5)
    mouth.line(qb((549, 578), (522, 604), (494, 580)), 5).line(qb((549, 578), (580, 604), (612, 582)), 5)
    mouth.shape([(535, 582), (549, 582), (549, 605), (535, 605)], WHITE, w=4, amp=0.8)
    mouth.shape([(549, 582), (563, 582), (563, 605), (549, 605)], WHITE, w=4, amp=0.8)
    wl = part("wk", 1.1, (384, 540))
    for e in ((236, 498), (226, 548), (250, 596)):
        wl.line([(384, 540), e], 3.5)
    wr = part("wk w2", 1.15, (648, 566))
    for e in ((806, 530), (818, 574), (796, 616)):
        wr.line([(648, 566), e], 3.5)
    out.append("</g></g>")  # HEAD_END

    # ---- the arm that holds all this up
    arm = part("", 3.0)
    arm.shape([(680, 704), (750, 694), (900, 860), (900, 940), (770, 940)], NAVY)
    arm.shape([(672, 672), (742, 664), (750, 694), (680, 704)], WHITE)
    arm.line([(708, 668), (716, 760)] + qb((716, 760), (722, 806), (690, 806))[1:] + qb((690, 806), (664, 806), (664, 778))[1:], 10)
    for i in range(4):
        y0 = 598 + i * 18
        cap = arc(727, y0 + 8.5, 8.5, -90, 90, 5) + arc(685, y0 + 8.5, 8.5, 90, 270, 5)
        ca, sa = math.cos(math.radians(-8)), math.sin(math.radians(-8))
        cap = [(706 + (x - 706) * ca - (y - 634) * sa, 634 + (x - 706) * sa + (y - 634) * ca) for x, y in cap]
        Part.shape(part(f"fg f{i}", 3.2 + i * 0.07), cap, WHITE, w=5, amp=0.7)

    # ---- still life, because every rabbit portrait is also about lunch
    car = part("ct", 3.5, (170, 780))
    car.shape([(236, 756), (296, 706), (262, 752)], GREEN, w=5)
    car.shape([(240, 760), (312, 744), (262, 768)], GREEN, w=5)
    car.shape([(238, 766), (292, 800), (250, 776)], GREEN, w=5)
    car.shape([(84, 812), (232, 742), (244, 778)], VERM)
    car.line([(150, 772), (158, 788)], 4).line([(186, 756), (192, 770)], 4)

    # ---- signed
    bowl = [(2.75 + 2.25 * math.cos(math.radians(a)), 7 + 3 * math.sin(math.radians(a))) for a in range(0, 361, 30)]
    letters = [
        (5.5, [qb((4.4, 1.2), (2, -0.6), (2, 2.6), 6) + [(2, 10)], [(0.4, 4), (4.2, 4)]]),          # f
        (7.0, [bowl, [(5, 4), (5, 10)]]),                                                          # a
        (7.0, [[(0.5, 0), (0.5, 10)], bowl]),                                                      # b
        (3.6, [[(1, 0), (1, 10)]]),                                                                # l
        (6.0, [[(0.5, 7), (5, 7)] + qb((5, 7), (5, 4), (2.75, 4), 6)[1:] + qb((2.75, 4), (0.5, 4), (0.5, 7), 6)[1:]
               + qb((0.5, 7), (0.5, 10), (2.75, 10), 6)[1:] + qb((2.75, 10), (4.3, 10), (5.1, 8.9), 6)[1:]]),  # e
    ]
    sig, ox = part("", 4.0), 0.0
    S, OX, OY = 6.2, 996, 792
    place = lambda x, y: (OX + S * (x + 0.2 * (10 - y)), OY + S * y)
    for adv, strokes in letters:
        for st in strokes:
            sig.line([place(ox + x, y) for x, y in st], 4.5)
        ox += adv
    sig.line([place(x, y) for x, y in qb((-1.5, 13.2), (14, 11.2), (ox + 1, 12.6), 8)], 4)

    GR = random.Random(3)
    grain = "".join(
        f'<rect x="{GR.uniform(0, 158):.0f}" y="{GR.uniform(0, 158):.0f}" width="1.7" height="1.7" '
        f'fill="{GR.choice(("#000", "#000", "#fff"))}" opacity="{GR.uniform(0.05, 0.16):.2f}"/>'
        for _ in range(300)
    )
    css = f"""
.in{{transform-box:fill-box;transform-origin:center;animation:in .9s cubic-bezier(.2,.9,.25,1) backwards}}
.b0,.b1,.b2{{fill:none;stroke:{K};stroke-width:7;stroke-linejoin:round;stroke-linecap:round}}
.b1,.b2{{opacity:0}}
.b0{{animation:b0 .66s step-end infinite}}.b1{{animation:b1 .66s step-end infinite}}.b2{{animation:b2 .66s step-end infinite}}
.rn1{{animation:rn1 1.1s linear infinite}}.rn2{{animation:rn2 .9s linear infinite}}
.dr1{{animation:dr1 11s ease-in-out infinite alternate}}.dr2{{animation:dr2 13s ease-in-out infinite alternate}}.dr3{{animation:dr1 9s ease-in-out -4s infinite alternate-reverse}}
.mA{{animation:bob 3.7s ease-in-out infinite alternate}}.mB{{animation:bob 3.7s ease-in-out infinite alternate-reverse}}
.sun{{animation:spin 48s linear infinite}}
.go{{animation:sw 5.5s ease-in-out infinite alternate}}
.g1{{animation-duration:4.7s;animation-delay:-2s}}.g2{{animation-duration:6.7s;animation-delay:-1s}}.g3{{animation-duration:5.1s;animation-delay:-3s}}.g4{{animation-duration:7.3s;animation-delay:-5s}}
.br{{animation:br 3.4s ease-in-out infinite alternate}}
.hd{{animation:hd 4.6s ease-in-out infinite alternate}}
.eL{{animation:eL 6.2s ease-in-out infinite}}
.eR{{animation:eR 5.1s ease-in-out infinite alternate}}
.fl{{animation:fl 2.9s ease-in-out infinite alternate}}
.ns{{transform-box:fill-box;transform-origin:right center;animation:ns 2.8s ease-in-out infinite}}
.lkA{{animation:lk 5.9s ease-in-out infinite}}.lkB{{animation:lk 7.7s ease-in-out -3s infinite reverse}}
.lidA,.lidB{{transform-box:fill-box;transform-origin:top;transform:scaleY(0)}}
.lidA{{animation:lid 5.3s step-end infinite}}.lidB{{animation:lid 7.1s step-end -2s infinite}}
.bw{{animation:bw 2.9s ease-in-out infinite alternate}}
.wk{{animation:wk .9s ease-in-out infinite alternate}}.w2{{animation-duration:1.1s;animation-direction:alternate-reverse}}
.fg{{animation:fg .8s ease-in-out infinite alternate}}.f1{{animation-delay:-.2s}}.f2{{animation-delay:-.4s}}.f3{{animation-delay:-.6s}}
.ct{{animation:ct 2.3s ease-in-out infinite alternate}}
@keyframes in{{from{{opacity:0;transform:translateY(36px) rotate(-4deg) scale(.93)}}}}
@keyframes b0{{0%{{opacity:1}}33.3%,100%{{opacity:0}}}}
@keyframes b1{{0%{{opacity:0}}33.3%{{opacity:1}}66.6%,100%{{opacity:0}}}}
@keyframes b2{{0%{{opacity:0}}66.6%,100%{{opacity:1}}}}
@keyframes rn1{{to{{transform:translate(-40px,120px)}}}}
@keyframes rn2{{to{{transform:translate(40px,100px)}}}}
@keyframes dr1{{from{{transform:translate(-3px,2px)}}to{{transform:translate(4px,-3px)}}}}
@keyframes dr2{{from{{transform:translate(3px,3px)}}to{{transform:translate(-4px,-2px)}}}}
@keyframes bob{{from{{transform:translateY(-6px)}}to{{transform:translateY(6px)}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes sw{{from{{transform:rotate(-1.5deg)}}to{{transform:rotate(1.8deg)}}}}
@keyframes br{{from{{transform:scaleY(1)}}to{{transform:scaleY(1.014)}}}}
@keyframes hd{{from{{transform:rotate(-1.3deg)}}to{{transform:rotate(1.6deg) translateY(4px)}}}}
@keyframes eL{{0%,84%,100%{{transform:rotate(0)}}88%{{transform:rotate(-8deg)}}91%{{transform:rotate(3deg)}}94%{{transform:rotate(-5deg)}}97%{{transform:rotate(1deg)}}}}
@keyframes eR{{from{{transform:rotate(-1deg)}}to{{transform:rotate(2.5deg)}}}}
@keyframes fl{{from{{transform:rotate(-2deg)}}to{{transform:rotate(9deg)}}}}
@keyframes ns{{0%,40%,100%{{transform:scale(1)}}46%,58%,70%{{transform:scale(1.22)}}52%,64%,76%{{transform:scale(.95)}}}}
@keyframes lk{{0%,20%,100%{{transform:translate(0,0)}}28%,48%{{transform:translate(-6px,1px)}}56%,72%{{transform:translate(5px,-2px)}}80%,92%{{transform:translate(1px,4px)}}}}
@keyframes lid{{0%,100%{{transform:scaleY(0)}}93%{{transform:scaleY(1)}}96%{{transform:scaleY(0)}}}}
@keyframes bw{{from{{transform:translateY(2px)}}to{{transform:translateY(-7px)}}}}
@keyframes wk{{from{{transform:rotate(-2.2deg)}}to{{transform:rotate(2.4deg)}}}}
@keyframes fg{{from{{transform:translateX(0)}}to{{transform:translateX(5px)}}}}
@keyframes ct{{from{{transform:rotate(-2.5deg)}}to{{transform:rotate(2.5deg)}}}}
{reduced()}
"""
    body = f"""<defs>
<clipPath id="f"><rect width="{W}" height="{H}" rx="4"/></clipPath>
<clipPath id="c1"><path d="{dpath(P1)}"/></clipPath>
<clipPath id="c2"><path d="{dpath(P2)}"/></clipPath>
<pattern id="rainA" width="40" height="60" patternUnits="userSpaceOnUse"><path d="M30 6L21 33" stroke="{WHITE}" stroke-width="2.6" stroke-linecap="round" opacity=".8"/></pattern>
<pattern id="rainB" width="40" height="50" patternUnits="userSpaceOnUse"><path d="M10 6L21 33.5" stroke="{NAVY}" stroke-width="2.6" stroke-linecap="round" opacity=".85"/></pattern>
<pattern id="hatch" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(-38)"><path d="M0 8H16" stroke="{K}" stroke-width="2" opacity=".22"/></pattern>
<pattern id="dotsK" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="7" cy="7" r="3.4" fill="{K}" opacity=".3"/><circle cx="21" cy="21" r="3.4" fill="{K}" opacity=".3"/></pattern>
<pattern id="dotsW" width="30" height="30" patternUnits="userSpaceOnUse"><circle cx="8" cy="8" r="4.6" fill="{WHITE}" opacity=".9"/><circle cx="23" cy="23" r="4.6" fill="{WHITE}" opacity=".9"/></pattern>
<pattern id="pin" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(20)"><rect width="2.6" height="14" fill="{WHITE}" opacity=".55"/></pattern>
<pattern id="stripes" width="18" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><rect width="8" height="18" fill="{WHITE}"/></pattern>
<pattern id="harl" width="56" height="84" patternUnits="userSpaceOnUse"><path d="M28 0L56 42L28 84L0 42Z" fill="#d7332c"/></pattern>
<pattern id="grain" width="160" height="160" patternUnits="userSpaceOnUse">{grain}</pattern>
</defs>
<g clip-path="url(#f)">
<rect width="{W}" height="{H}" fill="{PAPER}"/>
{"".join(o if isinstance(o, str) else o.render() for o in out)}
<rect width="{W}" height="{H}" fill="url(#grain)"/>
<rect x="6" y="6" width="{W - 12}" height="{H - 12}" rx="2" fill="none" stroke="{K}" stroke-width="12"/>
</g>"""
    write("iii-the-patron.svg", svg(W, H, "The patron, from every side at once", css, body))


WALL = {"mono": mono, "moire": moire, "patron": patron}
ARCHIVE = {"almost": almost}

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--preview" in args:
        at = args.index("--preview")
        FORCE_MOTION, OUT = True, args[at + 1]
        del args[at:at + 2]
    for name in args or WALL:
        {**WALL, **ARCHIVE}[name]()
