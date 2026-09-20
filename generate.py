# -*- coding: utf-8 -*-
"""
Gera dark_mode.svg e light_mode.svg com estatisticas reais do GitHub.

Uso local:
    export ACCESS_TOKEN=ghp_xxx
    python generate.py

Sem token (preview offline, numeros falsos):
    python generate.py --offline
"""

import os
import sys
import json
import time
import html
import datetime

import config as C

OFFLINE = "--offline" in sys.argv
TOKEN = os.environ.get("ACCESS_TOKEN", "")
CACHE_FILE = ".cache/loc.json"
API = "https://api.github.com"

if not OFFLINE:
    import requests
    SESSION = requests.Session()
    SESSION.headers.update({
        "Authorization": "bearer " + TOKEN,
        "Accept": "application/vnd.github+json",
        "User-Agent": C.USER + "-profile-card",
    })


# ----------------------------------------------------------------- helpers ---
def graphql(query, variables):
    for attempt in range(6):
        r = SESSION.post(API + "/graphql",
                         json={"query": query, "variables": variables},
                         timeout=30)
        if r.status_code == 200:
            data = r.json()
            if "errors" in data:
                raise RuntimeError(json.dumps(data["errors"])[:500])
            return data["data"]
        if r.status_code in (403, 429, 502, 503):
            time.sleep(2 ** attempt)
            continue
        raise RuntimeError("GraphQL %s: %s" % (r.status_code, r.text[:300]))
    raise RuntimeError("GraphQL: esgotadas as tentativas")


def uptime(birth, today=None):
    today = today or datetime.date.today()
    y = today.year - birth.year
    m = today.month - birth.month
    d = today.day - birth.day
    if d < 0:
        m -= 1
        prev = today.replace(day=1) - datetime.timedelta(days=1)
        d += prev.day
    if m < 0:
        m += 12
        y -= 1
    plural = lambda n: "" if n == 1 else "s"
    return "%d year%s, %d month%s, %d day%s" % (y, plural(y), m, plural(m), d, plural(d))


# ------------------------------------------------------------------- stats ---
REPO_QUERY = """
query($login:String!, $after:String) {
  user(login:$login) {
    createdAt
    followers { totalCount }
    following { totalCount }
    repositories(first:100, after:$after, ownerAffiliations:OWNER,
                 orderBy:{field:PUSHED_AT, direction:DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes { nameWithOwner stargazerCount isFork pushedAt defaultBranchRef { name } }
    }
    repositoriesContributedTo(first:100,
        contributionTypes:[COMMIT, PULL_REQUEST, REPOSITORY],
        includeUserRepositories:false) {
      totalCount
      nodes { nameWithOwner pushedAt }
    }
  }
}
"""

