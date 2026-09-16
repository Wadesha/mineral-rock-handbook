# -*- coding: utf-8 -*-
"""矿物与岩石实物手册 —— 多页静态站生成器（地点导向、单一内容、浅色版）。

用法：python build_site.py    输出到 ./docs

结构：只有一种内容，就是地点。根目录是地点目录，不做总览页，也不做按矿种的反查页；
每个地点一页，页内依次写位置与到达、地质背景、能看到的矿石与岩石、成因与共生、
现场怎么认、现在去看、资料来源。
零 JavaScript，纯 CSS，单一浅色主题；不使用图片、表格、列表、卡片与搜索控件；
正文为连续散文，矿物名用粗体起段，标题一律陈述式。
"""
import os, re, html
from d_p1 import P1
from d_p2 import P2
from d_p3 import P3
from d_p4 import P4
from d_p5 import P5
from d_p6 import P6
from d_p7 import P7
from d_p8 import P8
from d_p9 import P9
from d_p10 import P10
from d_p11 import P11
from d_p12 import P12
from d_p13 import P13
from d_p14 import P14







ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'docs')
E = html.escape

PLACES = P1 + P2 + P3 + P4 + P5 + P6 + P7 + P8 + P9 + P10 + P11 + P12 + P13 + P14

SITE = '矿物与岩石实物手册'
SITE_EN = 'Places you can actually go'
NAV = [('', '地点')]


def css():
    return """
*{box-sizing:border-box}
:root{
  --bg:#fbfaf7;--ink:#23201c;--muted:#6d6659;--line:#e2dcd0;--rule:#cfc7b8;
  --accent:#2f5d8c;--warm:#8c4a2f;
}
html{color-scheme:light}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Songti SC","Source Han Serif SC","Noto Serif CJK SC",Georgia,"SimSun",serif;
  font-size:15.5px;line-height:1.82;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none;border-bottom:1px solid var(--rule)}
a:hover{color:var(--accent);border-color:var(--accent)}
nav{border-bottom:1px solid var(--line);padding:7px 0 8px;background:var(--bg)}
nav .in{max-width:960px;margin:0 auto;padding:0 16px;display:flex;flex-wrap:wrap;gap:14px;align-items:baseline}
nav .brand{font-weight:700;border:0;letter-spacing:.02em}
nav a.on{color:var(--accent);border-color:var(--accent)}
nav .sp{flex:1}
nav .en{font-size:11.5px;color:var(--muted);font-family:Georgia,"Times New Roman",serif;font-style:italic}
main{max-width:760px;margin:0 auto;padding:18px 16px 54px}
h1{font-size:22px;line-height:1.4;margin:.15em 0 .4em;letter-spacing:.01em}
h2{font-size:16px;line-height:1.5;margin:1.3em 0 .36em;padding-bottom:.2em;border-bottom:1px solid var(--line)}
p{margin:0 0 .55em;text-indent:2em;text-align:justify}
p.flat{text-indent:0}
p.ore{text-indent:0;margin-bottom:.6em}
p.ref{text-indent:0;font-size:13px;color:var(--muted);line-height:1.7;word-break:break-word}
p.ref a{border-bottom-style:dotted}
span.en{font-size:.72em;color:var(--muted);font-family:Georgia,"Times New Roman",serif;font-weight:400;
  margin-left:.5em;margin-right:.4em;letter-spacing:.01em}
b.ore{color:var(--accent)}
footer{border-top:1px solid var(--line);margin-top:28px;padding:12px 0 26px;color:var(--muted);font-size:12.5px}
footer .in{max-width:760px;margin:0 auto;padding:0 16px}
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
<meta name="color-scheme" content="light">
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


def merge(items, low=105):
    """把同一节里过短的相邻段落并成一段，保证最短段落在一百字上下。"""
    out = []
    buf = ''
    for t in items:
        buf = (buf + t) if buf else t
        if len(buf) >= low:
            out.append(buf)
            buf = ''
    if buf:
        if out:
            out[-1] = out[-1] + buf
        else:
            out.append(buf)
    return out


def place_page(p):
    body = [f'<h1>{E(p["name"])} <span class="en">{E(p["en"])}</span></h1>']
    body.append('<h2>位置与到达</h2>')
    body.append(f'<p>{E(p["where"])}</p>')
    body.append('<h2>这一带的地质背景</h2>')
    body.append(f'<p>{E(p["bg"])}</p>')
    body.append('<h2>这里能看到的矿石与岩石</h2>')
    for name, text in p['ores']:
        body.append(f'<p class="ore"><b class="ore">{E(name)}</b>　{E(text)}</p>')
    body.append('<h2>成因与共生</h2>')
    for t in merge(p['why']):
        body.append(f'<p>{E(t)}</p>')
    body.append('<h2>现场辨认</h2>')
    for t in merge(p['how']):
        body.append(f'<p>{E(t)}</p>')
    body.append('<h2>现在去看</h2>')
    for t in merge(p['now']):
        body.append(f'<p>{E(t)}</p>')
    body.append('<h2>资料来源</h2>')
    body.append(f'<p class="ref">{srcs_html(p["src"])}</p>')
    return page(f'{p["name"]} · {SITE}', '../', '', '\n'.join(body), p["where"][:60])


def sents(s, n=2):
    parts = [x for x in re.split(r'(?<=。)', s.strip()) if x]
    return ''.join(parts[:n])


def home():
    body = ['<h1>能去看的地点 <span class="en">Places you can actually go</span></h1>',
            '<p>下面按地点排，一处一段。每一段先交代它在哪里、怎么到，再点出这里能看到哪些矿石与岩石，'
            '最后说一句这些东西为什么会聚在一起。想细看某一处，点地名进详情页，那里会逐条写清产出状态、'
            '共生组合、肉眼可辨的鉴定特征，以及现在的开放与保护规定。</p>']
    for p in PLACES:
        names = '、'.join(n for n, _ in p['ores'])
        body.append(
            f'<p><a href="didian/{p["slug"]}.html">{E(p["name"])}</a>'
            f' <span class="en">{E(p["en"])}</span>'
            f'{E(sents(p["where"], 2))}这一带的底子是{E(sents(p["bg"], 1))}'
            f'在这里能看到{E(names)}。{E(sents(p["why"][0], 1))}</p>')
    return page(SITE, '', '', '\n'.join(body), '能走到跟前去看的矿物与岩石，一处一页。')


def main():
    pages = {'index.html': home()}
    for p in PLACES:
        pages[f'didian/{p["slug"]}.html'] = place_page(p)

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
    print('pages: %d  places: %d  sources: %d  removed: %d'
          % (len(pages), len(PLACES), sum(len(p['src']) for p in PLACES), len(stale)))


if __name__ == '__main__':
    main()
