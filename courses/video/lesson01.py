"""第 1 课《机器是怎么学会的》线稿风格视频。

全课只用一个例子：机器人学徒学做菜。每讲一段做菜，右上角的概念卡点明它对应的概念。
字幕时间由讲解词长度自动计算，动画都挂在字幕的出现时间（cue）上，保证画面和讲解同步。

用法：
  python3 lesson01.py render OUT_DIR        并行渲染全部镜头并拼接成 OUT_DIR/lesson01.mp4，同时导出字幕
  python3 lesson01.py stills OUT_DIR        每个镜头抽几帧 PNG，用来检查画面
"""
import math
import os
import random
import subprocess
import sys
from multiprocessing import Pool

from PIL import Image, ImageDraw, ImageFont

W, H, S, FPS = 1280, 720, 2, 30
BG = (248, 247, 243)
INK = (32, 34, 40)
SOFT = (130, 133, 140)
FAINT = (205, 205, 200)
WHITE = (255, 255, 255)
BLUE = (44, 89, 224)
RED = (205, 58, 48)
GREEN = (30, 132, 86)
ORANGE = (214, 110, 30)
MARK = (255, 214, 80)
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONT_B = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
_fonts = {}


# ═════════════ 基础工具 ═════════════
def font(size, bold=False):
    k = (size, bold)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FONT_B if bold else FONT, int(size * S))
    return _fonts[k]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def seg(t, a, b):
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)


def mix(c1, c2, k):
    k = clamp(k)
    return tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))


def fade(c, k):
    return mix(BG, c, k)


def window(t, a, b, f=0.4):
    """在 [a, b] 区间内可见，两端各有 f 秒淡入淡出"""
    return min(seg(t, a, a + f), 1 - seg(t, b - f, b))


def text_w(s, size, bold=False):
    return font(size, bold).getlength(s) / S


def wrap(s, size, maxw, bold=False):
    lines, cur = [], ''
    for ch in s:
        if text_w(cur + ch, size, bold) > maxw and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    # 避免标点单独落到下一行开头：把上一行的最后一个字一起带下来
    for i in range(1, len(lines)):
        if lines[i][0] in '，。、；：？！…）"' and len(lines[i - 1]) > 1:
            lines[i] = lines[i - 1][-1] + lines[i]
            lines[i - 1] = lines[i - 1][:-1]
    return lines


def text(d, xy, s, size, color=INK, prog=1.0, bold=False, anchor='la'):
    n = math.ceil(len(s) * clamp(prog))
    if n > 0:
        d.text((xy[0] * S, xy[1] * S), s[:n], font=font(size, bold), fill=color, anchor=anchor)


def rough_line(p0, p1, seed, amp=1.3, n=None):
    rnd = random.Random(seed)
    L = math.dist(p0, p1) or 1
    n = n or max(2, int(L / 18))
    nx, ny = -(p1[1] - p0[1]) / L, (p1[0] - p0[0]) / L
    pts = []
    for i in range(n + 1):
        t = i / n
        off = (rnd.random() - 0.5) * 2 * amp * math.sin(math.pi * t)
        pts.append((p0[0] + (p1[0] - p0[0]) * t + nx * off, p0[1] + (p1[1] - p0[1]) * t + ny * off))
    return pts


def rough_poly(points, seed, closed=False, amp=1.3):
    pts = list(points) + ([points[0]] if closed else [])
    out = []
    for i in range(len(pts) - 1):
        part = rough_line(pts[i], pts[i + 1], seed + i, amp)
        out += part if i == 0 else part[1:]
    return out


def rough_rect(x0, y0, x1, y1, seed, amp=1.2):
    return rough_poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], seed, closed=True, amp=amp)


def rough_ellipse(cx, cy, rx, ry, seed=0, turns=1.05, amp=1.4, n=60):
    rnd = random.Random(seed)
    st = rnd.random() * math.tau
    return [(cx + (rx + (rnd.random() - .5) * amp * 2) * math.cos(st + turns * math.tau * i / n),
             cy + (ry + (rnd.random() - .5) * amp * 2) * math.sin(st + turns * math.tau * i / n)) for i in range(n + 1)]


def draw_path(d, pts, prog=1.0, color=INK, width=3):
    if prog <= 0 or len(pts) < 2:
        return
    lens = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total, acc, out = sum(lens) * clamp(prog), 0.0, [pts[0]]
    for i, l in enumerate(lens):
        if acc + l >= total:
            k = (total - acc) / l if l else 0
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k))
            break
        out.append(pts[i + 1])
        acc += l
    d.line([(x * S, y * S) for x, y in out], fill=color, width=int(width * S), joint='curve')
    r = width * S / 2
    for x, y in (out[0], out[-1]):
        d.ellipse((x * S - r, y * S - r, x * S + r, y * S + r), fill=color)


def strokes(d, items, p, color=INK, width=3):
    """按顺序逐笔画出一组线条"""
    n = len(items)
    for i, st in enumerate(items):
        draw_path(d, st, seg(p, i / n, (i + 1) / n), color, width)


def dashed(d, p0, p1, color, width=2, dash=8, gap=6, prog=1.0):
    L = math.dist(p0, p1)
    if L <= 0:
        return
    ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    s, end = 0, L * clamp(prog)
    while s < end:
        e = min(s + dash, end)
        d.line([((p0[0] + ux * s) * S, (p0[1] + uy * s) * S), ((p0[0] + ux * e) * S, (p0[1] + uy * e) * S)], fill=color, width=int(width * S))
        s += dash + gap


def arrow(d, p0, p1, prog=1.0, color=INK, width=3, seed=0, head=12):
    if prog <= 0:
        return
    pts = rough_line(p0, p1, seed, .8)
    draw_path(d, pts, prog, color, width)
    if prog >= 1:
        a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        for s_ in (-1, 1):
            q = (p1[0] - head * math.cos(a + s_ * .45), p1[1] - head * math.sin(a + s_ * .45))
            draw_path(d, [p1, q], 1, color, width)


def underline(d, x0, x1, y, prog, color=MARK, width=10, seed=1):
    draw_path(d, rough_line((x0, y), (x1, y + 3), seed, 2), ease(prog), color, width)


def dot(d, x, y, r, fill, outline=None, w=2):
    d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=fill, outline=outline, width=int(w * S) if outline else 0)


def box(d, x0, y0, x1, y1, k=1.0, fill=WHITE, outline=FAINT, r=10):
    d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, fill=mix(BG, fill, k), outline=mix(BG, outline, k), width=S)


def tick(d, x, y, prog, color=GREEN, seed=0, sz=16):
    draw_path(d, rough_poly([(x, y), (x + sz * .4, y + sz * .45), (x + sz, y - sz * .55)], seed, amp=.6), prog, color, 3.5)


def cross(d, x, y, r, prog, color=RED, seed=0, width=5):
    draw_path(d, rough_line((x - r, y - r), (x + r, y + r), seed, 2), seg(prog, 0, .5), color, width)
    draw_path(d, rough_line((x + r, y - r), (x - r, y + r), seed + 9, 2), seg(prog, .5, 1), color, width)


# ═════════════ 固定画面元素 ═════════════
def robot(d, cx, cy, s=1.0, p=1.0, mood='normal', color=INK, seed=0):
    """机器人学徒：方脑袋、天线、围裙。cy 是身体中心。"""
    P = lambda x, y: (cx + x * s, cy + y * s)
    its = [
        rough_rect(*P(-40, -118), *P(40, -60), seed),
        rough_line(P(0, -118), P(0, -134), seed + 1, .3),
        rough_ellipse(*P(0, -139), 5 * s, 5 * s, seed + 2, amp=.4, n=20),
        rough_ellipse(*P(-16, -94), 7 * s, 7 * s, seed + 3, amp=.4, n=24),
        rough_ellipse(*P(16, -94), 7 * s, 7 * s, seed + 4, amp=.4, n=24),
        rough_rect(*P(-46, -52), *P(46, 40), seed + 5),
        rough_poly([P(-28, -42), P(28, -42), P(32, 34), P(-32, 34)], seed + 6, closed=True, amp=.8),
        rough_line(P(-46, -40), P(-72, 2), seed + 7, .6), rough_line(P(46, -40), P(72, 2), seed + 8, .6),
        rough_line(P(-20, 40), P(-20, 70), seed + 9, .4), rough_line(P(20, 40), P(20, 70), seed + 10, .4),
    ]
    if mood == 'happy':
        its.append(rough_poly([P(-12, -77), P(0, -70), P(12, -77)], seed + 11, amp=.3))
    elif mood == 'confused':
        its.append(rough_poly([P(-12, -73), P(-6, -77), P(0, -73), P(6, -77), P(12, -73)], seed + 11, amp=.3))
    else:
        its.append(rough_line(P(-11, -74), P(11, -74), seed + 11, .3))
    strokes(d, its, p, color, max(2, 3 * s))
    if p >= 1 and mood == 'confused':
        text(d, P(52, -128), '?', int(30 * s), ORANGE, bold=True)


