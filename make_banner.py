"""
make_banner.py — Generates banner_630x500.png for the itch.io page.
Style: Lovecraftian cosmic horror + synthwave retro.
Knight featured centre; Ranger left, Jester right.
Run with:  python make_banner.py
Output:    banner_630x500.png
"""

import math, random, pygame

W, H = 630, 500
OUT  = "banner_630x500.png"

pygame.init()
surf = pygame.Surface((W, H))
rng  = random.Random(7)   # fixed seed — deterministic re-runs

# ── Palette ──────────────────────────────────────────────────────────────────
VOID       = (4,  3, 14)
DEEP       = (10,  6, 28)
CYAN       = (0, 220, 255)
MAGENTA    = (210, 40, 255)
GREEN      = (30, 220, 110)
ORANGE     = (255, 150, 20)
GOLD       = (220, 180, 40)
WHITE      = (230, 225, 245)
ELDRITCH   = (80, 255, 160)    # sickly void-green
DIM_CYAN   = (0, 60, 90)
DIM_MAG    = (60, 10, 80)
BLOOD_RED  = (180, 20, 30)
TENTACLE   = (30, 10, 50)

# ── Core helpers ─────────────────────────────────────────────────────────────
def clamp_color(c):
    return tuple(max(0, min(255, v)) for v in c)

def glow(dst, color, center, radius, steps=6, max_alpha=60):
    cx, cy = int(center[0]), int(center[1])
    radius = int(radius)
    if radius <= 0:
        return
    for i in range(steps, 0, -1):
        alpha = int(max_alpha * (i / steps) ** 2)
        r_i   = max(1, int(radius * i / steps))
        s = pygame.Surface((r_i * 2 + 2, r_i * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, alpha), (r_i + 1, r_i + 1), r_i)
        dst.blit(s, (cx - r_i - 1, cy - r_i - 1))

def poly_outline(dst, pts, fill, stroke, width=2):
    pygame.draw.polygon(dst, fill, pts)
    pygame.draw.polygon(dst, stroke, pts, width)

def arc_pts(cx, cy, rx, ry, a0, a1, steps=24):
    """Return list of (x,y) points along an ellipse arc."""
    pts = []
    for i in range(steps + 1):
        t = a0 + (a1 - a0) * i / steps
        pts.append((int(cx + rx * math.cos(t)), int(cy + ry * math.sin(t))))
    return pts

# ── Font helpers ─────────────────────────────────────────────────────────────
def get_font(names, size, bold=False):
    for name in names:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        except Exception:
            pass
    return pygame.font.Font(None, size)

def outlined_text(dst, text, font, color, outline_col, cx, cy, outline=3):
    for dx in range(-outline, outline + 1):
        for dy in range(-outline, outline + 1):
            if dx*dx + dy*dy <= (outline+1)**2:
                s = font.render(text, True, outline_col)
                dst.blit(s, s.get_rect(center=(cx+dx, cy+dy)))
    s = font.render(text, True, color)
    dst.blit(s, s.get_rect(center=(cx, cy)))

def glow_text(dst, text, font, color, glow_col, cx, cy, steps=4, spread=6):
    for i in range(steps, 0, -1):
        sp  = max(1, int(spread * i / steps))
        alp = int(90 * (i / steps) ** 2)
        gs  = font.render(text, True, glow_col)
        gs.set_alpha(alp)
        for dx in range(-sp, sp+1, max(1, sp)):
            for dy in range(-sp, sp+1, max(1, sp)):
                dst.blit(gs, gs.get_rect(center=(cx+dx, cy+dy)))
    s = font.render(text, True, color)
    dst.blit(s, s.get_rect(center=(cx, cy)))


# ══════════════════════════════════════════════════════════════════════════════
# 1.  COSMIC VOID BACKGROUND
# ══════════════════════════════════════════════════════════════════════════════
for y in range(H):
    t  = y / H
    rv = int(VOID[0] * (1-t) + 16 * t)
    gv = int(VOID[1] * (1-t) + 4  * t)
    bv = int(VOID[2] * (1-t) + 40 * t)
    pygame.draw.line(surf, (rv, gv, bv), (0, y), (W, y))

# Nebula wisps — soft blobs of color
for nx, ny, nr, nc in [
    (140, 200, 130, (60, 10, 100)),
    (500, 190, 120, (0,  40, 90)),
    (310, 300, 100, (20, 5,  60)),
    (80,  350, 80,  (40, 0,  70)),
    (560, 340, 80,  (0,  30, 70)),
]:
    ns = pygame.Surface((nr*2, nr*2), pygame.SRCALPHA)
    for step in range(6, 0, -1):
        a = int(35 * (step/6)**2)
        r = int(nr * step / 6)
        pygame.draw.circle(ns, (*nc, a), (nr, nr), r)
    surf.blit(ns, (nx - nr, ny - nr))

