# -*- coding: utf-8 -*-
"""矿物与岩石实物手册 —— 多页静态站生成器（地点导向版）。

用法：python build_site.py    输出到 ./docs

结构：根目录是地点目录（不做总览页），每个地点一页；另有一页「按矿种找地点」的反向索引。
零 JavaScript，纯 CSS 跟随系统明暗；不使用图片、表格、列表、卡片与搜索控件；
正文为连续散文，矿物名用粗体起段，标题一律陈述式。
"""
import os, re, html
from d_places_a import PLACES_A
from d_places_b import PLACES_B

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'docs')
E = html.escape
PLACES = PLACES_A + PLACES_B

SITE = '矿物与岩石实物手册'
SITE_EN = 'Where to go, and what you can actually see there'
NAV = [('', '地点'), ('kuangzhong/', '按矿种找地点')]


def css():
    return """
*{box-sizing:border-box}
:root{
  --bg:#fbfaf7;--ink:#23201c;--muted:#6d6659;--line:#e2dcd0;--rule:#cfc7b8;
  --accent:#2f5d8c;--warm:#8c4a2f;
}
@media (prefers-color-scheme:dark){
  :root{--bg:#16171a;--ink:#e6e3dc;--muted:#9d968b;--line:#2b2f34;--rule:#3a3f45;
        --accent:#8ab4dc;--warm:#d09a7c}
}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Songti SC","Source Han Serif SC","Noto Serif CJK SC",Georgia,"SimSun",serif;
  font-size:15.5px;line-height:1.85;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none;border-bottom:1px solid var(--rule)}
a:hover{color:var(--accent);border-color:var(--accent)}
nav{border-bottom:1px solid var(--line);padding:7px 0 8px;background:var(--bg)}
nav .in{max-width:960px;margin:0 auto;padding:0 16px;display:flex;flex-wrap:wrap;gap:14px;align-items:baseline}
nav .brand{font-weight:700;border:0;letter-spacing:.02em}
nav a.on{color:var(--accent);border-color:var(--accent)}
nav .sp{flex:1}
nav .en{font-size:11.5px;color:var(--muted);font-family:Georgia,"Times New Roman",serif;font-style:italic}
main{max-width:740px;margin:0 auto;padding:18px 16px 54px}
h1{font-size:22px;line-height:1.4;margin:.15em 0 .4em;letter-spacing:.01em}
h2{font-size:16px;line-height:1.5;margin:1.35em 0 .38em;padding-bottom:.2em;border-bottom:1px solid var(--line)}
p{margin:0 0 .55em;text-indent:2em;text-align:justify}
p.flat{text-indent:0}
p.ore{text-indent:0;margin-bottom:.6em}
p.ref{text-indent:0;font-size:13px;color:var(--muted);line-height:1.7;word-break:break-word}
p.ref a{border-bottom-style:dotted}
span.en{font-size:.72em;color:var(--muted);font-family:Georgia,"Times New Roman",serif;font-weight:400;
  margin-left:.5em;margin-right:.4em;letter-spacing:.01em}
b.ore{color:var(--accent)}
footer{border-top:1px solid var(--line);margin-top:28px;padding:12px 0 26px;color:var(--muted);font-size:12.5px}
footer .in{max-width:740px;margin:0 auto;padding:0 16px}
footer p{text-indent:0;line-height:1.75}
"""


def nav(prefix, cur):
    items = ''
    for href, label in NAV:
        cls = ' class="on"' if href == cur else ''
        items += f'<a href="{prefix}{href}"{cls}>{E(label)}</a>'
    return (f'<nav><div class="in"><a class="brand" href="{prefix}">{E(SITE)}</a>'
            f'<span class="sp"></span>{items}</div>'
            f'<div class="in"><span class="en">{E(SITE_EN)}</span></div></nav>')


FOOT = ('这里写的是能走到跟前去看的东西，以及它们为什么长成这样。每一处的位置、矿种、共生关系与开放状态，'
        '都对照了公开资料并注明来源。实地情况会随季节、开放安排与保护规定变化，出发前请再确认一次当下的情形；'
        '文中标出的地点是观察对象所在的大致范围，不代表那里可以随意采集标本，也不代表进入不受限制。')