def plate(d, cx, cy, r, p=1.0, color=INK, style=0, seed=0, food=INK):
    its = [rough_ellipse(cx, cy, r, r * .42, seed), rough_ellipse(cx, cy, r * .68, r * .27, seed + 1, amp=1)]
    rnd = random.Random(style * 13 + 5)
    if style == 0:      # 一堆方块（红烧肉）
        for k in range(4):
            x = cx - r * .32 + k * r * .2
            its.append(rough_rect(x, cy - r * .16, x + r * .14, cy - r * .02, style * 7 + k, .5))
    elif style == 1:    # 几团圆（豆腐块）
        for k in range(3):
            its.append(rough_ellipse(cx - r * .3 + k * r * .3, cy - r * .08, r * .1, r * .07, style + k, amp=.4, n=16))
    elif style == 2:    # 一条曲线（汤汁）
        its.append(rough_poly([(cx - r * .4, cy - r * .05), (cx - r * .1, cy - r * .18), (cx + r * .15, cy - r * .02), (cx + r * .4, cy - r * .14)], style, amp=.8))
    else:               # 几根短线（葱花）
        for k in range(5):
            x = cx - r * .35 + rnd.random() * r * .7
            y = cy - r * .15 + rnd.random() * r * .12
            its.append(rough_line((x, y), (x + r * .1, y - r * .05), style + k, .2))
    strokes(d, its[:2], seg(p, 0, .6), color, 3)
    strokes(d, its[2:], seg(p, .5, 1), food, 2.5)


def gauge(d, cx, cy, r, v, p=1.0, label='错误分', value=None, seed=40):
    """测味道的仪器：半圆仪表，左边 0（好），右边高（差）"""
    arc = [(cx + r * math.cos(math.pi + math.pi * i / 40), cy + r * math.sin(math.pi + math.pi * i / 40)) for i in range(41)]
    draw_path(d, rough_poly(arc, seed, amp=.6), seg(p, 0, .6), INK, 3)
    draw_path(d, rough_line((cx - r - 14, cy), (cx + r + 14, cy), seed + 1, .5), seg(p, .3, .7), INK, 3)
    if p < .6:
        return
    for i in range(11):
        a = math.pi + math.pi * i / 10
        c = mix(GREEN, RED, i / 10)
        d.line([((cx + (r - 12) * math.cos(a)) * S, (cy + (r - 12) * math.sin(a)) * S), ((cx + r * math.cos(a)) * S, (cy + r * math.sin(a)) * S)], fill=c, width=int(3 * S))
    text(d, (cx - r, cy + 16), '0', 18, GREEN, anchor='ma')
    text(d, (cx + r, cy + 16), '高', 18, RED, anchor='ma')
    a = math.pi + math.pi * clamp(v, -.02, 1.02)
    draw_path(d, [(cx, cy), (cx + (r - 22) * math.cos(a), cy + (r - 22) * math.sin(a))], seg(p, .6, 1), RED, 4)
    dot(d, cx, cy, 7, INK)
    text(d, (cx, cy + 22), label, 20, SOFT, seg(p, .7, 1), anchor='ma')
    if value is not None:
        text(d, (cx, cy + 50), value, 26, INK, seg(p, .8, 1), bold=True, anchor='ma')


def slider(d, x, y0, y1, v, label, p=1.0, color=BLUE, seed=0, ghost=None, lsize=20):
    draw_path(d, rough_line((x, y0), (x, y1), seed, .5), seg(p, 0, .6), INK, 3)
    if p < .6:
        return
    if ghost is not None:
        gy = y1 - (y1 - y0) * ghost
        d.ellipse(((x - 11) * S, (gy - 11) * S, (x + 11) * S, (gy + 11) * S), outline=fade(color, .5), width=int(2 * S))
    ky = y1 - (y1 - y0) * clamp(v)
    dot(d, x, ky, 11, fade(color, seg(p, .6, 1)))
    text(d, (x, y1 + 14), label, lsize, INK, seg(p, .7, 1), anchor='ma')


def ucurve(f, x0, x1, y0, y1, lo=0.0, hi=1.0, ymax=1.0, n=120):
    """把函数 f 在 [lo, hi] 上画到矩形 (x0..x1, y0..y1) 里，返回点列和坐标换算函数"""
    X = lambda u: x0 + (u - lo) / (hi - lo) * (x1 - x0)
    Y = lambda v: y1 - clamp(v / ymax, -.05, 1.2) * (y1 - y0)
    return [(X(lo + (hi - lo) * i / n), Y(f(lo + (hi - lo) * i / n))) for i in range(n + 1)], X, Y


def aside_frame(d, t, y0=70):
    k = seg(t, 0, .6)
    if k <= 0:
        return
    c = fade(SOFT, k)
    for a, b in [((40, y0), (840, y0)), ((840, y0), (840, 615)), ((840, 615), (40, 615)), ((40, 615), (40, y0))]:
        dashed(d, a, b, c, 1.5, 10, 7)
    box(d, 56, y0 - 16, 170, y0 + 16, k, fill=WHITE, outline=SOFT, r=14)
    text(d, (113, y0), '了解即可', 18, c, anchor='mm')


def bars(d, cands, t0, t, x=330, y0=290, hl=0, k=1.0, scale=10):
    for i, (w, pct) in enumerate(cands):
        p = seg(t, t0 + i * .3, t0 + i * .3 + .8)
        if p <= 0:
            continue
        y = y0 + i * 58
        text(d, (x - 30, y + 19), w, 30, fade(INK, k), anchor='rm')
        bw = pct * scale * ease(p)
        lc = fade(BLUE if i == hl else INK, k)
        draw_path(d, rough_rect(x, y, x + max(bw, 2), y + 36, 100 + i, .7), 1, lc, 2.5)
        for xx in range(x + 8, int(x + bw) - 2, 12):
            d.line([(xx * S, (y + 34) * S), ((xx + 10) * S, (y + 2) * S)], fill=mix(BG, lc, .5), width=int(1.6 * S))
        text(d, (x + bw + 14, y + 19), f'{pct}%', 22, fade(SOFT, k), seg(t, t0 + i * .3 + .5, t0 + i * .3 + .9), anchor='lm')


def tag(d, x, y, s, k, size=19, color=INK, seed=0):
    if k <= 0:
        return
    w = text_w(s, size) + 26
    box(d, x, y, x + w, y + size + 18, k, fill=WHITE, outline=mix(FAINT, color, .35), r=16)
    text(d, (x + w / 2, y + (size + 18) / 2), s, size, fade(color, k), anchor='mm')


# ═════════════ 概念卡与字幕 ═════════════
def card(d, info, k):
    if k <= 0:
        return
    title, l1, l2 = info
    x0, y0, w = 862 + (1 - ease(k)) * 50, 22, 394
    a = wrap(l1, 18, w - 34)
    b = wrap(l2, 16, w - 34)
    h = 18 + 22 + 36 + len(a) * 27 + 6 + len(b) * 24 + 14
    box(d, x0, y0, x0 + w, y0 + h, ease(k), fill=WHITE, outline=(190, 196, 214), r=12)
    text(d, (x0 + 17, y0 + 16), '概念', 14, fade(SOFT, k))
    text(d, (x0 + 17, y0 + 36), title, 25, fade(BLUE, k), bold=True)
    y = y0 + 36 + 40
    for s_ in a:
        text(d, (x0 + 17, y), s_, 18, fade(INK, k))
        y += 27
    y += 6
    for s_ in b:
        text(d, (x0 + 17, y), s_, 16, fade(SOFT, k))
        y += 24


def subtitle(d, s, k):
    if k <= 0 or not s:
        return
    lines = wrap(s, 25, 1080)
    lh = 36
    hgt = len(lines) * lh + 18
    y0 = 706 - hgt
    w = max(text_w(l, 25) for l in lines) + 44
    box(d, 640 - w / 2, y0, 640 + w / 2, y0 + hgt, k, fill=WHITE, outline=(214, 214, 208), r=12)
    for i, l in enumerate(lines):
        text(d, (640, y0 + 9 + lh * i + lh / 2), l, 25, fade(INK, k), anchor='mm')


# ═════════════ 镜头 ═════════════
SHOTS = []


def shot(captions, card=None, card_cue=0, min_dur=0, pre=0.7, post=1.2):
    """card: (标题, 一句话, 大模型里) / 'keep' 沿用上一张 / None 不显示"""
    def deco(fn):
        SHOTS.append(dict(fn=fn, captions=captions, card=card, card_cue=card_cue, min_dur=min_dur, pre=pre, post=post))
        return fn
    return deco


def cap_dur(s):
    return clamp(len(s) * 0.25, 2.6, 9.5)


# ── 1 标题
@shot([], min_dur=6)
def s01(d, t, c):
    text(d, (640, 250), '第 1 课', 30, SOFT, seg(t, .2, .8), anchor='mm')
    text(d, (640, 330), '机器是怎么学会的', 66, INK, seg(t, .6, 2.2), bold=True, anchor='mm')
    w = text_w('机器是怎么学会的', 66, True)
    underline(d, 640 - w / 2, 640 + w / 2, 380, seg(t, 2.2, 3.0), BLUE, 5, 7)
    text(d, (640, 440), '一个机器人学徒学做菜的故事', 28, SOFT, seg(t, 3.0, 4.4), anchor='mm')