COMMIT_QUERY = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    contributionsCollection(from:$from, to:$to) {
      totalCommitContributions
      restrictedContributionsCount
    }
  }
}
"""


def fetch_stats():
    repos, contributed = [], []
    after, meta = None, None
    while True:
        data = graphql(REPO_QUERY, {"login": C.USER, "after": after})["user"]
        if meta is None:
            meta = data
            contributed = data["repositoriesContributedTo"]["nodes"]
        page = data["repositories"]
        repos.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]

    created = datetime.datetime.fromisoformat(meta["createdAt"].replace("Z", "+00:00"))
    now = datetime.datetime.now(datetime.timezone.utc)

    commits = 0
    year = created.year
    while year <= now.year:
        start = max(created, datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc))
        end = min(now, datetime.datetime(year, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc))
        cc = graphql(COMMIT_QUERY, {
            "login": C.USER,
            "from": start.isoformat().replace("+00:00", "Z"),
            "to": end.isoformat().replace("+00:00", "Z"),
        })["user"]["contributionsCollection"]
        commits += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
        year += 1

    add, rem = count_loc(repos, contributed)

    return {
        "repos": meta["repositories"]["totalCount"],
        "contrib": meta["repositoriesContributedTo"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "followers": meta["followers"]["totalCount"],
        "following": meta["following"]["totalCount"],
        "commits": commits,
        "loc_add": add,
        "loc_del": rem,
        "loc": add - rem,
    }


def count_loc(repos, contributed):
    """Soma additions/deletions do usuario via REST, com cache por pushedAt."""
    try:
        cache = json.load(open(CACHE_FILE, encoding="utf-8"))
    except (IOError, ValueError):
        cache = {}

    targets = []
    for r in repos:
        if r["isFork"] and not C.LOC_COUNT_FORKS:
            continue
        if r["nameWithOwner"] in C.LOC_IGNORE_REPOS:
            continue
        targets.append((r["nameWithOwner"], r["pushedAt"]))
    for r in contributed:
        if r["nameWithOwner"] not in C.LOC_IGNORE_REPOS:
            targets.append((r["nameWithOwner"], r["pushedAt"]))

    total_add = total_del = 0
    for name, pushed in targets:
        hit = cache.get(name)
        if hit and hit.get("pushedAt") == pushed:
            total_add += hit["add"]
            total_del += hit["del"]
            continue

        add = rem = 0
        stats = None
        for attempt in range(5):
            r = SESSION.get("%s/repos/%s/stats/contributors" % (API, name), timeout=60)
            if r.status_code == 200:
                stats = r.json()
                break
            if r.status_code == 202:          # GitHub ainda esta calculando
                time.sleep(3 + attempt * 3)
                continue
            break                              # 404 / 403 / repo vazio -> ignora
        if isinstance(stats, list):
            for c in stats:
                if (c.get("author") or {}).get("login", "").lower() != C.USER.lower():
                    continue
                for w in c.get("weeks", []):
                    add += w.get("a", 0)
                    rem += w.get("d", 0)

        cache[name] = {"pushedAt": pushed, "add": add, "del": rem}
        total_add += add
        total_del += rem

    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    json.dump(cache, open(CACHE_FILE, "w", encoding="utf-8"), indent=1, sort_keys=True)
    return total_add, total_del


FAKE = dict(repos=25, contrib=12, stars=7, followers=18, following=14,
            commits=2116, loc_add=523178, loc_del=76902, loc=446276)


# ------------------------------------------------------------------ layout ---
E = lambda s: html.escape(s, quote=False)


def fmt(text, data):
    return text.format(**data)


def leader(label, value, width):
    dots = max(1, width - len(label) - len(value) - 2)
    return label, " " + "." * dots + " ", value


def build_lines(data):
    """Devolve [(kind, payload)] ja com os numeros resolvidos."""
    w = C.INFO_WIDTH
    out = [("head", (C.NICK, "-" * max(1, w - len(C.NICK) - 1))), ("gap", None)]

    for row in C.ROWS:
        kind = row[0]
        if kind == "gap":
            out.append(("gap", None))
        elif kind == "kv":
            out.append(("kv", leader(row[1], fmt(row[2], data), w)))
        elif kind == "rule":
            head = "- %s " % row[1]
            out.append(("rule", (head, "-" * max(1, w - len(head)))))
        elif kind == "stat2":
            half = (w - 3) // 2
            a = leader(row[1][0], fmt(row[1][1], data), half)
            b = leader(row[2][0], fmt(row[2][1], data), half)
            out.append(("stat2", (a, b)))
        elif kind == "loc":
            value = "{loc:,} ( {loc_add:,}++, {loc_del:,}-- )".format(**data)
            out.append(("loc", leader(row[1], value, w)))
    return out


def measure(lines):
    """Maior largura real em caracteres, para o SVG nunca cortar texto."""
    best = C.INFO_WIDTH
    for kind, p in lines:
        if kind == "gap":
            continue
        if kind in ("head", "rule"):
            best = max(best, len(p[0]) + len(p[1]))
        elif kind in ("kv", "loc"):
            best = max(best, len(p[0]) + len(p[1]) + len(p[2]))
        elif kind == "stat2":
            best = max(best, sum(len(x) for x in p[0]) + 3 + sum(len(x) for x in p[1]))
    return best


def tone_color(level, T):
    """'0'..'f' -> cor interpolada; 'G'/'T' -> acentos."""
    if level == "G":
        return T.get("art_green", T["art"])
    if level == "T":
        return T.get("art_teal", T["art"])
    try:
        v = int(level, 16) / 15.0
    except ValueError:
        return T["art"]
    lo = T.get("art_low")
    hi = T.get("art_high")
    if not lo or not hi:
        return T["art"]
    a = [int(lo[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(hi[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * v) for i in range(3))


def art_line_svg(chars, tones, T):
    """Agrupa caracteres vizinhos de mesma cor num unico tspan."""
    if tones is None:
        return E(chars)
    parts, run, cur = [], "", None
    for i, c in enumerate(chars):
        lev = tones[i] if i < len(tones) else " "
        col = None if c == " " else tone_color(lev, T)
        if col != cur and run:
            parts.append((cur, run))
            run = ""
        cur, run = col, run + c
    if run:
        parts.append((cur, run))
    out = []
    for col, txt in parts:
        if col is None:
            out.append(E(txt))
        else:
            out.append('<tspan fill="%s">%s</tspan>' % (col, E(txt)))
    return "".join(out)


def render(theme, art, tone, lines, info_cols):
    T = C.THEMES[theme]
    fs, lh = C.FONT_SIZE, C.LINE_HEIGHT
    ch = fs * 0.6
    chrome = getattr(C, "TERMINAL_CHROME", False)
    cursor = getattr(C, "SHOW_CURSOR", False)

    info_x = C.PAD_LEFT + C.GUTTER_COLS * ch
    width = round(info_x + info_cols * fs * 0.625 + 18)

    bar_h = 34.0 if chrome else 0.0
    top = bar_h + C.PAD_TOP
    prompt_rows = 2 if chrome else 0            # linha do prompt + linha em branco
    body_top = top + prompt_rows * lh
    body_rows = max(len(art), len(lines))
    tail = (2 * lh) if cursor else 0.0
    height = round(body_top + body_rows * lh + tail + 20)

    s = []
    s.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
             'viewBox="0 0 %d %d" font-size="%g" font-family="%s" role="img" '
             'aria-label="%s neofetch profile card">'
             % (width, height, width, height, fs, C.FONT_STACK, E(C.USER)))

    anim = ('@keyframes fadeIn{from{opacity:0;transform:translateX(-6px)}'
            'to{opacity:1;transform:translateX(0)}}'
            '.f{animation:fadeIn .45s ease-out both}'
            '@media(prefers-reduced-motion:reduce){.f{animation:none}}'
            ) if C.ANIMATE else ''
    blink = ('@keyframes blink{0%,45%{opacity:1}50%,95%{opacity:0}100%{opacity:1}}'
             '.cur{animation:blink 1.15s step-end infinite}'
             '@media(prefers-reduced-motion:reduce){.cur{animation:none}}'
             ) if cursor else ''
    s.append('<style>text{white-space:pre;dominant-baseline:middle}%s%s'
             '.art{fill:%s}.lbl{fill:%s}.val{fill:%s}.dot{fill:%s}.dash{fill:%s}'
             '.sec{fill:%s}.nick{fill:%s;font-weight:bold}.num{fill:%s}'
             '.sep{fill:%s}.add{fill:%s}.rem{fill:%s}</style>'
             % (anim, blink, T["art"], T["label"], T["value"], T["dots"], T["dash"],
                T["sec"], T["header"], T["num"], T["dash"], T["add"], T["rem"]))

    s.append('<rect x="0" y="0" width="%d" height="%d" rx="14" fill="%s" '
             'stroke="%s" stroke-width="1"/>' % (width, height, T["bg"], T["border"]))

    # ---- barra de titulo
    if chrome:
        s.append('<path d="M0 14a14 14 0 0 1 14-14h%.0fa14 14 0 0 1 14 14v%.0fH0Z" '
                 'fill="%s"/>' % (width - 28, bar_h - 14, T.get("chrome_bg", T["bg"])))
        s.append('<line x1="0" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                 'stroke-width="1"/>' % (bar_h, width, bar_h, T.get("chrome_line", T["border"])))
        for i, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
            s.append('<circle cx="%.1f" cy="%.1f" r="5.5" fill="%s"/>'
                     % (22 + i * 19, bar_h / 2, col))
        s.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="%g" '
                 'fill="%s">%s</text>'
                 % (width / 2, bar_h / 2, fs - 1.5,
                    T.get("chrome_title", T["sec"]), E(C.WINDOW_TITLE)))

    def text(x, y, delay, body, extra=""):
        cls = ' class="f"' if C.ANIMATE else ''
        style = ' style="animation-delay:%.2fs"' % delay if C.ANIMATE else ''
        return '<text%s x="%g" y="%g"%s%s>%s</text>' % (cls, x, y, style, extra, body)

    # ---- linha de prompt
    if chrome:
        s.append(text(C.PAD_LEFT, top, 0.05,
                      '<tspan class="nick">%s</tspan>'
                      '<tspan fill="%s">%s </tspan>'
                      '<tspan fill="%s">%s</tspan>'
                      % (E(C.PROMPT_USER), T.get("prompt_sign", T["dash"]),
                         E(C.PROMPT_SIGN), T.get("prompt_cmd", T["value"]),
                         E(C.PROMPT_CMD))))

    # ---- arte
    s.append('<g class="art">')
    for i, line in enumerate(art):
        body = art_line_svg(line, tone[i] if tone else None, T)
        s.append(text(C.PAD_LEFT, body_top + i * lh, 0.18 + i * 0.022, body))
    s.append('</g>')

    # ---- bloco neofetch
    for i, (kind, p) in enumerate(lines):
        if kind == "gap":
            continue
        y, d = body_top + i * lh, 0.50 + i * 0.045
        if kind == "head":
            body = ('<tspan class="nick">%s</tspan><tspan class="dash"> %s</tspan>'
                    % (E(p[0]), p[1]))
        elif kind == "rule":
            body = ('<tspan class="sec">%s</tspan><tspan class="dash">%s</tspan>'
                    % (E(p[0]), p[1]))
        elif kind == "kv":
            body = ('<tspan class="lbl">%s</tspan><tspan class="dot">%s</tspan>'
                    '<tspan class="val">%s</tspan>' % (E(p[0]), p[1], E(p[2])))
        elif kind == "stat2":
            (l1, d1, v1), (l2, d2, v2) = p
            body = ('<tspan class="lbl">%s</tspan><tspan class="dot">%s</tspan>'
                    '<tspan class="num">%s</tspan><tspan class="sep"> | </tspan>'
                    '<tspan class="lbl">%s</tspan><tspan class="dot">%s</tspan>'
                    '<tspan class="num">%s</tspan>'
                    % (E(l1), d1, E(v1), E(l2), d2, E(v2)))
        elif kind == "loc":
            label, dots, value = p
            total, rest = value.split(" ( ", 1)
            adds, dels = rest.rstrip(" )").split(", ")
            body = ('<tspan class="lbl">%s</tspan><tspan class="dot">%s</tspan>'
                    '<tspan class="num">%s</tspan><tspan class="sep"> ( </tspan>'
                    '<tspan class="add">%s</tspan><tspan class="sep">, </tspan>'
                    '<tspan class="rem">%s</tspan><tspan class="sep"> )</tspan>'
                    % (E(label), dots, E(total), E(adds), E(dels)))
        s.append(text(info_x, y, d, body))

    # ---- cursor piscando
    if cursor:
        y = body_top + body_rows * lh + lh * 0.6
        s.append(text(C.PAD_LEFT, y, 0.9,
                      '<tspan class="nick">%s</tspan><tspan fill="%s">%s</tspan>'
                      % (E(C.PROMPT_USER), T.get("prompt_sign", T["dash"]),
                         E(C.PROMPT_SIGN))))
        cx = C.PAD_LEFT + (len(C.PROMPT_USER) + len(C.PROMPT_SIGN) + 1) * ch
        s.append('<rect class="cur" x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="%s"/>' % (cx, y - fs * 0.55, ch * 0.95, fs * 1.05,
                                   T.get("cursor", T["value"])))

    s.append('</svg>')
    return "\n".join(s)


# -------------------------------------------------------------------- main ---
def read_art():
    art = open(C.ASCII_FILE, encoding="utf-8").read().split("\n")
    while art and not art[-1].strip():
        art.pop()
    tone = None
    tone_file = getattr(C, "TONE_FILE", None)
    if tone_file and os.path.exists(tone_file):
        tone = open(tone_file, encoding="utf-8").read().split("\n")
        tone = (tone + [""] * len(art))[:len(art)]
        tone = [(t + " " * len(a))[:len(a)] for t, a in zip(tone, art)]
    return art, tone


def main():
    art, tone = read_art()

    if OFFLINE or not TOKEN:
        if not OFFLINE:
            raise SystemExit("ACCESS_TOKEN nao definido. Use --offline para preview.")
        data = dict(FAKE)
    else:
        data = fetch_stats()

    data["uptime"] = uptime(C.BIRTHDAY)
    data = {k: ("{:,}".format(v) if isinstance(v, int) else v) for k, v in data.items()}
    # o loc precisa dos ints para o formato com virgula na linha especial
    ints = {k: int(v.replace(",", "")) for k, v in data.items() if k.startswith("loc")}
    data.update(ints)

    lines = build_lines(data)
    cols = measure(lines)
    for theme, path in C.OUTPUT.items():
        svg = render(theme, art, tone, lines, cols)
        open(path, "w", encoding="utf-8").write(svg)
        print("%-16s %5d bytes" % (path, len(svg)))


if __name__ == "__main__":
    main()