# Stars
for _ in range(280):
    sx, sy = rng.randint(0, W), rng.randint(0, H*2//3)
    sz     = rng.choices([1, 1, 1, 2], k=1)[0]
    br     = rng.randint(130, 255)
    pygame.draw.circle(surf, (br, br, min(255, br+20)), (sx, sy), sz)

# Twinkling bright stars
for _ in range(12):
    sx, sy = rng.randint(30, W-30), rng.randint(20, H//2)
    pygame.draw.circle(surf, WHITE, (sx, sy), 2)
    pygame.draw.line(surf, (WHITE[0], WHITE[1], WHITE[2]), (sx-5, sy), (sx+5, sy), 1)
    pygame.draw.line(surf, (WHITE[0], WHITE[1], WHITE[2]), (sx, sy-5), (sx, sy+5), 1)


# ══════════════════════════════════════════════════════════════════════════════
# 2.  ELDRITCH EYE in the sky (upper-right background)
# ══════════════════════════════════════════════════════════════════════════════
ex_c, ey_c = 510, 130
# outer glow
glow(surf, (60, 200, 100), (ex_c, ey_c), 75, steps=8, max_alpha=40)
# sclera (white of eye)
pygame.draw.ellipse(surf, (15, 35, 25), (ex_c-55, ey_c-28, 110, 56))
pygame.draw.ellipse(surf, (30, 80, 50),  (ex_c-55, ey_c-28, 110, 56), 2)
# iris rings
for ir, ic in [(22, (20, 160, 80)), (16, (30, 200, 100)), (10, (50, 240, 130))]:
    pygame.draw.circle(surf, ic, (ex_c, ey_c), ir)
# pupil — slit / vertical
pygame.draw.ellipse(surf, (2, 2, 5), (ex_c-5, ey_c-16, 10, 32))
# pupil glow
glow(surf, ELDRITCH, (ex_c, ey_c), 12, steps=4, max_alpha=80)
# eyelids
pygame.draw.arc(surf, (10,30,18), (ex_c-56, ey_c-28, 112, 56), math.pi, 2*math.pi, 3)
pygame.draw.arc(surf, (10,30,18), (ex_c-56, ey_c-28, 112, 56), 0, math.pi, 3)
# veins
for va in [0.3, 0.7, -0.3, 1.1]:
    vx = int(ex_c + math.cos(va)*52)
    vy = int(ey_c + math.sin(va)*24)
    pygame.draw.line(surf, (40, 100, 60), (ex_c, ey_c), (vx, vy), 1)


# ══════════════════════════════════════════════════════════════════════════════
# 3.  VOID RIFT (portal) behind center knight
# ══════════════════════════════════════════════════════════════════════════════
vr_cx, vr_cy = W//2, 310
glow(surf, MAGENTA,  (vr_cx, vr_cy), 100, steps=10, max_alpha=35)
glow(surf, CYAN,     (vr_cx, vr_cy),  70, steps=8,  max_alpha=30)
# dark core
pygame.draw.ellipse(surf, (6, 2, 18), (vr_cx-52, vr_cy-70, 104, 140))
pygame.draw.ellipse(surf, MAGENTA,    (vr_cx-52, vr_cy-70, 104, 140), 2)
pygame.draw.ellipse(surf, CYAN,       (vr_cx-46, vr_cy-64, 92,  128), 1)
# swirl lines
for i in range(8):
    a = i * math.pi / 4
    x1 = int(vr_cx + math.cos(a) * 20)
    y1 = int(vr_cy + math.sin(a) * 28)
    x2 = int(vr_cx + math.cos(a + 0.6) * 48)
    y2 = int(vr_cy + math.sin(a + 0.6) * 64)
    col_swirl = CYAN if i % 2 == 0 else MAGENTA
    pygame.draw.line(surf, col_swirl, (x1, y1), (x2, y2), 1)


# ══════════════════════════════════════════════════════════════════════════════
# 4.  RETRO GRID FLOOR
# ══════════════════════════════════════════════════════════════════════════════
horizon_y = 318
vp_x      = W // 2

for i in range(12):
    t  = (i / 11) ** 1.8
    y  = int(horizon_y + (H - horizon_y) * t)
    br = int(90 * t)
    c  = (0, int(br * 0.8), int(br * 1.2))
    pygame.draw.line(surf, clamp_color(c), (0, y), (W, y), 1)

for i in range(18):
    xb = int(W * i / 17)
    br = max(0, 60 - abs(xb - W//2) // 4)
    pygame.draw.line(surf, (0, int(br*0.6), br), (vp_x, horizon_y), (xb, H), 1)


# ══════════════════════════════════════════════════════════════════════════════
# 5.  TENTACLES
# ══════════════════════════════════════════════════════════════════════════════
def draw_tentacle(dst, ox, oy, segs, angle, curve, thickness, col, glow_col=None):
    """Draw a segmented tentacle starting at (ox,oy) going in direction angle."""
    pts = [(ox, oy)]
    a   = angle
    tx, ty = float(ox), float(oy)
    for i, (seg_len, da) in enumerate(segs):
        a  += da
        tx += math.cos(a) * seg_len
        ty += math.sin(a) * seg_len
        pts.append((int(tx), int(ty)))
    if glow_col:
        for j in range(len(pts)-1):
            glow(dst, glow_col, pts[j], thickness*2, steps=3, max_alpha=30)
    for j in range(len(pts)-1):
        w = max(1, int(thickness * (1 - j/len(pts)) * 1.4))
        pygame.draw.line(dst, col, pts[j], pts[j+1], w)
    # sucker dots
    for j in range(1, len(pts)-1, 2):
        r = max(1, int(thickness * 0.35 * (1 - j/len(pts))))
        pygame.draw.circle(dst, clamp_color((col[0]+30, col[1]+20, col[2]+40)), pts[j], r)
    # tip nub
    pygame.draw.circle(dst, clamp_color((col[0]+40, col[1]+20, col[2]+60)), pts[-1], max(1, thickness//3))

# Bottom-left tentacle cluster
tentacle_segs_L = [
    [(30,-0.1),(28,-0.15),(25,-0.2),(22,-0.25),(18,-0.3),(14,-0.35),(10,-0.3)],
    [(28, 0.1),(26, 0.2), (22, 0.3),(18, 0.25),(14, 0.2),(10, 0.15),(8,  0.1)],
    [(35,-0.05),(30,-0.1),(26,-0.2),(20,-0.3),(16,-0.25),(12,-0.2),(8,-0.1)],
]
for i, (base_x, base_y, base_a, segs) in enumerate([
    (0,   H+10, -math.pi*0.42, tentacle_segs_L[0]),
    (30,  H+10, -math.pi*0.48, tentacle_segs_L[1]),
    (-20, H+10, -math.pi*0.36, tentacle_segs_L[2]),
]):
    draw_tentacle(surf, base_x, base_y, segs, base_a, 0, 8-i,
                  TENTACLE, glow_col=(60, 0, 80))

# Bottom-right tentacle cluster
tentacle_segs_R = [
    [(30,0.1),(28,0.15),(25,0.2),(22,0.25),(18,0.3),(14,0.35),(10,0.3)],
    [(28,-0.1),(26,-0.2),(22,-0.3),(18,-0.25),(14,-0.2),(10,-0.15),(8,-0.1)],
    [(32,0.05),(28,0.1),(24,0.2),(20,0.3),(16,0.25),(12,0.2),(8,0.1)],
]
for i, (base_x, base_y, base_a, segs) in enumerate([
    (W,    H+10, -math.pi*0.58, tentacle_segs_R[0]),
    (W-30, H+10, -math.pi*0.52, tentacle_segs_R[1]),
    (W+20, H+10, -math.pi*0.64, tentacle_segs_R[2]),
]):
    draw_tentacle(surf, base_x, base_y, segs, base_a, 0, 8-i,
                  TENTACLE, glow_col=(0, 40, 80))

# Thin eldritch tendrils creeping up sides
for i in range(4):
    base_y = 380 + i * 25
    segs   = [(20,-0.3+i*0.05),(18,-0.25),(15,-0.2),(12,-0.15),(9,-0.1)]
    draw_tentacle(surf, 0, base_y, segs, 0.1 - i*0.05, 0, 2, (50, 0, 70))
for i in range(4):
    base_y = 380 + i * 25
    segs   = [(20,-0.3+i*0.05),(18,-0.2),(14,-0.15),(11,-0.1),(8,-0.05)]
    draw_tentacle(surf, W, base_y, segs, math.pi + 0.1 - i*0.05, 0, 2, (0, 30, 60))


# ══════════════════════════════════════════════════════════════════════════════
# 6.  SUMMONING CIRCLE under Knight
# ══════════════════════════════════════════════════════════════════════════════
sc_cx, sc_cy = W//2, 420
# outer ring glow
glow(surf, CYAN, (sc_cx, sc_cy), 68, steps=5, max_alpha=50)
pygame.draw.circle(surf, CYAN,    (sc_cx, sc_cy), 62, 2)
pygame.draw.circle(surf, DIM_CYAN,(sc_cx, sc_cy), 54, 1)
# inner pentagram
for i in range(5):
    a1 = math.radians(-90 + i*72)
    a2 = math.radians(-90 + (i+2)*72)
    x1 = int(sc_cx + math.cos(a1)*48)
    y1 = int(sc_cy + math.sin(a1)*18)
    x2 = int(sc_cx + math.cos(a2)*48)
    y2 = int(sc_cy + math.sin(a2)*18)
    pygame.draw.line(surf, CYAN, (x1,y1), (x2,y2), 1)
# rune dots on ring
for i in range(8):
    a  = i * math.tau / 8
    rx = int(sc_cx + math.cos(a)*62)
    ry = int(sc_cy + math.sin(a)*22)
    pygame.draw.circle(surf, CYAN, (rx, ry), 3)


# ══════════════════════════════════════════════════════════════════════════════
# 7.  CHARACTERS
# ══════════════════════════════════════════════════════════════════════════════

# ── RANGER (left) ─────────────────────────────────────────────────────────
rx, ry = 118, 390   # feet position
rs = 2.8            # scale

def rp(dx, dy):
    return (int(rx + dx*rs), int(ry + dy*rs))

# ground shadow
glow(surf, GREEN, (rx, ry), 28, steps=3, max_alpha=40)

# hooded cloak (large triangle from head to feet)
cloak_pts = [rp(0,-36), rp(-14,0), rp(-10,4), rp(10,4), rp(14,0)]
poly_outline(surf, cloak_pts, (20, 45, 25), GREEN, 2)

# inner hood shadow
pygame.draw.polygon(surf, (10, 25, 15),
    [rp(-5,-35), rp(-8,-10), rp(0,-8), rp(8,-10), rp(5,-35)])

# face / dark void under hood
pygame.draw.circle(surf, (8, 18, 10), rp(0,-30), int(7*rs*0.7))
# two pinpoint glowing eyes
glow(surf, GREEN, rp(-3,-31), 5, steps=3, max_alpha=120)
glow(surf, GREEN, rp( 3,-31), 5, steps=3, max_alpha=120)
pygame.draw.circle(surf, GREEN, rp(-3,-31), 2)
pygame.draw.circle(surf, GREEN, rp( 3,-31), 2)

# bow (arc on left side)
bow_cx, bow_cy = rp(-18,-18)
pygame.draw.arc(surf, GOLD,
    (bow_cx-int(6*rs), bow_cy-int(14*rs), int(12*rs), int(28*rs)),
    math.radians(70), math.radians(290), max(2, int(1.5*rs)))
# bowstring
pygame.draw.line(surf, (180,180,130), rp(-18,-32), rp(-18,-4), 1)
# arrow nocked
pygame.draw.line(surf, GOLD, rp(-18,-18), rp(18,-22), 2)
glow(surf, GOLD, rp(18,-22), 8, steps=3, max_alpha=80)
pygame.draw.circle(surf, GOLD, rp(18,-22), 3)

# quiver on back
pygame.draw.rect(surf, (30, 60, 30),
    (rp(8,-28)[0], rp(8,-28)[1], int(5*rs), int(14*rs)))
for qi in range(3):
    pygame.draw.line(surf, GOLD,
        (rp(9+qi,-27)[0], rp(9+qi,-27)[1]),
        (rp(9+qi,-34)[0], rp(9+qi,-34)[1]), 1)

# ── JESTER (right) ────────────────────────────────────────────────────────
jx, jy = 490, 390   # shifted left for rubber chicken
js = 2.8

def jp(dx, dy):
    return (int(jx + dx*js), int(jy + dy*js))

glow(surf, MAGENTA, (jx, jy), 28, steps=3, max_alpha=40)

# legs — slightly splayed (mid-trick pose)
for lx, langle in [(-4, 0.15), (4, -0.10)]:
    lbx = int(jx + lx*js + math.sin(langle)*10*js)
    lby = int(jy + math.cos(langle)*8*js)
    pygame.draw.line(surf, (60, 20, 80), jp(lx, 0), (lbx, lby), max(2, int(2.5*js)))

# body — diamond-patterned tunic
body_pts = [jp(0,-28), jp(-9,-14), jp(0,-6), jp(9,-14)]
poly_outline(surf, body_pts, (90, 15, 120), MAGENTA, 2)
# diamond pattern
pygame.draw.polygon(surf, ORANGE,
    [jp(-4,-21), jp(0,-14), jp(4,-21), jp(0,-28)])

# arms — one up (throwing), one out
# left arm down/out holding bright juggling ball
pygame.draw.line(surf, (80,20,100), jp(-9,-20), jp(-18,-12), max(2,int(2*js)))
# JUGGLING BALL — vivid purple, hard to miss
_jball = jp(-18, -12)
_jbr = max(18, int(12*js*0.5))
pygame.draw.circle(surf, (140, 30, 230), _jball, _jbr)
pygame.draw.circle(surf, (210, 80, 255), _jball, _jbr, 3)
pygame.draw.circle(surf, (230, 180, 255), (_jball[0]-int(_jbr*0.35), _jball[1]-int(_jbr*0.35)), max(3, int(_jbr*0.28)))
glow(surf, (180, 60, 255), _jball, _jbr+10, steps=4, max_alpha=110)
# right arm raised, holding rubber chicken
pygame.draw.line(surf, (80,20,100), jp(9,-20), jp(18,-32), max(2,int(2*js)))
# RUBBER CHICKEN in raised right hand
_ck = jp(22, -40)  # tip of hand
# body — big yellow oval
pygame.draw.ellipse(surf, (255, 200, 30), (_ck[0]-10, _ck[1]-18, 32, 22))
pygame.draw.ellipse(surf, (220, 140, 0), (_ck[0]-10, _ck[1]-18, 32, 22), 2)
# wing bump
pygame.draw.arc(surf, (200, 120, 0), (_ck[0]-2, _ck[1]-10, 22, 14), math.radians(200), math.radians(360), 3)
# neck
pygame.draw.line(surf, (255, 200, 30), (_ck[0]+10, _ck[1]-18), (_ck[0]+14, _ck[1]-32), 5)
# head
pygame.draw.circle(surf, (255, 210, 40), (_ck[0]+16, _ck[1]-34), 11)
pygame.draw.circle(surf, (220, 140, 0), (_ck[0]+16, _ck[1]-34), 11, 2)
# beak
pygame.draw.polygon(surf, (255, 100, 0),
    [(_ck[0]+20, _ck[1]-37), (_ck[0]+28, _ck[1]-34), (_ck[0]+20, _ck[1]-31)])
# wattle
pygame.draw.ellipse(surf, (200, 30, 30), (_ck[0]+21, _ck[1]-31, 6, 9))
# eye
pygame.draw.circle(surf, (10, 10, 10), (_ck[0]+13, _ck[1]-37), 2)
# legs dangling
pygame.draw.line(surf, (220, 140, 0), (_ck[0]+4, _ck[1]+4), (_ck[0]+2, _ck[1]+14), 2)
pygame.draw.line(surf, (220, 140, 0), (_ck[0]+10, _ck[1]+4), (_ck[0]+10, _ck[1]+14), 2)
# glow halo
glow(surf, (255, 200, 30), (_ck[0]+8, _ck[1]-12), 22, steps=3, max_alpha=90)

# head
pygame.draw.circle(surf, (70, 20, 95), jp(0,-34), int(8*js*0.7))
pygame.draw.circle(surf, MAGENTA, jp(0,-34), int(8*js*0.7), 2)

# jester hat — 2-pointed
hat_pts = [jp(-9,-38), jp(-6,-52), jp(0,-44), jp(6,-52), jp(9,-38)]
poly_outline(surf, hat_pts, (100, 15, 130), MAGENTA, 1)
# bells at hat tips
for bpos in [jp(-6,-52), jp(6,-52)]:
    pygame.draw.circle(surf, ORANGE, bpos, max(2, int(2*js)))
    glow(surf, ORANGE, bpos, 6, steps=2, max_alpha=80)

# eyes — chaotic wide
pygame.draw.circle(surf, ORANGE, jp(-3,-35), 2)
pygame.draw.circle(surf, GREEN,  jp( 3,-35), 2)
glow(surf, ORANGE, jp(-3,-35), 4, steps=2, max_alpha=120)
glow(surf, GREEN,  jp( 3,-35), 4, steps=2, max_alpha=120)

# laughing mouth
pygame.draw.arc(surf, WHITE,
    (jp(-4,-33)[0], jp(-4,-33)[1], int(8*js), int(5*js)),
    math.radians(190), math.radians(350), 1)

# floating daggers orbiting jester
for di, da in enumerate([0.4, 1.8, 3.2]):
    ddx = int(jx + math.cos(da)*32)
    ddy = int(jy - 20 + math.sin(da)*14)
    pygame.draw.line(surf, CYAN,
        (ddx, ddy), (int(ddx + math.cos(da+1.2)*9), int(ddy + math.sin(da+1.2)*9)), 2)
    glow(surf, CYAN, (ddx, ddy), 5, steps=2, max_alpha=80)


# ── KNIGHT (centre, largest) ──────────────────────────────────────────────
kx, ky = W//2, 390   # feet
ks = 4.0             # larger scale — hero

def kp(dx, dy):
    return (int(kx + dx*ks), int(ky + dy*ks))

# ground aura — strong
glow(surf, CYAN,    (kx, ky), 55, steps=6, max_alpha=60)
glow(surf, MAGENTA, (kx, ky), 35, steps=4, max_alpha=30)

# flowing cape (behind body)
cape_pts = [kp(0,-38), kp(-18,-10), kp(-16,0), kp(-10,6),
            kp(0,2),   kp(10,6),    kp(16,0),  kp(18,-10)]
poly_outline(surf, cape_pts, (55, 10, 90), MAGENTA, 2)
# cape inner shadow
pygame.draw.polygon(surf, (35, 5, 60),
    [kp(-2,-35), kp(-10,0), kp(0,-2), kp(10,0), kp(2,-35)])

# legs
for lx in (-4, 4):
    leg_rect = (*kp(lx-2, 0), int(4*ks), int(10*ks))
    pygame.draw.rect(surf, (35, 40, 80), leg_rect)
    pygame.draw.rect(surf, (70, 80, 160), leg_rect, 2)
    # knee plate
    pygame.draw.rect(surf, (80, 90, 180),
        (kp(lx-3,4)[0], kp(lx-3,4)[1], int(6*ks), int(3*ks)))

# body armour
body_rect = (*kp(-7,-18), int(14*ks), int(20*ks))
pygame.draw.rect(surf, (40, 44, 100), body_rect)
pygame.draw.rect(surf, CYAN, body_rect, 2)
# chest rune — glowing sigil
pygame.draw.polygon(surf, CYAN,
    [kp(0,-16), kp(-4,-11), kp(4,-11)], 1)
pygame.draw.polygon(surf, CYAN,
    [kp(0,-8), kp(-4,-13), kp(4,-13)], 1)
glow(surf, CYAN, kp(0,-12), 8, steps=3, max_alpha=80)

# shoulder pauldrons
for sx in (-7, 7):
    pts = [kp(sx,-18), kp(sx+(-3 if sx<0 else 3),-22),
           kp(sx+(-5 if sx<0 else 5),-16), kp(sx+(-4 if sx<0 else 4),-12)]
    poly_outline(surf, pts, (50, 55, 120), CYAN, 2)

# head / helmet
pygame.draw.circle(surf, (45, 50, 110), kp(0,-26), int(9*ks*0.7))
pygame.draw.circle(surf, CYAN,          kp(0,-26), int(9*ks*0.7), 2)
# visor slit — glowing
visor_rect = (kp(-6,-28)[0], kp(-6,-28)[1], int(12*ks), int(3*ks))
pygame.draw.rect(surf, (5, 5, 30), visor_rect)
pygame.draw.rect(surf, CYAN, visor_rect, 1)
glow(surf, CYAN, (kp(-6,-28)[0] + int(6*ks), kp(-6,-28)[1] + int(1.5*ks)),
     int(5*ks), steps=4, max_alpha=90)
# helmet crest / fin
crest_pts = [kp(-2,-34), kp(-1,-42), kp(1,-42), kp(2,-34)]
poly_outline(surf, crest_pts, (60, 65, 140), CYAN, 1)

# sword arm (raised right, blade angled up-right)
# upper arm
pygame.draw.line(surf, (50, 55, 120), kp(7,-16), kp(18,-26), max(3, int(3*ks)))
# lower arm / fist
pygame.draw.line(surf, (50, 55, 120), kp(18,-26), kp(22,-34), max(3, int(2.5*ks)))
# hilt guard
pygame.draw.line(surf, GOLD, kp(20,-33), kp(26,-28), max(2, int(2*ks)))
# blade — long bright
blade_start = kp(23,-36)
blade_end   = kp(38,-54)
pygame.draw.line(surf, WHITE, blade_start, blade_end, max(2, int(1.8*ks)))
pygame.draw.line(surf, CYAN,  blade_start, blade_end, max(1, int(0.8*ks)))
glow(surf, CYAN,  blade_end, 18, steps=5, max_alpha=120)
glow(surf, WHITE, blade_end,  8, steps=3, max_alpha=180)
pygame.draw.circle(surf, WHITE, blade_end, 4)

# shield (left arm, lower-left)
pygame.draw.line(surf, (50,55,120), kp(-7,-16), kp(-18,-8), max(3,int(3*ks)))
shield_pts = [kp(-20,-16), kp(-28,-12), kp(-30,-4), kp(-24,2), kp(-18,-4), kp(-16,-12)]
poly_outline(surf, shield_pts, (40, 44, 100), CYAN, 2)
pygame.draw.circle(surf, CYAN, kp(-24,-7), max(2, int(2*ks)))
glow(surf, CYAN, kp(-24,-7), 8, steps=3, max_alpha=60)


# ══════════════════════════════════════════════════════════════════════════════
# 8.  FLOATING PARTICLES / XP ORBS
# ══════════════════════════════════════════════════════════════════════════════
for ox, oy, oc in [
    (80, 365, GREEN), (170, 348, GREEN), (460, 355, GREEN),
    (548, 372, GREEN), (230, 380, CYAN), (400, 378, CYAN),
    (310, 460, MAGENTA), (150, 420, ELDRITCH), (480, 430, ELDRITCH),
]:
    glow(surf, oc, (ox, oy), 9, steps=3, max_alpha=80)
    pygame.draw.circle(surf, oc, (ox, oy), 3)

# faint rune symbols on grid — circles with cross
for rx2, ry2 in [(160, 400), (470, 408), (260, 435), (380, 440)]:
    pygame.draw.circle(surf, (0, 50, 60), (rx2, ry2), 12, 1)
    pygame.draw.line(surf, (0,40,50), (rx2-12, ry2), (rx2+12, ry2), 1)
    pygame.draw.line(surf, (0,40,50), (rx2, ry2-12), (rx2, ry2+12), 1)


# ══════════════════════════════════════════════════════════════════════════════
# 9.  TITLE  (Old English + gothic neon)
# ══════════════════════════════════════════════════════════════════════════════
TITLE_STR  = "CYBER SURVIVOR"
CYBER_STR  = "CYBER"
SURV_STR   = "SURVIVOR"
GAP        = 16
MARGIN     = int(W * 0.04)
MAX_TITLE_W = W - MARGIN * 2

# pick Old English for the gothic vibe, fall back to Impact
title_font_names = ["impact", "franklingothicheavy", "arialblack", None]
sub_font_names   = ["garamond", "baskervilleoldface", "timesnewroman", "georgia", None]
tag_font_names   = ["garamond", "georgia", "timesnewroman", None]

# auto-size title font so CYBER + gap + SURVIVOR <= MAX_TITLE_W
t_size = 90
while t_size > 22:
    tf = get_font(title_font_names, t_size, bold=False)
    cw = tf.size(CYBER_STR)[0]
    sw = tf.size(SURV_STR)[0]
    if cw + GAP + sw <= MAX_TITLE_W:
        break
    t_size -= 2

title_font = get_font(title_font_names, t_size, bold=False)
sub_font   = get_font(sub_font_names, 22, bold=False)
tag_font   = get_font(tag_font_names, 17, bold=False)
class_font = get_font(sub_font_names, 19, bold=True)

cw = title_font.size(CYBER_STR)[0]
sw = title_font.size(SURV_STR)[0]
total_tw   = cw + GAP + sw
title_x    = (W - total_tw) // 2
title_y    = 68

# decorative horizontal rule above title
rule_pad = 10
pygame.draw.line(surf, DIM_CYAN,  (MARGIN, title_y - 14), (title_x - rule_pad, title_y - 14), 1)
pygame.draw.line(surf, DIM_MAG, (title_x + total_tw + rule_pad, title_y - 14), (W - MARGIN, title_y - 14), 1)
# small diamond ornaments
for dx2 in [MARGIN, title_x - rule_pad, title_x + total_tw + rule_pad, W - MARGIN]:
    pts2 = [(dx2, title_y-18),(dx2+4, title_y-14),(dx2, title_y-10),(dx2-4, title_y-14)]
    pygame.draw.polygon(surf, CYAN if dx2 < W//2 else MAGENTA, pts2)

# CYBER — cyan
glow_text(surf, CYBER_STR, title_font, CYAN, CYAN,
          title_x + cw//2, title_y, steps=5, spread=10)
outlined_text(surf, CYBER_STR, title_font, CYAN, (0,0,8),
              title_x + cw//2, title_y, outline=3)

# SURVIVOR — magenta
glow_text(surf, SURV_STR, title_font, MAGENTA, MAGENTA,
          title_x + cw + GAP + sw//2, title_y, steps=5, spread=10)
outlined_text(surf, SURV_STR, title_font, MAGENTA, (8,0,8),
              title_x + cw + GAP + sw//2, title_y, outline=3)

# underline rule
line_y2 = title_y + title_font.size(CYBER_STR)[1]//2 + 6
pygame.draw.line(surf, CYAN,    (title_x,           line_y2), (title_x + cw,               line_y2), 2)
pygame.draw.line(surf, MAGENTA, (title_x + cw + GAP,line_y2), (title_x + total_tw,          line_y2), 2)

# tagline with dark backing for readability
tagline = "Survive the void. Level up. Conquer the Abyss."
tl_surf = sub_font.render(tagline, True, (215, 215, 245))
tl_rect = tl_surf.get_rect(center=(W//2, title_y + 52))
if tl_surf.get_width() > W - MARGIN*2:
    sub_font2 = get_font(sub_font_names, 17, bold=False)
    tl_surf   = sub_font2.render(tagline, True, (215, 215, 245))
    tl_rect   = tl_surf.get_rect(center=(W//2, title_y + 52))
_tl_pad = 12
_tl_bg  = pygame.Surface((tl_rect.width + _tl_pad*2, tl_rect.height + 10), pygame.SRCALPHA)
pygame.draw.rect(_tl_bg, (0, 0, 25, 195), (0, 0, _tl_bg.get_width(), _tl_bg.get_height()), border_radius=5)
pygame.draw.rect(_tl_bg, (0, 150, 190, 130), (0, 0, _tl_bg.get_width(), _tl_bg.get_height()), 1, border_radius=5)
surf.blit(_tl_bg, (tl_rect.x - _tl_pad, tl_rect.y - 5))
surf.blit(tl_surf, tl_rect)

# EARLY ACCESS — diagonal corner ribbon, bottom-right
_rib_reach = 115            # reach along edge from corner
_rib_w     = 48             # ribbon band width
_rib_pts   = [
    (W - _rib_reach,           H),
    (W,                        H - _rib_reach),
    (W,                        H - _rib_reach + _rib_w),
    (W - _rib_reach + _rib_w,  H),
]
_rib_overlay = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.polygon(_rib_overlay, (195, 85, 0, 235), _rib_pts)
pygame.draw.polygon(_rib_overlay, (255, 165, 0, 200), _rib_pts, 2)
surf.blit(_rib_overlay, (0, 0))
_rib_tfont = get_font(tag_font_names, 14, bold=True)
_rib_tsurf = _rib_tfont.render("EARLY ACCESS", True, (255, 255, 255))
_rib_trot  = pygame.transform.rotate(_rib_tsurf, 45)
_rib_cx    = W - _rib_reach // 2 + _rib_w // 4
_rib_cy    = H - _rib_reach // 2 + _rib_w // 4
surf.blit(_rib_trot, _rib_trot.get_rect(center=(_rib_cx, _rib_cy)))


# 11. CRT / SCANLINE + VIGNETTE OVERLAY
# ══════════════════════════════════════════════════════════════════════════════
# Scanlines
scan = pygame.Surface((W, H), pygame.SRCALPHA)
for sy in range(0, H, 3):
    pygame.draw.line(scan, (0, 0, 0, 22), (0, sy), (W, sy))
surf.blit(scan, (0, 0))

# Vignette (darken edges)
vig = pygame.Surface((W, H), pygame.SRCALPHA)
for vy in range(H):
    for side in [0, W-1]:
        pass   # done per-column below would be slow; use rect gradients
# top/bottom bars
for i in range(40):
    a = int(120 * ((40 - i) / 40) ** 2)
    pygame.draw.line(vig, (0, 0, 0, a), (0, i),   (W, i))
    pygame.draw.line(vig, (0, 0, 0, a), (0, H-1-i),(W, H-1-i))
# left/right bars
for i in range(50):
    a = int(100 * ((50 - i) / 50) ** 2)
    pygame.draw.line(vig, (0, 0, 0, a), (i, 0),     (i, H))
    pygame.draw.line(vig, (0, 0, 0, a), (W-1-i, 0), (W-1-i, H))
surf.blit(vig, (0, 0))


# ── Save ─────────────────────────────────────────────────────────────────────
pygame.image.save(surf, OUT)
print(f"Saved {OUT}  ({W}×{H})")
pygame.quit()