# ── 2 猜下一个字
@shot(['你每天用的 AI，比如 Claude、ChatGPT，看起来像在思考。',
       '其实它只做一件事：根据前面的字，猜下一个字。',
       '给它半句话：红烧肉要先把糖炒出……',
       '它会给每个可能的下一个字打一个把握：接"色"的把握最大，接"来"的小一些。',
       '它选一个接上，再猜下一个。它的每一个回答，都是这样一个字一个字猜出来的。'])
def s02(d, t, c):
    k = window(t, 0, c[2] - .1)
    if k > 0:
        draw_path(d, rough_rect(250, 140, 1030, 330, 3), seg(t, .2, 1.4), fade(INK, k), 3)
        draw_path(d, rough_poly([(330, 330), (310, 372), (370, 330)], 4), seg(t, 1.2, 1.6), fade(INK, k), 3)
        for i in range(3):
            r = 9 + 3 * math.sin(t * 4 + i)
            if t > 1.4:
                dot(d, 590 + i * 50, 235, r, fade(SOFT, k))
        text(d, (640, 300), 'AI 正在回答……', 20, fade(SOFT, k), seg(t, 1.6, 2.4), anchor='mm')
        text(d, (640, 450), '根据前面的字，猜下一个字', 46, fade(INK, k), seg(t, c[1], c[1] + 1.4), bold=True, anchor='mm')
        w = text_w('根据前面的字，猜下一个字', 46, True)
        underline(d, 640 - w / 2, 640 + w / 2, 486, seg(t, c[1] + 1.4, c[1] + 2.2) * k, MARK, 10, 2)
    if t < c[2]:
        return
    base, x0, y0 = '红烧肉要先把糖炒出', 150, 170
    text(d, (x0, y0), base, 54, INK, seg(t, c[2], c[2] + 1.6), bold=True, anchor='lm')
    bw = text_w(base, 54, True)
    added = ''
    if t > c[4] + 1.2:
        added = '色'
    if t > c[4] + 2.2:
        tail = '，再放五花肉'
        added = '色' + tail[:math.ceil(len(tail) * seg(t, c[4] + 2.2, c[4] + 4.4))]
    text(d, (x0 + bw, y0), added, 54, BLUE, bold=True, anchor='lm')
    cw = text_w(added, 54, True) if added else 0
    if int(t * 2.4) % 2 == 0 and t > c[2] + 1.6:
        d.line([((x0 + bw + cw + 6) * S, (y0 - 30) * S), ((x0 + bw + cw + 6) * S, (y0 + 30) * S)], fill=BLUE, width=3 * S)
    kb = 1 - seg(t, c[4] + 2.0, c[4] + 2.6)
    if kb > 0 and t > c[3]:
        bars(d, [('色', 58), ('来', 18), ('焦', 10), ('香', 8), ('泡', 6)], c[3] + .2, t, hl=0, k=kb)
        if t > c[4]:
            draw_path(d, rough_ellipse(300, 309, 38, 30, 3), ease(seg(t, c[4], c[4] + .8)), fade(BLUE, kb), 3.5)
            draw_path(d, rough_poly([(300, 278), (320, 236), (x0 + bw + 14, 204)], 21, amp=1), ease(seg(t, c[4] + .6, c[4] + 1.2)), fade(BLUE, kb), 3)


# ── 3 请出学徒
@shot(['这节课只回答一个问题：它是怎么学会猜得这么准的？',
       '为了讲清楚，我们请出一个机器人学徒，看它怎么学做菜。',
       '客人的点单，就相当于前面的字；',
       '学徒做出来的菜，就相当于模型猜的下一个字。'],
      card=('对应关系', '点单 = 前面的字', '学徒做出的菜 = 模型猜的下一个字'), card_cue=2)
def s03(d, t, c):
    k = window(t, 0, c[2] - .2)
    text(d, (640, 110), '它是怎么学会猜得这么准的？', 40, fade(INK, k), seg(t, .2, 1.8), bold=True, anchor='mm')
    robot(d, 420, 420, 1.15, seg(t, c[1], c[1] + 2.4), 'happy' if t > c[1] + 2.6 else 'normal')
    if t > c[2]:
        p = seg(t, c[2], c[2] + 1.2)
        draw_path(d, rough_rect(90, 300, 250, 470, 61), p, INK, 3)
        text(d, (170, 332), '点单', 24, INK, seg(t, c[2] + .6, c[2] + 1.0), bold=True, anchor='mm')
        for i in range(3):
            draw_path(d, rough_line((115, 372 + i * 26), (225, 372 + i * 26), 70 + i, .6), seg(t, c[2] + .8 + i * .15, c[2] + 1.1 + i * .15), SOFT, 2)
        text(d, (170, 500), '= 前面的字', 22, BLUE, seg(t, c[2] + 1.2, c[2] + 1.8), bold=True, anchor='mm')
        arrow(d, (262, 390), (325, 390), seg(t, c[2] + 1.4, c[2] + 2.0), INK, 3, 5)
    if t > c[3]:
        arrow(d, (515, 410), (600, 440), seg(t, c[3], c[3] + .6), INK, 3, 6)
        plate(d, 710, 455, 95, seg(t, c[3] + .4, c[3] + 1.8), style=0)
        text(d, (710, 540), '= 模型猜的下一个字', 22, BLUE, seg(t, c[3] + 1.6, c[3] + 2.4), bold=True, anchor='mm')


# ── 4 写规则
@shot(['最直接的办法，是给学徒一本超级菜谱。',
       '红烧肉放 15 克糖、炖 40 分钟，番茄炒蛋先炒蛋……一条条写清楚。',
       '可是肉有多有少，锅有大有小，四川人爱辣，广东人爱清淡，同一道菜还有十几种做法。',
       '情况无穷无尽，菜谱永远写不完。',
       '这就是早期的规则式 AI：人把语言规则一条条写进程序，可人说话的组合是无穷的，这条路走不通。'],
      card=('规则式 AI', '人把规则一条条写进程序', '大模型里：说话的组合无穷无尽，规则永远写不完，这条路走不通'), card_cue=4)
def s04(d, t, c):
    robot(d, 140, 440, .85, seg(t, 0, 1.5), 'confused' if t > c[3] else 'normal')
    p = seg(t, c[0], c[0] + 1.6)
    draw_path(d, rough_poly([(470, 210), (300, 225), (300, 470), (470, 455)], 31), p, INK, 3)
    draw_path(d, rough_poly([(470, 210), (640, 225), (640, 470), (470, 455)], 32), p, INK, 3)
    draw_path(d, rough_line((470, 210), (470, 455), 33, .5), p, INK, 3)
    rules = [('红烧肉：糖 15 克', 320, 250), ('炖 40 分钟', 320, 290), ('先大火后小火', 320, 330),
             ('番茄炒蛋：先炒蛋', 488, 260), ('盐 2 克', 488, 300), ('出锅撒葱花', 488, 340)]
    for i, (s_, x, y) in enumerate(rules):
        text(d, (x, y), s_, 17, INK, seg(t, c[1] + i * .5, c[1] + i * .5 + .6))
    tags = [('肉多？肉少？', 665, 235), ('锅大？锅小？', 665, 300), ('四川：多放辣', 665, 365), ('广东：要清淡', 665, 430), ('同一道菜，十几种做法', 330, 505)]
    for i, (s_, x, y) in enumerate(tags):
        tag(d, x, y, s_, seg(t, c[2] + i * .7, c[2] + i * .7 + .5), 18, ORANGE, i)
    if t > c[3]:
        n = int(12 + 99988 * ease(seg(t, c[3], c[3] + 2.4)) ** 3)
        text(d, (470, 390), f'第 {n:,} 页……', 24, RED, bold=True, anchor='mm')
        cross(d, 470, 340, 120, seg(t, c[3] + 2.4, c[3] + 3.2), seed=4, width=7)


# ── 5 从例子中学
@shot(['那就不写菜谱了。',
       '让学徒自己做，做完和师傅做好的菜比一比。',
       '差了，就改改自己的做法，再做下一道。',
       '这就是机器学习：不教规则，给它大量例子，让它自己猜、自己对比、自己调整。'],
      card=('机器学习', '不教规则，从大量例子中学', '大模型里：自己猜、自己对比、自己调整'), card_cue=3)
def s05(d, t, c):
    k = window(t, 0, c[1])
    if k > 0:
        draw_path(d, rough_rect(380, 230, 560, 400, 81), 1, fade(INK, k), 3)
        text(d, (470, 315), '菜谱', 30, fade(INK, k), bold=True, anchor='mm')
        cross(d, 470, 315, 95, seg(t, .3, 1.0) * k, color=fade(RED, k), seed=8, width=7)
    robot(d, 170, 430, 1.0, seg(t, c[0], c[0] + 1.5), 'confused' if c[2] < t < c[2] + 2.5 else ('happy' if t > c[2] + 2.5 else 'normal'))
    if t > c[1]:
        plate(d, 420, 470, 85, seg(t, c[1], c[1] + 1.2), BLUE, 0, 11)
        text(d, (420, 545), '学徒的菜', 20, BLUE, seg(t, c[1] + 1, c[1] + 1.4), anchor='mm')
        plate(d, 680, 470, 85, seg(t, c[1] + .8, c[1] + 2.0), GREEN, 2, 12)
        text(d, (680, 545), '师傅的菜', 20, GREEN, seg(t, c[1] + 1.8, c[1] + 2.2), anchor='mm')
        text(d, (550, 465), '≠', 44, RED, seg(t, c[1] + 2.2, c[1] + 2.5), bold=True, anchor='mm')
        text(d, (550, 405), '比一比', 20, SOFT, seg(t, c[1] + 2.3, c[1] + 2.7), anchor='mm')
    if t > c[2]:
        pts = [(170 + (420 - 170) * (i / 30), 300 - 70 * math.sin(math.pi * i / 30)) for i in range(31)][::-1]
        draw_path(d, rough_poly(pts, 91, amp=.6), ease(seg(t, c[2], c[2] + 1.2)), ORANGE, 3)
        text(d, (300, 225), '改一改，再做一道', 22, ORANGE, seg(t, c[2] + 1, c[2] + 1.6), bold=True, anchor='mm')


