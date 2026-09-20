# -*- coding: utf-8 -*-
"""
Converte uma imagem em arte ASCII com tonalidade (cor por caractere).

    python make_art.py avatar.png

Gera dois arquivos que o generate.py consome:

    ascii_art.txt    os caracteres
    ascii_tone.txt   um "tom" por caractere, mesma grade

Tons: 0-9 e a-f = escala de luminancia (0 = mais escuro, f = mais claro)
      G = verde   (olhos / acentos verdes)
      T = ciano   (marcas azuladas)
      espaco = fundo, nao desenha nada

Os dois arquivos sao texto puro: da para ajustar um caractere ou um tom na mao
depois, sem rodar o script de novo.
"""

import sys
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

COLS = 56            # largura da arte em caracteres
ASPECT = 0.54        # proporcao do caractere (altura/largura efetiva)
BG_IS_WHITE = True   # fundo da imagem e claro? (avatar em fundo branco)
TONE_GAMMA = 0.80    # <1 clareia os meios-tons (rosto salta mais), >1 escurece
CROP = (65, 65, 325, 295)   # None = imagem inteira, ou (x0, y0, x1, y1)

LEVELS = "0123456789abcdef"


def flood_background(mask):
    """Marca o que e fundo: pixels da cor do fundo conectados as bordas."""
    h, w = mask.shape
    seen = np.zeros_like(mask)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if mask[y, x] and not seen[y, x]:
                seen[y, x] = True
                dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if mask[y, x] and not seen[y, x]:
                seen[y, x] = True
                dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                dq.append((ny, nx))
    return seen


def classify(rgb, lum):
    r, g, b = rgb
    mx, mn = max(r, g, b), min(r, g, b)
    sat = (mx - mn) / (mx + 1e-6)
    if 0.18 < lum < 0.88 and sat > 0.14:
        if g >= r and g >= b:
            return "G"
        if b >= r and g > r:
            return "T"
    return None


def main(path):
    src = Image.open(path).convert("RGBA")
    if CROP:
        src = src.crop(CROP)
    flat = Image.alpha_composite(
        Image.new("RGBA", src.size, (255, 255, 255, 255) if BG_IS_WHITE
                  else (0, 0, 0, 255)), src).convert("RGB")
    flat = flat.filter(ImageFilter.MedianFilter(5))     # tira ruido de compressao

    rgb = np.array(flat).astype(float)
    lum = np.array(flat.convert("L")).astype(float) / 255.0
    h, w = lum.shape

    bg_mask = (lum > 0.59) if BG_IS_WHITE else (lum < 0.41)
    outside = flood_background(bg_mask)

    rows = int(round(COLS * (h / w) * ASPECT))
    small = lambda a: np.array(
        Image.fromarray(a.astype(np.uint8)).resize((COLS, rows), Image.BOX)
    ).astype(float)

    L = small(lum * 255) / 255
    O = small(outside * 255) / 255
    C = np.stack([small(rgb[..., i]) for i in range(3)], -1)

    art, tone = [], []
    for y in range(rows):
        a, t = "", ""
        for x in range(COLS):
            out = O[y, x]
            if out > 0.55:                       # fundo
                a += " "
                t += " "
                continue
            l = float(L[y, x])
            kind = classify(C[y, x], l)

            if out > 0.25:                       # borda: suaviza o recorte
                ch = "+" if l < 0.5 else ":"
            elif l > 0.55:
                ch = "@"
            elif l > 0.28:
                ch = "#"
            else:
                ch = "%"

            if kind:
                ch, lev = "@", kind
            else:
                lev = LEVELS[max(0, min(15, int(round((l ** TONE_GAMMA) * 15))))]
            a += ch
            t += lev
        art.append(a.rstrip())
        tone.append(t[:len(a.rstrip())])

    open("ascii_art.txt", "w", encoding="utf-8").write("\n".join(art) + "\n")
    open("ascii_tone.txt", "w", encoding="utf-8").write("\n".join(tone) + "\n")
    print("ascii_art.txt / ascii_tone.txt  ->  %d colunas x %d linhas" % (COLS, rows))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "avatar.png")