def page(title, prefix, cur, body, desc=''):
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc or SITE)}">
<style>{css()}</style></head><body>
{nav(prefix, cur)}
<main>
{body}
</main>
<footer><div class="in"><p>{E(FOOT)}</p></div></footer>
</body></html>"""


def srcs_html(srcs):
    return '；'.join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>' for t, u in srcs)


def place_page(p, is_rock):
    body = [f'<h1>{E(p["name"])} <span class="en">{E(p["en"])}</span></h1>',
            f'<p>{E(p["place"])}{E(p["open"])}</p>']
    body.append('<h2>这里能看到的岩石与矿物</h2>' if is_rock else '<h2>这里能看到的矿石</h2>')
    for name, text in p['ores']:
        body.append(f'<p class="ore"><b class="ore">{E(name)}</b>　{E(text)}</p>')
    body.append('<h2>成因与共生</h2>')
    for t in p['why']:
        body.append(f'<p>{E(t)}</p>')
    body.append('<h2>现在去看</h2>')
    for t in p['now']:
        body.append(f'<p>{E(t)}</p>')
    body.append('<h2>资料来源</h2>')
    body.append(f'<p class="ref">{srcs_html(p["src"])}</p>')
    return page(f'{p["name"]} · {SITE}', '../', '', '\n'.join(body), p['place'][:60])


def split_names(s):
    """把「石英（水晶）」「磁铁矿与赤铁矿」「石榴子石、透辉石」拆成主矿物名列表。"""
    s = re.sub(r'（[^）]*）', '', s)
    out = []
    for part in s.split('、'):
        part = part.strip()
        if not part:
            continue
        if '与' in part and 3 <= len(part) <= 12:
            a, b = part.split('与', 1)
            if a.strip() and b.strip():
                out += [a.strip(), b.strip()]
                continue
        out.append(part)
    return out


def build_mineral_index():
    idx = {}
    for p in PLACES:
        for name, text in p['ores']:
            for m in split_names(name):
                if len(m) < 2:
                    continue
                sents = [x for x in re.split(r'(?<=。)', text.strip()) if x]
                brief = ''.join(sents[:2]).rstrip('。')
                if len(brief) < 90:
                    brief = text.strip().rstrip('。')
                idx.setdefault(m, []).append((p['slug'], p['name'], brief))
    return idx


def mineral_page():
    idx = build_mineral_index()
    items = sorted(idx.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    body = ['<h1>按矿种找地点 <span class="en">Which minerals, and where</span></h1>',
            '<p class="flat">这一页把各处的矿种倒过来排一遍：先是一个矿种名，后面是能看见它的地点，'
            '以及它在这个地点以什么状态出现。同一矿种在不同地点往往长得不一样，因为产出方式不同——'
            '原生矿、砂矿、氧化带次生矿、博物馆标本、市场商品，看头完全不同。想顺着某一种矿物追下去，'
            '从这一页进去最快。</p>']
    for m, lst in items:
        seg = []
        for slug, pname, first in lst:
            seg.append(f'<a href="../didian/{slug}.html">{E(pname)}</a>：{E(first)}')
        body.append(f'<p class="ore"><b class="ore">{E(m)}</b>　' + '；'.join(seg) + '</p>')
    return page(f'按矿种找地点 · {SITE}', '../', 'kuangzhong/', '\n'.join(body),
                '按矿种反查能看到它的地点。')


def home():
    body = ['<h1>能去看的地点 <span class="en">Places you can actually go</span></h1>']
    for title, group, is_rock in [('矿床与产地', PLACES_A, False), ('岩石露头', PLACES_B, True)]:
        body.append(f'<h2>{title}</h2>')
        for p in group:
            first = re.split(r'(?<=。)', p['ores'][0][1].strip())[0]
            names = '、'.join(n for n, _ in p['ores'])
            body.append(
                f'<p><a href="didian/{p["slug"]}.html">{E(p["name"])}</a>'
                f' <span class="en">{E(p["en"].split("—")[0].strip())}</span>'
                f'{E(p["place"])}这里能看到{E(names)}。{E(first)}</p>')
    return page(SITE, '', '', '\n'.join(body), '能走到跟前去看的矿物与岩石，一处一页。')


def main():
    pages = {'index.html': home()}
    for p in PLACES_A:
        pages[f'didian/{p["slug"]}.html'] = place_page(p, False)
    for p in PLACES_B:
        pages[f'didian/{p["slug"]}.html'] = place_page(p, True)
    pages['kuangzhong/index.html'] = mineral_page()

    stale = []
    for dp, dn, fn in os.walk(OUT):
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), OUT).replace('\\', '/')
            if rel not in pages and rel != '.nojekyll':
                stale.append(os.path.join(dp, f))
    for fp in stale:
        try:
            os.remove(fp)
        except OSError:
            pass

    for rel, s in pages.items():
        fp = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, 'w', encoding='utf-8') as fh:
            fh.write(s)
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    print('pages: %d  places: %d (产地 %d / 露头 %d)  sources: %d  removed: %d'
          % (len(pages), len(PLACES), len(PLACES_A), len(PLACES_B),
             sum(len(p['src']) for p in PLACES), len(stale)))


if __name__ == '__main__':
    main()