# ── 6 参数 = 手感
LAB6 = ['盐', '糖', '火候', '时间', '醋', '酱油']
UNIT6 = [('克', 8), ('克', 25), ('档', 9), ('分', 60), ('毫升', 15), ('毫升', 20)]


@shot(['学徒做菜靠的是手感：盐放几克、糖放几克、火开多大、炒多久。',
       '这些都是数字。学徒学习，就是在改这些数字。',
       '而且学徒只有一份手感，却要做所有的菜。',
       '这就是参数：模型里存着 n 个数字，学习就是调整它们。',
       '大模型的参数有几千亿个，同一组参数，要应付所有的句子。'],
      card=('参数', '模型里的 n 个数字，学习就是调整它们', '大模型里：几千亿个，同一组参数要应付所有句子'), card_cue=3)
def s06(d, t, c):
    kw = seg(t, c[4], c[4] + 1.0)
    k = 1 - kw
    robot(d, 120, 440, .85, seg(t, 0, 1.2) if k > 0 else 0, color=fade(INK, k))
    if k > 0 and t > .8:
        draw_path(d, rough_rect(99, 432, 141, 458, 7), 1, fade(BLUE, k), 2.5)
        arrow(d, (150, 440), (250, 380), seg(t, .9, 1.5), fade(BLUE, k), 2.5, 9)
        draw_path(d, rough_rect(260, 225, 830, 500, 71), seg(t, c[0] - .3, c[0] + .8), fade(INK, k), 3)
        for i, lab in enumerate(LAB6):
            v = .35 + .25 * math.sin(t * 1.3 + i * 1.7) if t > c[0] + 1 else .5
            x = 320 + i * 95
            slider(d, x, 260, 430, v, lab, seg(t, c[0] + i * .2, c[0] + i * .2 + .9) * k, fade(BLUE, k), i)
            if t > c[1]:
                u, mx = UNIT6[i]
                text(d, (x, 485), f'{round(v * mx)} {u}', 17, fade(BLUE, k), seg(t, c[1] + i * .15, c[1] + i * .15 + .4), anchor='mm')
        if t > c[1] + 1.5:
            text(d, (545, 205), '都是数字', 22, fade(INK, k), seg(t, c[1] + 1.5, c[1] + 2.0), bold=True, anchor='mm')
        if t > c[2]:
            for i in range(6):
                plate(d, 330 + i * 92, 572, 34, seg(t, c[2] + i * .15, c[2] + i * .15 + .8) * k, fade(INK, k), i % 4, 120 + i)
            text(d, (290, 572), '所有的菜', 18, fade(SOFT, k), seg(t, c[2], c[2] + .5), anchor='rm')
    if kw > 0:
        rnd = random.Random(5)
        cols, rows = 40, 12
        n = int(cols * rows * ease(seg(t, c[4], c[4] + 2.5)))
        for idx in range(n):
            i, j = idx % cols, idx // cols
            x, y = 70 + i * 19, 240 + j * 28
            d.line([(x * S, y * S), (x * S, (y + 20) * S)], fill=fade(SOFT, kw), width=S)
            dot(d, x, y + 4 + rnd.random() * 12, 3, fade(BLUE, kw))
        if t > c[4] + 1.8:
            box(d, 290, 340, 600, 430, seg(t, c[4] + 1.8, c[4] + 2.3), fill=WHITE, outline=BLUE, r=14)
            text(d, (445, 385), '几千亿个', 44, fade(BLUE, seg(t, c[4] + 1.8, c[4] + 2.3)), bold=True, anchor='mm')


# ── 7 标准答案
@shot(['学徒要对比，得有标准。',
       '好在师傅已经做好了成千上万道菜，摆在那里，直接拿来比就行。',
       '对应到大模型：拿一句现成的话，遮住最后一个字，让它猜。',
       '原文里的那个字，就是标准答案，不需要任何人去标注。',
       '所以整个互联网的文字都能拿来学。这种自己给自己出题的方式，叫自监督学习。'],
      card=('标准答案', '原文里真实的下一个字', '大模型里：不需要人标注，这叫自监督学习'), card_cue=3)
def s07(d, t, c):
    text(d, (60, 100), '要对比，得有标准', 32, INK, seg(t, .1, 1.2), bold=True)
    if t > c[1]:
        for i in range(7):
            r = 62 - i * 6
            plate(d, 120 + i * 108 - i * i * 2, 290, r, seg(t, c[1] + i * .25, c[1] + i * .25 + .9), GREEN, i % 4, 200 + i)
        text(d, (60, 360), '师傅做好的菜：成千上万道', 20, GREEN, seg(t, c[1] + 1.5, c[1] + 2.2))
    if t > c[2]:
        s_ = '红烧肉要先把糖炒出'
        x0, y0 = 100, 470
        box(d, x0 - 20, y0 - 40, x0 + 620, y0 + 40, seg(t, c[2], c[2] + .5), fill=WHITE, outline=FAINT)
        text(d, (x0, y0), s_, 36, INK, seg(t, c[2] + .3, c[2] + 1.3), bold=True, anchor='lm')
        bx = x0 + text_w(s_, 36, True) + 8
        lift = ease(seg(t, c[3], c[3] + 1.0))
        text(d, (bx + 22, y0), '色', 36, GREEN, 1 if t > c[3] else 0, bold=True, anchor='mm')
        if lift < 1 and t > c[2] + 1.3:
            yy = y0 - 60 * lift
            kk = 1 - lift
            d.rectangle([(bx) * S, (yy - 26) * S, (bx + 44) * S, (yy + 26) * S], fill=mix(BG, (215, 215, 210), kk), outline=fade(INK, kk), width=2 * S)
            text(d, (bx + 22, yy), '?', 30, fade(INK, kk), bold=True, anchor='mm')
        text(d, (bx + 70, y0), '← 遮住最后一个字' if t < c[3] else '← 标准答案', 20, ORANGE if t < c[3] else GREEN, seg(t, c[2] + 1.6, c[2] + 2.2), bold=True, anchor='lm')
    if t > c[4]:
        for i in range(10):
            p = seg(t, c[4] + i * .2, c[4] + i * .2 + .6)
            x = 120 + i * 60
            draw_path(d, rough_rect(x, 545, x + 34, 590, 300 + i, .6), p, SOFT, 2)
            for j in range(3):
                draw_path(d, rough_line((x + 6, 556 + j * 10), (x + 28, 556 + j * 10), 310 + i * 3 + j, .2), p, FAINT, 1.5)
        text(d, (740, 568), '整个互联网的文字', 20, INK, seg(t, c[4] + 1.5, c[4] + 2.2), bold=True, anchor='lm')


# ── 8 仪器打分
@shot(['学徒做完一道菜，放进一台仪器。',
       '仪器测出它和师傅的菜差多少，给出一个分数。',
       '差得越多，分数越高；一模一样，就是 0。',
       '注意，"差多少算多差"这个标准，是人事先定好的，仪器只负责按标准去测。',
       '这就是损失函数：打分的规则，由人选定。按规则算出来的分数，叫错误分。'],
      card=('损失函数 / 错误分', '损失函数：打分的规则，由人选定', '错误分：按规则算出的分数，越低越好，0 表示完全一样'), card_cue=4)
def s08(d, t, c):
    plate(d, 130, 330, 70, seg(t, 0, 1.0), BLUE, 0, 11)
    text(d, (130, 390), '学徒的菜', 18, BLUE, seg(t, .8, 1.2), anchor='mm')
    plate(d, 130, 500, 70, seg(t, .4, 1.4), GREEN, 2, 12)
    text(d, (130, 560), '师傅的菜', 18, GREEN, seg(t, 1.2, 1.6), anchor='mm')
    arrow(d, (215, 340), (420, 420), seg(t, c[0] + 1.2, c[0] + 1.8), INK, 3, 2)
    arrow(d, (215, 495), (420, 445), seg(t, c[0] + 1.4, c[0] + 2.0), INK, 3, 3)
    if t < c[1]:
        v, val = 0.0, None
    elif t < c[2]:
        u = seg(t, c[1], c[1] + 1.4)
        v = .55 + .12 * math.sin(u * 9) * (1 - u)
        val = '错误分 1.6'
    else:
        u1, u2 = seg(t, c[2], c[2] + 1.0), seg(t, c[2] + 2.4, c[2] + 3.4)
        v = .55 + (.92 - .55) * ease(u1) - .92 * ease(u2)
        val = '错误分 4.6' if u2 < .5 else '错误分 0'
    gauge(d, 610, 470, 150, v, seg(t, c[0] + .4, c[0] + 1.8), '测味道的仪器', val)
    if t > c[2]:
        tag(d, 470, 250, '差得越多 → 分越高', window(t, c[2], c[2] + 2.6), 19, RED, 1)
        tag(d, 470, 250, '一模一样 → 0', seg(t, c[2] + 2.6, c[2] + 3.1), 19, GREEN, 2)
    if t > c[3]:
        k = seg(t, c[3], c[3] + .6)
        box(d, 700, 300, 830, 360, k, fill=(255, 248, 214), outline=ORANGE, r=6)
        text(d, (765, 330), '打分规则', 20, fade(INK, k), bold=True, anchor='mm')
        p = seg(t, c[3] + .5, c[3] + 1.5)
        strokes(d, [rough_ellipse(790, 220, 14, 14, 401, amp=.4, n=24), rough_line((790, 234), (790, 268), 402, .3),
                    rough_line((790, 248), (765, 300), 403, .3), rough_line((790, 268), (775, 290), 404, .3), rough_line((790, 268), (805, 290), 405, .3)], p, INK, 2.5)
        text(d, (820, 225), '人定的', 18, ORANGE, seg(t, c[3] + 1.3, c[3] + 1.8), bold=True, anchor='lm')


# ── 9 把握 → 错误分
ROWS9 = [(100, 0.0), (90, 0.105), (50, 0.693), (20, 1.609), (1, 4.605)]


@shot(['在大模型里，错误分看的是：它给正确答案打了多少把握。',
       '给"色"百分之百的把握，错误分是 0。',
       '只给了 20%，错误分就高；几乎没想到是"色"，错误分会特别高。',
       '大模型普遍用一个叫"交叉熵"的公式来算，全部由程序自动完成。'],
      card='keep')
def s09(d, t, c):
    text(d, (60, 92), '错误分看的是：给正确答案"色"打了多少把握', 26, INK, seg(t, .1, 1.6), bold=True)
    text(d, (120, 172), '给"色"的把握', 18, SOFT, seg(t, c[0] + 1, c[0] + 1.5))
    text(d, (470, 172), '错误分', 18, SOFT, seg(t, c[0] + 1, c[0] + 1.5))
    for i, (pct, e) in enumerate(ROWS9):
        a = c[1] + i * .8 if i < 2 else c[2] + (i - 2) * 1.0
        p = seg(t, a, a + .6)
        if p <= 0:
            continue
        y = 210 + i * 66
        hl = (i == 0 and c[1] <= t < c[2]) or (i == 3 and c[2] <= t < c[2] + 3) or (i == 4 and c[2] + 3 <= t < c[3])
        if hl:
            box(d, 96, y - 10, 830, y + 46, 1, fill=(255, 250, 225), outline=(240, 220, 150), r=8)
        text(d, (120, y + 18), f'{pct}%', 26, INK, p, bold=True, anchor='lm')
        bw = pct * 2.2 * ease(p)
        if bw > 1:
            d.rectangle([(205) * S, (y + 8) * S, (205 + bw) * S, (y + 28) * S], fill=mix(BG, BLUE, .75))
        ew = e * 62 * ease(p)
        if ew > 1:
            d.rectangle([(470) * S, (y + 8) * S, (470 + ew) * S, (y + 28) * S], fill=mix(BG, RED, .8))
        text(d, (470 + max(ew, 0) + 12, y + 18), f'{e:.1f}', 24, RED if e > 1 else INK, p, bold=True, anchor='lm')
    if t > c[2] + 4:
        text(d, (120, 560), '越接近 0%，罚得越重', 22, RED, seg(t, c[2] + 4, c[2] + 4.6), bold=True)
    if t > c[3]:
        tag(d, 470, 548, '公式：交叉熵（程序自动算）', seg(t, c[3], c[3] + .6), 19, BLUE, 3)


# ── 10 明确与模糊
@shot(['有的菜能做准，有的菜做不准。',
       '宫保鸡丁，各家做法差不多，学徒可以做得和师傅几乎一样。',
       '家常豆腐就不同了，每个师傅做法都不一样，学徒怎么做，都不可能和所有人一样。',
       '对应到大模型："床前明月光，疑是地上"，后面几乎只能是"霜"。',
       '而"我想吃"后面，可以是火锅、面、饭，没有唯一答案，模型只能给出合理的比例。',
       '所以模型不可能百分之百准确。这不是没学好，而是语言本身就有很多种合理的说法。'],
      card=('明确 vs 模糊', '有的句子答案唯一，有的不唯一', '大模型里：模糊的地方只能给概率，不可能 100% 准确'), card_cue=3)
def s10(d, t, c):
    dashed(d, (455, 230), (455, 560), FAINT, 2, prog=seg(t, 0, 1))
    text(d, (250, 250), '宫保鸡丁', 28, INK, seg(t, c[0], c[0] + .8), bold=True, anchor='mm')
    text(d, (655, 250), '家常豆腐', 28, INK, seg(t, c[0] + .5, c[0] + 1.3), bold=True, anchor='mm')
    if t > c[1]:
        for i in range(3):
            plate(d, 120 + i * 130, 330, 48, seg(t, c[1] + i * .3, c[1] + i * .3 + .8), GREEN, 0, 500 + i)
        text(d, (60, 330), '师傅们', 16, GREEN, seg(t, c[1], c[1] + .4), anchor='rm')
        plate(d, 250, 435, 52, seg(t, c[1] + 1.2, c[1] + 2.0), BLUE, 0, 510)
        text(d, (250, 480), '学徒', 16, BLUE, seg(t, c[1] + 1.8, c[1] + 2.2), anchor='mm')
        tick(d, 320, 430, seg(t, c[1] + 2.2, c[1] + 2.7), sz=24)
    if t > c[2]:
        for i in range(3):
            plate(d, 530 + i * 125, 330, 48, seg(t, c[2] + i * .3, c[2] + i * .3 + .8), GREEN, i + 1, 520 + i)
        plate(d, 655, 435, 52, seg(t, c[2] + 1.2, c[2] + 2.0), BLUE, 1, 530)
        text(d, (655, 480), '学徒', 16, BLUE, seg(t, c[2] + 1.8, c[2] + 2.2), anchor='mm')
        text(d, (725, 430), '?', 40, ORANGE, seg(t, c[2] + 2.2, c[2] + 2.5), bold=True, anchor='mm')
    if t > c[3]:
        text(d, (80, 525), '疑是地上 →', 20, INK, seg(t, c[3], c[3] + .8))
        text(d, (200, 525), '霜 98%', 20, GREEN, seg(t, c[3] + .8, c[3] + 1.4), bold=True)
    if t > c[4]:
        text(d, (480, 525), '我想吃 →', 20, INK, seg(t, c[4], c[4] + .6))
        text(d, (572, 525), '火锅 30%｜面 25%｜饭 20%…', 19, BLUE, seg(t, c[4] + .6, c[4] + 2.0), bold=True)
    if t > c[5]:
        text(d, (455, 588), '不可能 100% 准确', 26, INK, seg(t, c[5], c[5] + .8), bold=True, anchor='mm')
        w = text_w('不可能 100% 准确', 26, True)
        underline(d, 455 - w / 2, 455 + w / 2, 606, seg(t, c[5] + .8, c[5] + 1.4), MARK, 8, 3)


# ── 11 最低点
eGB = lambda s: 2.6 * (s - .7) ** 2 + .08
eTF = lambda s: 2.6 * (s - .3) ** 2 + .45
eTOT = lambda s: eGB(s) + eTF(s)


@shot(['学徒只有一份手感，要做所有的菜。',
       '为了让宫保鸡丁更像，可能会让家常豆腐差一点。',
       '最好的手感，是所有菜加起来，总差距最小的那一份。',
       '把手感的每一种取值和总差距画出来，就像一座山。山的最低处，就是最低点。',
       '真实的大模型，这座山有几千亿个方向，但道理完全一样。',
       '而且因为有家常豆腐这种菜，最低点的总差距也不会是 0。'],
      card=('最低点', '让总错误分最小的那组参数', '大模型里：训练的目标；它的错误分不会是 0'), card_cue=3)
def s11(d, t, c):
    if t < c[1]:
        s_ = .15
    elif t < c[2]:
        s_ = .15 + .7 * ease(seg(t, c[1] + .3, c[1] + 3.0))
    elif t < c[3]:
        s_ = .85 - .35 * ease(seg(t, c[2] + .3, c[2] + 2.5))
    else:
        # 先从 0.5 扫到 0、再扫到 1 画出整条曲线，最后回到最低点 0.5
        u = seg(t, c[3] + .5, c[3] + 4.5)
        if u < .2:
            s_ = .5 - .5 * ease(u / .2)
        elif u < .75:
            s_ = ease((u - .2) / .55)
        else:
            s_ = 1 - .5 * ease((u - .75) / .25)
    p0 = seg(t, 0, 1.2)
    text(d, (95, 236), '手感', 20, INK, p0, bold=True, anchor='mm')
    slider(d, 95, 270, 520, s_, '', p0, BLUE, 7)
    gauge(d, 290, 305, 66, eGB(s_) / 1.6, seg(t, .3, 1.5), '宫保鸡丁', f'{eGB(s_):.2f}', 50)
    gauge(d, 290, 480, 66, eTF(s_) / 1.6, seg(t, .5, 1.7), '家常豆腐', f'{eTF(s_):.2f}', 60)
    if t > c[2]:
        k = seg(t, c[2], c[2] + .6)
        box(d, 160, 585, 420, 622, k, fill=(255, 250, 225), outline=ORANGE, r=8)
        text(d, (290, 603), f'总差距 {eTOT(s_):.2f}', 22, fade(INK, k), bold=True, anchor='mm')
    if t > c[3]:
        pts, X, Y = ucurve(eTOT, 480, 820, 270, 560, 0, 1, 2.2)
        draw_path(d, rough_line((480, 560), (830, 560), 70, .4), seg(t, c[3], c[3] + .6), INK, 2.5)
        draw_path(d, rough_line((480, 560), (480, 255), 71, .4), seg(t, c[3], c[3] + .6), INK, 2.5)
        text(d, (830, 580), '手感', 17, SOFT, seg(t, c[3] + .4, c[3] + .8), anchor='ra')
        text(d, (488, 262), '总差距', 17, SOFT, seg(t, c[3] + .4, c[3] + .8))
        reveal = 1.0 if t > c[3] + 3.0 else 0.0
        if reveal == 0 and t > c[3] + .5:
            # 扫描阶段：只画出已经扫过的部分，看起来是"一边拧一边画"
            seen = [p for p in pts if p[0] <= X(max(s_, 0)) + 1] if seg(t, c[3] + .5, c[3] + 4.5) > .2 else []
            if len(seen) > 1:
                draw_path(d, seen, 1, INK, 3)
        draw_path(d, pts, reveal, INK, 3)
        if reveal > 0:
            dot(d, X(s_), Y(eTOT(s_)), 8, BLUE)
        if t > c[3] + 4.5:
            k = seg(t, c[3] + 4.5, c[3] + 5.1)
            dashed(d, (X(.5), Y(eTOT(.5)) + 10), (X(.5), 560), fade(GREEN, k), 2)
            text(d, (X(.5), 588 - 4), '最低点', 18, fade(GREEN, k), bold=True, anchor='ma')
    if t > c[4]:
        tag(d, 520, 228, '真实的山：几千亿个方向', seg(t, c[4], c[4] + .6), 18, BLUE, 4)
    if t > c[5]:
        X = lambda u: 480 + u * 340
        Y = lambda v: 560 - v / 2.2 * 290
        k = seg(t, c[5], c[5] + .6)
        x = X(.5) + 40
        draw_path(d, [(x, 560), (x, Y(eTOT(.5)))], k, RED, 2.5)
        text(d, (x + 10, (560 + Y(eTOT(.5))) / 2), '≠ 0', 22, fade(RED, k), bold=True, anchor='lm')


# ── 12 过拟合（了解即可）
@shot(['了解一下：如果学徒把练习过的每道菜都背得一模一样，仪器会给它打 0 分。',
       '可是来了一道没做过的新菜，它就不会做了。',
       '这叫过拟合：背下来不等于学会。所以要留一部分它没见过的文字，专门用来检验，叫测试集。'],
      card=('过拟合', '把练习题背下来了，新题却不会', '大模型里：用没见过的测试集来检验'), card_cue=2)
def s12(d, t, c):
    aside_frame(d, t)
    robot(d, 170, 420, .95, seg(t, .3, 1.6), 'happy' if t < c[1] else 'confused')
    p = seg(t, c[0] + .5, c[0] + 1.6)
    draw_path(d, rough_rect(270, 260, 400, 370, 601), p, INK, 2.5)
    text(d, (335, 290), '背', 26, INK, seg(t, c[0] + 1.2, c[0] + 1.6), bold=True, anchor='mm')
    for j in range(3):
        draw_path(d, rough_line((290, 320 + j * 15), (380, 320 + j * 15), 602 + j, .2), seg(t, c[0] + 1.4, c[0] + 1.9), SOFT, 2)
    if t < c[1]:
        v, val = 0.0, '练习过的菜：0 分'
    else:
        v, val = .9 * ease(seg(t, c[1] + 1.2, c[1] + 2.2)), ('没见过的新菜：很高' if t > c[1] + 1.6 else '练习过的菜：0 分')
    gauge(d, 640, 430, 110, v, seg(t, c[0] + 1, c[0] + 2.4), '仪器', val, 610)
    if t > c[1]:
        plate(d, 335, 495, 62, seg(t, c[1], c[1] + 1.0), INK, 3, 620)
        text(d, (335, 545), '新菜', 18, ORANGE, seg(t, c[1] + .8, c[1] + 1.2), bold=True, anchor='mm')
    if t > c[2] + 3:
        tag(d, 470, 560, '测试集：考试时用没见过的题', seg(t, c[2] + 3, c[2] + 3.6), 18, BLUE, 6)


# ── 13 梯度下降：一样一样试
def s13_state(t, c):
    salt, sugar, fire, gh, needle, msg = .45, .55, .5, None, .55, ''
    if c[1] <= t < c[2]:
        u = seg(t, c[1] + .5, c[1] + 1.2)
        salt, gh = .45 + .08 * ease(u), ('salt', .45)
        needle = .55 - .1 * ease(seg(t, c[1] + 1.2, c[1] + 2.0))
    elif c[2] <= t < c[3]:
        u = seg(t, c[2] + .5, c[2] + 1.2)
        sugar, gh = .55 + .08 * ease(u), ('sugar', .55)
        needle = .55 + .12 * ease(seg(t, c[2] + 1.2, c[2] + 2.0))
    elif c[3] <= t < c[4]:
        fire = .5 + .05 * math.sin((t - c[3]) * 5) * (1 - seg(t, c[3] + 2.5, c[3] + 3))
        needle = .55 + .005 * math.sin((t - c[3]) * 5)
    elif t >= c[4]:
        u = ease(seg(t, c[4] + .6, c[4] + 2.2))
        salt, sugar, fire = .45 + .1 * u, .55 - .1 * u, .5 + .01 * u
        needle = .55 - .2 * u
    return salt, sugar, fire, gh, needle


@shot(['知道了差多少，手感该怎么改？学徒的办法是：一样一样试。',
       '盐多放一点点，送进仪器：分数降了，说明加盐是对的，那就往加盐的方向改。',
       '糖多放一点点：分数反而升了，说明方向反了，那就少放点糖。',
       '火候动一动，分数几乎不变，说明它跟这次的差距关系不大，少改或者不改。',
       '所有调料都这样，同时改一小步。这就是梯度下降。'],
      card=('梯度下降', '每个参数试着动一点，往错误分变小的方向改', '大模型里：变化越明显的参数，改得越多'), card_cue=4)
def s13(d, t, c):
    salt, sugar, fire, gh, needle = s13_state(t, c)
    p = seg(t, 0, 1.4)
    for i, (lab, v, key) in enumerate([('盐', salt, 'salt'), ('糖', sugar, 'sugar'), ('火候', fire, 'fire')]):
        slider(d, 150 + i * 120, 270, 500, v, lab, p, BLUE, 30 + i, ghost=gh[1] if gh and gh[0] == key else None, lsize=22)
    gauge(d, 640, 470, 145, needle, seg(t, .4, 1.8), '仪器', f'错误分 {needle * 3:.2f}', 700)
    if c[1] + 2.2 < t < c[2]:
        k = seg(t, c[1] + 2.2, c[1] + 2.7)
        arrow(d, (190, 420), (190, 300), k, GREEN, 4, 2)
        text(d, (205, 250), '降了 ✓ 往这边改', 19, fade(GREEN, k), bold=True)
    if c[2] + 2.2 < t < c[3]:
        k = seg(t, c[2] + 2.2, c[2] + 2.7)
        arrow(d, (310, 300), (310, 420), k, RED, 4, 3)
        text(d, (325, 250), '升了 ✗ 反方向改', 19, fade(RED, k), bold=True)
    if c[3] + 1.2 < t < c[4]:
        text(d, (390, 250), '≈ 关系不大', 19, fade(SOFT, seg(t, c[3] + 1.2, c[3] + 1.7)), bold=True, anchor='ma')
    if t > c[4] + .6:
        tag(d, 140, 565, '所有调料一起改一小步', seg(t, c[4] + .6, c[4] + 1.2), 19, BLUE, 5)


# ── 14 蒙眼下山
f14 = lambda u: 1.6 * (u - .62) ** 2 + .12 * math.sin(u * 3) + .2
STEPS14 = [.08]
for _ in range(9):
    u = STEPS14[-1]
    g = (f14(u + 1e-4) - f14(u - 1e-4)) / 2e-4
    STEPS14.append(u - .18 * g)


@shot(['每个参数动一点，错误分怎么变，这个变化的方向和快慢，叫梯度，就像山坡的坡度。',
       '这就像蒙着眼睛下山：看不见谷底在哪，但能感觉到脚下哪边是下坡。',
       '于是往下坡迈一步，再感觉，再迈一步，一直走到谷底。每一步，就是学徒改一次调料。'],
      card='keep')
def s14(d, t, c):
    pts, X, Y = ucurve(f14, 90, 820, 250, 560, 0, 1, .9)
    draw_path(d, pts, seg(t, 0, 1.6), INK, 3)
    text(d, (90, 590), '参数的取值 →', 18, SOFT, seg(t, 1, 1.5))
    text(d, (90, 232), '错误分 ↑', 18, SOFT, seg(t, 1, 1.5))
    n = int(clamp((t - c[2] - .8) / .7, 0, len(STEPS14) - 1)) if t > c[2] + .8 else 0
    fr = clamp((t - c[2] - .8) / .7 - n) if t > c[2] + .8 and n < len(STEPS14) - 1 else 0
    u = STEPS14[n] + (STEPS14[min(n + 1, len(STEPS14) - 1)] - STEPS14[n]) * ease(fr)
    for k in range(n):
        dot(d, X(STEPS14[k]), Y(f14(STEPS14[k])), 4, fade(ORANGE, .5))
    bx, by = X(u), Y(f14(u)) - 14
    if t > 1.2:
        dot(d, bx, by, 14, ORANGE, WHITE, 2)
        if t > c[1]:
            k = seg(t, c[1], c[1] + .5)
            d.rectangle([(bx - 15) * S, (by - 6) * S, (bx + 15) * S, (by + 1) * S], fill=fade(INK, k))
    if c[0] + .6 < t < c[2] + .8:
        g = (f14(u + 1e-4) - f14(u - 1e-4)) / 2e-4
        k = seg(t, c[0] + .6, c[0] + 1.2)
        dx = 70
        sy = g * (dx / 730) / .9 * 310
        dashed(d, (X(u) - dx, Y(f14(u)) - sy), (X(u) + dx, Y(f14(u)) + sy), fade(BLUE, k), 2.5)
        text(d, (X(u) + dx + 10, Y(f14(u)) + sy), '坡度（梯度）', 19, fade(BLUE, k), bold=True, anchor='lm')
    if t > c[2] + .8:
        text(d, (560, 300), f'第 {n + 1} 步 = 改一次调料' if n < len(STEPS14) - 1 else '到了谷底', 22, ORANGE, bold=True)


# ── 15 学习率
def gd_track(lr, n=12, u0=.08):
    us = [u0]
    for _ in range(n):
        us.append(us[-1] - lr * 2 * (us[-1] - .5))
    return us


TRK15 = [('改太少', gd_track(.06)), ('刚刚好', gd_track(.38)), ('改太多', gd_track(1.08))]


@shot(['每次改多少，也有讲究。',
       '改太少：每次加一粒盐，要调到天黑。',
       '改太多：太淡了猛加盐，结果太咸；又猛减，又太淡，来回折腾，甚至越调越差。',
       '这就是学习率：控制每一步改多少。太大会来回震荡，太小学得很慢。'],
      card=('学习率', '每一步改多少', '大模型里：太大来回震荡甚至越调越差，太小训练很慢'), card_cue=3)
def s15(d, t, c):
    for i, (lab, tr) in enumerate(TRK15):
        cx0 = 70 + i * 260
        f = lambda u: (u - .5) ** 2 * 4
        pts, X, Y = ucurve(f, cx0, cx0 + 220, 300, 520, 0, 1, 1.1)
        draw_path(d, pts, seg(t, i * .3, i * .3 + 1.2), INK, 3)
        text(d, (cx0 + 110, 270), lab, 24, [BLUE, GREEN, RED][i], seg(t, .4 + i * .3, 1 + i * .3), bold=True, anchor='mm')
        start = c[1] if i < 2 else c[2]
        if i == 1:
            start = c[1] + 1.5
        if t < start:
            n, fr = 0, 0
        else:
            q = (t - start) / .55
            n, fr = min(int(q), len(tr) - 1), q - int(q)
            if n >= len(tr) - 1:
                fr = 0
        u = tr[n] + (tr[min(n + 1, len(tr) - 1)] - tr[n]) * ease(fr)
        for k in range(n):
            if 0 <= tr[k] <= 1:
                dot(d, X(tr[k]), Y(f(tr[k])), 3.5, fade(ORANGE, .5))
        if -.05 <= u <= 1.05:
            dot(d, X(u), Y(f(u)) - 11, 11, ORANGE, WHITE, 2)
        elif i == 2:
            text(d, (cx0 + 110, 560), '被甩出去了！', 20, RED, bold=True, anchor='mm')
        if i == 0 and t > start + 3:
            text(d, (cx0 + 110, 560), '走了半天还没到', 18, SOFT, seg(t, start + 3, start + 3.5), anchor='mm')
        if i == 1 and n >= 5:
            text(d, (cx0 + 110, 560), '几步就到谷底', 18, GREEN, bold=True, anchor='mm')


# ── 16 训练循环
NODES16 = [((440, 260), '点单', '拿一段文字，遮住下一个字'), ((700, 405), '学徒做菜', '模型用当前参数猜'),
           ((440, 545), '仪器打分', '和原文对比，算错误分'), ((180, 405), '调手感', '参数往下坡改一小步')]


@shot(['学徒的一天就是这样：接单做菜，送进仪器打分，按分数改一点手感，接着做下一道。',
       '大模型的训练也是这样：拿一段文字，遮住下一个字；',
       '模型用当前的参数猜；和原文对比，算出错误分；',
       '所有参数往错误分变小的方向改一小步，然后换下一段文字。',
       '这个循环重复几万亿次，几千亿个参数被慢慢调好，这就叫训练。',
       '用海量文字练"猜下一个字"的这个阶段，叫预训练。',
       '所以"模型学会了"，意思就是：它的参数被调到了让错误分很低的位置。'],
      card=('训练 / 预训练', '做、打分、调整，重复无数次', '预训练：用海量文字练"猜下一个字"，把几千亿个参数调好'), card_cue=4)
def s16(d, t, c):
    reveal = [c[1], c[2], c[2] + 2.2, c[3]]
    for i, ((x, y), a, b) in enumerate(NODES16):
        p = seg(t, i * .5, i * .5 + 1.0)
        on = c[0] < t < c[1] and int((t - c[0]) / 1.4) % 4 == i
        box(d, x - 110, y - 38, x + 110, y + 38, p, fill=(232, 238, 252) if on else WHITE, outline=BLUE if on else (180, 180, 176), r=12)
        text(d, (x, y - 12 if t > reveal[i] else y), a, 22, fade(INK, p), bold=True, anchor='mm')
        if t > reveal[i]:
            text(d, (x, y + 16), b, 15, BLUE, seg(t, reveal[i], reveal[i] + 1.2), anchor='mm')
    links = [((540, 275), (650, 360)), ((650, 450), (540, 530)), ((340, 530), (230, 450)), ((230, 360), (340, 275))]
    for i, (a, b) in enumerate(links):
        arrow(d, a, b, seg(t, 1.6 + i * .3, 2.2 + i * .3), SOFT, 3, 20 + i)
    if t > c[4]:
        speed = 1 + 30 * ease(seg(t, c[4], c[4] + 5)) ** 2
        ang = ((t - c[4]) * speed) % (2 * math.pi)
        dot(d, 440 + 200 * math.cos(ang), 405 + 120 * math.sin(ang), 9, ORANGE)
        n = 10 ** (1 + 11 * ease(seg(t, c[4] + .3, c[4] + 4.5)))
        label = f'第 {int(n):,} 次' if n < 1e12 * .99 else '几万亿次'
        text(d, (440, 405), label, 24 if n < 1e8 else 26, INK, bold=True, anchor='mm')
    if t > c[6]:
        tag(d, 120, 590, '学会了 = 参数被调到错误分很低的位置', seg(t, c[6], c[6] + .7), 19, BLUE, 9)


# ── 17 局部最低点（了解即可）
f17 = lambda x: .09 * (x - 6.6) ** 2 + .55 * math.sin(2.3 * x) + .22 * math.sin(5.1 * x + 1) + 1.6


def track17(mom):
    x, v, out = 1.2, 0, [1.2]
    for _ in range(140):
        g = (f17(x + 1e-4) - f17(x - 1e-4)) / 2e-4
        if mom:
            v = .88 * v - .05 * g
            x += v
        else:
            x -= .12 * g
        out.append(min(10, max(0, x)))
    return out


TA17, TB17 = track17(False), track17(True)
GMIN17 = min((i / 200 for i in range(2001)), key=f17)


@shot(['了解一下：学徒可能调到一种口味，往哪个方向微调都变差，于是就停在那儿了。',
       '其实换一套完全不同的做法，可能更好吃。',
       '这叫局部最低点：山上不止一个坑。实际训练会加上"惯性"，让它能冲过一些小坑。好在大模型找到的坑，通常已经足够低。'],
      card=('局部最低点', '停在了一个不是最低的坑', '大模型里：加上惯性能冲过小坑；找到的坑通常足够低'), card_cue=2)
def s17(d, t, c):
    aside_frame(d, t)
    pts, X, Y = ucurve(f17, 80, 820, 120, 560, 0, 10, 6.0)
    draw_path(d, pts, seg(t, .3, 1.8), INK, 3)

    def ball(track, start, color, trail):
        q = clamp((t - start) * 20, 0, len(track) - 1) if t > start else 0
        x = track[int(q)]
        if trail:
            for k in range(0, int(q), 3):
                dot(d, X(track[k]), Y(f17(track[k])), 3, fade(color, .45))
        dot(d, X(x), Y(f17(x)) - 11, 11, color, WHITE, 2)
        return x

    if t > 1.5:
        xa = ball(TA17, c[0] + .5, BLUE, False)
        if t > c[0] + 4:
            text(d, (X(xa), Y(f17(xa)) - 40), '停住了', 18, BLUE, seg(t, c[0] + 4, c[0] + 4.4), bold=True, anchor='mm')
    if t > c[1]:
        k = seg(t, c[1], c[1] + .6)
        dashed(d, (X(GMIN17), Y(f17(GMIN17)) + 14), (X(GMIN17), 580), fade(GREEN, k), 2)
        text(d, (X(GMIN17), 592), '最深的坑', 18, fade(GREEN, k), bold=True, anchor='mm')
    if t > c[2] + 3:
        xb = ball(TB17, c[2] + 3.5, ORANGE, True)
        text(d, (120, 590), '橙色：加了惯性', 18, ORANGE, seg(t, c[2] + 3.5, c[2] + 4), bold=True)
        if t > c[2] + 9:
            text(d, (X(xb), Y(f17(xb)) + 30), '冲过小坑，到了深得多的坑', 18, ORANGE, seg(t, c[2] + 9, c[2] + 9.6), bold=True, anchor='mm')


# ── 18 回顾
RECAP = [('学徒的手感', '参数'), ('师傅做好的菜', '标准答案（原文里的下一个字）'), ('测味道的仪器', '损失函数 / 错误分'),
         ('所有菜总差距最小的手感', '最低点'), ('每样调料试一试，往对的方向改', '梯度下降'), ('每次改多少', '学习率'),
         ('做菜、打分、改手感，日复一日', '训练')]


@shot(['回顾一下学徒的故事。',
       '学徒的手感，就是参数；师傅做好的菜，就是标准答案。',
       '测味道的仪器，是损失函数；所有菜总差距最小的手感，是最低点。',
       '每样调料加一点试试，往对的方向改，是梯度下降；每次改多少，是学习率。',
       '做菜、打分、改手感，日复一日，就是训练。'])
def s18(d, t, c):
    text(d, (640, 70), '学徒做菜  ↔  大模型', 32, INK, seg(t, .1, 1.2), bold=True, anchor='mm')
    starts = [c[1], c[1] + 2.4, c[2], c[2] + 2.6, c[3], c[3] + 3.2, c[4]]
    for i, (a, b) in enumerate(RECAP):
        p = seg(t, starts[i], starts[i] + .6)
        if p <= 0:
            continue
        y = 120 + i * 66
        box(d, 190, y, 1090, y + 54, p, fill=WHITE, outline=FAINT, r=10)
        text(d, (220, y + 27), a, 22, fade(INK, p), anchor='lm')
        text(d, (690, y + 27), '→', 22, fade(SOFT, p), anchor='mm')
        text(d, (730, y + 27), b, 22, fade(BLUE, p), bold=True, anchor='lm')


# ── 19 下一课
@shot(['但还有一个问题：学徒只有几十种调料，可以一样一样试。',
       '大模型有几千亿个参数，每个都"多放一点试一下"，永远也试不完。',
       '而且，学徒的手感里面，到底是怎么组织起来的？',
       '下一课，我们走进厨房的流水线，看看神经网络是什么，以及菜做砸了，怎么一下子就知道该怪哪个工位。'],
      card=('下一课', '神经网络', '菜做砸了，怎么一下子就知道该怪哪个工位'), card_cue=3, post=3.0)
def s19(d, t, c):
    k = 1 - seg(t, c[2], c[2] + .8)
    if k > 0:
        rnd = random.Random(9)
        cols, rows = 38, 11
        for idx in range(cols * rows):
            i, j = idx % cols, idx // cols
            x, y = 70 + i * 19, 230 + j * 28
            hot = t > c[1] and rnd.random() < .08 + .5 * seg(t, c[1], c[1] + 4) and (int(t * 6) + idx) % 7 == 0
            d.line([(x * S, y * S), (x * S, (y + 20) * S)], fill=fade(ORANGE if hot else SOFT, k), width=S)
            dot(d, x, y + 4 + rnd.random() * 12, 3, fade(ORANGE if hot else BLUE, k))
        if t > c[1] + 1:
            box(d, 250, 340, 590, 420, seg(t, c[1] + 1, c[1] + 1.5) * k, fill=WHITE, outline=RED, r=14)
            text(d, (420, 380), '永远也试不完', 36, fade(RED, seg(t, c[1] + 1, c[1] + 1.5) * k), bold=True, anchor='mm')
    if t > c[2]:
        p = seg(t, c[2] + .6, c[2] + 2.4)
        for i in range(4):
            x = 90 + i * 190
            draw_path(d, rough_rect(x, 330, x + 130, 430, 900 + i), seg(p, i * .18, i * .18 + .35), INK, 3)
            text(d, (x + 65, 380), f'工位 {i + 1}', 20, INK, seg(p, i * .18 + .3, i * .18 + .45), anchor='mm')
            if i < 3:
                arrow(d, (x + 135, 380), (x + 185, 380), seg(p, i * .18 + .3, i * .18 + .45), SOFT, 3, 910 + i)
        draw_path(d, rough_line((80, 460), (830, 460), 930, .6), p, SOFT, 2.5)
        text(d, (455, 290), '?', 54, ORANGE, seg(t, c[2] + 2.2, c[2] + 2.6), bold=True, anchor='mm')
    if t > c[3] + 5:
        text(d, (455, 545), '下一课：神经网络', 34, BLUE, seg(t, c[3] + 5, c[3] + 6.2), bold=True, anchor='mm')


# ═════════════ 时间轴与渲染 ═════════════
def build():
    out, prev_card = [], None
    for sh in SHOTS:
        cues, ends, cur = [], [], sh['pre']
        for s_ in sh['captions']:
            cues.append(cur)
            dur = cap_dur(s_)
            ends.append(cur + dur)
            cur += dur + .3
        total = max(sh['min_dur'], cur - .3 + sh['post'])
        cd = sh['card']
        if cd == 'keep':
            info, appear = prev_card, None
        elif cd:
            info, appear = cd, cues[sh['card_cue']]
        else:
            info, appear = None, None
        prev_card = info
        out.append(dict(sh, cues=cues, ends=ends, dur=total, card_info=info, card_at=appear))
    return out


def frame(sh, t):
    img = Image.new('RGB', (W * S, H * S), BG)
    d = ImageDraw.Draw(img)
    sh['fn'](d, t, sh['cues'])
    if sh['card_info']:
        k = 1.0 if sh['card_at'] is None else seg(t, sh['card_at'], sh['card_at'] + .6)
        card(d, sh['card_info'], k)
    for a, b, s_ in zip(sh['cues'], sh['ends'], sh['captions']):
        if a - .2 <= t <= b + .2:
            subtitle(d, s_, min(seg(t, a - .2, a + .1), 1 - seg(t, b - .1, b + .2)))
    return img.reduce(S)


def render_shot(args):
    idx, out_dir = args
    sh = build()[idx]
    path = os.path.join(out_dir, f'seg_{idx:02d}.mp4')
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', path], stdin=subprocess.PIPE)
    for f in range(int(sh['dur'] * FPS)):
        ff.stdin.write(frame(sh, f / FPS).tobytes())
    ff.stdin.close()
    ff.wait()
    return path


def srt(shots, path):
    def ts(x):
        return f'{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(round((x - int(x)) * 1000)) % 1000:03d}'
    lines, n, off = [], 1, 0.0
    for sh in shots:
        for a, b, s_ in zip(sh['cues'], sh['ends'], sh['captions']):
            lines += [str(n), f'{ts(off + a)} --> {ts(off + b)}', s_, '']
            n += 1
        off += int(sh['dur'] * FPS) / FPS
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))


def main():
    mode, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    shots = build()
    print(f'{len(shots)} 个镜头，共 {sum(s["dur"] for s in shots) / 60:.1f} 分钟')
    if mode == 'stills':
        only = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else range(len(shots))
        for i in only:
            sh = shots[i]
            for q in (.35, .7, .97):
                frame(sh, sh['dur'] * q).save(os.path.join(out_dir, f'still_{i + 1:02d}_{int(q * 100)}.png'))
        return
    with Pool(int(os.environ.get('JOBS', os.cpu_count() or 2))) as pool:
        paths = pool.map(render_shot, [(i, out_dir) for i in range(len(shots))])
    lst = os.path.join(out_dir, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{os.path.abspath(p)}'\n" for p in paths))
    final = os.path.join(out_dir, 'lesson01.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', final], check=True)
    srt(shots, os.path.join(out_dir, 'lesson01.srt'))
    print('done', final)


if __name__ == '__main__':
    main()
