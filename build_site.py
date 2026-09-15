# -*- coding: utf-8 -*-
"""矿物与岩石实物手册 —— 多页静态站点生成器。
用法：python build_site.py    输出到 ./docs

设计：零 JavaScript，纯 CSS 自动明暗（跟随系统）；不使用图片、表格、列表、卡片与搜索控件；
正文为连续散文，标题为陈述式名词短语；粗体与强调色用于阅读引导。
"""
import os, html, shutil
from d_kuangwu import KUANGWU
from d_yanshi import YANSHI
from d_pages import (YUANLI, YUANLI_LEAD, DUIBI, DUIBI_LEAD,
                     LAILI, LAILI_LEAD, LAILI_TAIL)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'docs')
E = html.escape
CASES = KUANGWU + YANSHI

SITE = '矿物与岩石实物手册'
SITE_EN = 'A field guide to minerals and rocks you can actually handle'
NAV = [('', '总览'), ('kuangwu/', '矿物实物'), ('yanshi/', '岩石实物'),
       ('yuanli/', '原理'), ('duibi/', '易混对照'), ('laili/', '来历与变化')]


def css():
    return """
*{box-sizing:border-box}
:root{
  --bg:#fbfaf7;--panel:#f4f1ea;--ink:#23201c;--muted:#6d6659;--line:#e2dcd0;--rule:#cfc7b8;
  --accent:#2f5d8c;--soft:#e8eff5;--warm:#8c4a2f;--warmsoft:#f6ece6;
}
@media (prefers-color-scheme:dark){
  :root{--bg:#16171a;--panel:#1e2024;--ink:#e6e3dc;--muted:#9d968b;--line:#2b2f34;--rule:#3a3f45;
        --accent:#8ab4dc;--soft:#22303c;--warm:#d09a7c;--warmsoft:#2e2621}
}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Songti SC","Source Han Serif SC","Noto Serif CJK SC",Georgia,"SimSun",serif;
  font-size:16px;line-height:1.95;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none;border-bottom:1px solid var(--rule)}
a:hover{color:var(--accent);border-color:var(--accent)}
nav{border-bottom:1px solid var(--line);padding:8px 0 9px;background:var(--bg)}
nav .in{max-width:1000px;margin:0 auto;padding:0 18px;display:flex;flex-wrap:wrap;gap:14px;align-items:baseline}
nav .brand{font-weight:700;border:0;letter-spacing:.02em}
nav a.on{color:var(--accent);border-color:var(--accent)}
nav .sp{flex:1}
nav .en{font-size:12px;color:var(--muted);font-family:Georgia,"Times New Roman",serif;font-style:italic}
main{max-width:820px;margin:0 auto;padding:22px 18px 60px}
h1{font-size:24px;line-height:1.4;margin:.2em 0 .35em;letter-spacing:.01em}
h2{font-size:17.5px;line-height:1.5;margin:1.5em 0 .4em;padding-bottom:.22em;border-bottom:1px solid var(--line)}
h3{font-size:16.5px;line-height:1.5;margin:1.35em 0 .3em}
p{margin:0 0 .62em;text-indent:2em;text-align:justify}
p.flat{text-indent:0}
p.kicker{text-indent:0;font-size:13.5px;color:var(--muted);margin-bottom:.15em}
p.lead{text-indent:0;color:var(--muted);line-height:1.8}
p.ref{text-indent:0;font-size:13.5px;color:var(--muted);line-height:1.7;word-break:break-word}
p.ref a{border-bottom-style:dotted}
p.go{text-indent:0;font-size:14.5px;background:var(--panel);border-left:3px solid var(--rule);
  padding:8px 12px;line-height:1.8}
span.en{font-size:.72em;color:var(--muted);font-family:Georgia,"Times New Roman",serif;font-weight:400;
  margin-left:.5em;margin-right:.45em;letter-spacing:.01em}
b{font-weight:700}
.hl{color:var(--accent);font-weight:700}
.hw{color:var(--warm);font-weight:700}
footer{border-top:1px solid var(--line);margin-top:34px;padding:14px 0 30px;color:var(--muted);font-size:13px}
footer .in{max-width:820px;margin:0 auto;padding:0 18px}
footer p{text-indent:0;line-height:1.8}
.hlist p{margin-bottom:.75em}
"""


def nav(prefix, cur):
    items = ''
    for href, label in NAV:
        cls = ' class="on"' if href == cur else ''
        items += f'<a href="{prefix}{href}"{cls}>{E(label)}</a>'
    return (f'<nav><div class="in"><a class="brand" href="{prefix}">{E(SITE)}</a>'
            f'<span class="sp"></span>{items}</div>'
            f'<div class="in"><span class="en">{E(SITE_EN)}</span></div></nav>')


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
<footer><div class="in">
<p>本手册写的是能摸到、能看到的东西，以及它们为什么长成这样。每一页的实物描述、地点信息与来历变化，都对照了公开资料并注明来源，
实地情况会随季节、开放安排与保护规定变化，出发前请再确认一次当下的情况；进入矿区、地质公园与生产区域时，请遵守当地的管理要求。
文中标出的地点是观察对象所在的大致范围，不代表那里可以随意采集标本，也不代表进入不受限制。</p>
</div></footer>
</body></html>"""


def srcs_html(srcs):
    return '；'.join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>' for t, u in srcs)


def rel_html(origin, rel):
    """相邻实例：相对当前页所在目录计算链接，并把每一处写成完整的一段话。"""
    cur_sub = 'kuangwu' if origin['cat'] == '矿物' else 'yanshi'
    items = []
    for s in rel:
        c = next((x for x in CASES if x['slug'] == s), None)
        if not c:
            continue
        tgt_sub = 'kuangwu' if c['cat'] == '矿物' else 'yanshi'
        href = (f'{c["slug"]}.html' if tgt_sub == cur_sub
                else f'../{tgt_sub}/{c["slug"]}.html')
        lead = c['lead'].rstrip('。；')
        items.append(f'<a href="{href}">{E(c["name"])}</a>在{E(c["place"])}，{E(lead)}')
    if not items:
        return ''
    return ('可以接着看的相邻实例：' + '；'.join(items) +
            '。把这几处放在一起看，同一类性质在不同实物上的差别会更容易分辨，'
            '手里的工具也能一次用熟，不必每换一处都重新学一遍判断的动作。')


def case_page(c):
    sub = 'kuangwu' if c['cat'] == '矿物' else 'yanshi'
    # 页面自开头即进入实物：首段把原本的一行提要并进正文本体，不留独立短行。
    body = [f'<h1>{E(c["name"])} <span class="en">{E(c["en"])}</span></h1>']
    for title, key in [('手里的样子', 'look'), ('到哪里去看', 'where'),
                       ('来历与变化', 'history'), ('背后的道理', 'why')]:
        body.append(f'<h2>{title}</h2>')
        for i, p in enumerate(c[key]):
            if key == 'look' and i == 0:
                p = c['lead'] + p
            elif key == 'where' and i == 0:
                p = f'这一页的观察地点在{c["place"]}，到了当地，' + _lower_first(p)
            body.append(f'<p>{E(p)}</p>')
    body.append('<h2>资料来源</h2>')
    body.append('<p class="ref">这一页写的位置、实物描述与来历变化，都逐条对照了下列公开资料，'
                '其中以主管部门、科研机构与主流媒体的发布为准，同一件事存在不同口径的，按各自来源分别列出：'
                f'{srcs_html(c["src"])}。</p>')
    r = rel_html(c, c.get('rel', []))
    if r:
        body.append(f'<p class="go">{r}</p>')
    return page(f'{c["name"]} · {SITE}', '../', c['cat'], '\n'.join(body), c['lead'])


def _lower_first(s):
    return s[:1].lower() + s[1:] if s else s


def index_list(cases, sub):
    """索引页：每一处写成一段自成一体的话，名称以链接落在句中，不做名称加一句的短行。"""
    out = []
    for c in cases:
        en = c['en'].split('—')[0].strip()
        out.append(
            f'<p><a href="{c["slug"]}.html">{E(c["name"])}</a>'
            f' <span class="en">{E(en)}</span>在{E(c["place"])}。{E(c["lead"])}'
            f'{E(c["look"][0])}到这一页可以按手里的样子、能看到的去处、它的来历与变化、背后的道理这个顺序读下去。</p>')
    return '\n'.join(out)


def mod_index(sub, cases, h1, intro):
    body = [f'<h1>{E(h1)}</h1>', f'<p class="lead">{E(intro)}</p>', '<div class="hlist">']
    body.append(index_list(cases, sub))
    body.append('</div>')
    return page(f'{h1} · {SITE}', '../', sub + '/', '\n'.join(body))


def home():
    km, ys = len(KUANGWU), len(YANSHI)
    names = '、'.join(c['name'] for c in KUANGWU[:6]) + '、' + '、'.join(c['name'] for c in YANSHI[:4]) + '等'
    body = [
        f'<h1>{E(SITE)} <span class="en">{E(SITE_EN)}</span></h1>',
        '<p class="lead">这里写的都是能亲手摸到的东西：一块透明得像冰的六棱柱，一枚能在铁上擦出火花的蓝黑小石头，一面条带弯曲的古老岩石，一块红绿相间的深部岩石。'
        '每一页都从手里这块东西的样子讲起——颜色、光泽、软硬、裂开的方式、颗粒粗细，然后讲它在什么地方能看到，再讲它的来历与这些年的变化，最后回到它为什么长成这样。</p>',
        '<h2>这份手册的读法</h2>',
        '<p>顺序是刻意的：先看见，再追溯，最后解释。手里先有一块具体的石头，后面的原理才有落脚的地方；反过来先背原理，到了现场往往认不出任何东西。'
        '所以每一页的开头都不谈成因，只谈你拿起它时能感到、能看到的一切，包括那些容易被忽略的细节，比如解理面的平整程度、气孔被充填的样子、颗粒之间是紧密镶嵌还是松散堆积。</p>',
        f'<p>手册分两部分。矿物实物 {km} 处，都是能到现场、能上手比较的地点，从东海的水晶到宣化的赤铁矿；岩石实物 {ys} 处，从五大连池刚喷出不久的玄武岩到曾进入地下深处又被抬回地表的榴辉岩。'
        f'两部分合起来，涵盖{names}这些可以亲眼看到的东西。另有三个专题页：原理讲的是这些性质背后的成因，易混对照给出几组容易认错的组合与区分动作，来历与变化讲的是名称与用途怎么一路变过来。</p>',
        '<h2>手边要带的几样东西</h2>',
        '<p>一块没有上釉的白瓷板，用来测条痕，这是判断铁矿石与含铜矿物最省事的办法；一把小刀或一枚硬度较高的金属钥匙，用来比较硬度；'
        '一个小瓶稀盐酸或一瓶白醋，用来试碳酸盐类矿物的反应；一块磁铁，用来分辨含磁性的矿物；一个十倍左右的放大镜，用来观察颗粒、解理面与包裹体。'
        '再带上紫外灯就更完整，能看出萤石一类矿物的荧光。这些工具的价格都很低，但能把现场判断的可靠性提高很多。</p>',
        '<h2>几条实在的提醒</h2>',
        '<p>地质公园、风景名胜区与生产矿区都有各自的管理规定，采集标本通常是不允许的，露头本身也需要保护；进入废弃坑口与边坡下方存在落石与坍塌风险，独自下坑没有必要。'
        '观察与记录同样能让人看懂一块岩石：看清它与围岩的界线，写清它的构造与颗粒，量出条带的走向，这些做法比带走标本更有价值，也不会让后来的访问者无物可看。</p>',
        '<h2>起步的次序</h2>',
        '<p>如果手里已经有一块不知道是什么的石头，可以先看易混对照那一页，按给出的动作逐项排查，多数常见矿物能在几分钟内缩小到两三种可能；'
        '如果打算出行，就先看两部分实物索引，按地点挑一处距离合适的，把那一页的实物描述读一遍，到了现场再对照；如果只想弄明白为什么，直接去原理页，那里从晶体内部的排列方式讲起，一路讲到变质作用的温压条件。</p>',
        '<p>总览之外，矿物实物共十二处，都是能上手比较的地点，从江苏东海的水晶一直排到河北宣化的赤铁矿，看的是单颗矿物的颜色、光泽、硬度与裂开的方式；'
        '岩石实物共七处，看的是颗粒之间的关系与整体的结构构造，从五大连池刚喷出不久的玄武岩，到曾进入地下深处又被抬回地表的榴辉岩；'
        '原理页把硬度、解理、双折射、结晶顺序与变质条件这几条线索串起来，回答这些性质从哪儿来；'
        '易混对照页给出几组现场最容易认错的组合，每一组都配上可以在手里做的区分动作；'
        '来历与变化页则专讲名称与用途的沿革，许多今天熟悉的叫法，几十年前完全是另一回事。</p>',
    ]
    return page(SITE, '', '', '\n'.join(body), '能摸到的矿物与岩石：实物描述、可到访地点、来历变化与背后的原理。')


def yuanli_page():
    body = ['<h1>原理：性质背后的成因</h1>', f'<p class="lead">{E(YUANLI_LEAD)}</p>']
    for sec in YUANLI:
        body.append(f'<h2>{E(sec["t"])}</h2>')
        for p in sec['ps']:
            body.append(f'<p>{E(p)}</p>')
    body.append('<h2>原理在实物上的落点</h2>')
    body.append('<p>原理本身不是目的地。回到具体的东西上，它才变成能用的东西：硬度与解理决定了一块石头能不能被刻动、从哪里裂开，'
                '这是汉白玉能雕到极细而萤石一敲就碎的原因；干涉色与双折射决定了薄片在显微镜下呈现什么样子，'
                '这是方解石透光看字成双影的原因；结晶温度的顺序决定了矿物能不能长在一起，这是橄榄石与石英很少大量共生的原因；'
                '而变质条件决定了同一种原岩会变成片岩还是大理岩，这是泰山的岩石与房山的石材截然不同的原因。</p>')
    body.append('<p>想把原理与实物对照着看，可以先读 <a href="../kuangwu/donghai-shuijing.html">东海的水晶</a>，那里有最规整的柱面与最典型的解理面，'
                '再看 <a href="../kuangwu/wuyi-yingshi.html">武义的萤石</a>，同一族矿物的颜色差异在那里最集中；'
                '接着翻到 <a href="../yanshi/fangshan-hanbaiyu.html">房山的汉白玉</a>，一块石灰岩经过高温高压之后变成什么样子，'
                '在这里可以亲眼看到；最后到 <a href="../yanshi/dabieshan-liuhuiyan.html">大别山的榴辉岩</a>，'
                '红绿相间的两种矿物是怎么被挤到地下几十公里深处又重新抬回地表的，那一页讲得最清楚。'
                '四处按这个顺序走完，前面几节抄下来的名词基本都能找到对应的实物。</p>')
    return page(f'原理 · {SITE}', '../', 'yuanli/', '\n'.join(body), YUANLI_LEAD[:60])


def duibi_page():
    body = ['<h1>易混对照：几组最容易认错的组合</h1>', f'<p class="lead">{E(DUIBI_LEAD)}</p>']
    for sec in DUIBI:
        body.append(f'<h2>{E(sec["t"])}</h2>')
        body.append(f'<p>{E(sec["p"])}</p>')
    body.append('<h2>把这几组串起来用</h2>')
    body.append('<p>真正到了现场，手边常常只有一两样工具，判断的顺序就比记住多少组特征更重要。建议先做不损伤标本、也不需要试剂的观察：'
                '看整体颜色与结构，看颗粒粗细，看有无方向性的条带；然后是可以在废石上做的动作：用白瓷板划条痕，用刀试硬度，用磁铁试磁性；'
                '最后才用酸液与紫外灯这类需要额外工具的手段。按这个顺序走，多数标本在第二步就已经可以定案。</p>')
    body.append('<p>还有一条经验值得记住：位置与伴生关系往往比单独一颗矿物的特征更管用。同一条矿脉里出现的矿物组合是有限的，'
                '把它旁边的东西看清楚，常常比反复研究手里这一块更快得出结论。若现场条件不允许下结论，把方位、产状、伴生矿物记清楚带回来，比带走一块认不准的石头有用得多。</p>')
    return page(f'易混对照 · {SITE}', '../', 'duibi/', '\n'.join(body), DUIBI_LEAD[:60])


def laili_page():
    body = ['<h1>来历与变化：名称与用途的沿革</h1>', f'<p class="lead">{E(LAILI_LEAD)}</p>']
    for sec in LAILI:
        body.append(f'<h2>{E(sec["t"])}</h2>')
        body.append(f'<p>{E(sec["p"])}</p>')
    body.append(f'<p>{E(LAILI_TAIL)}</p>')
    body.append('<p class="go">这一页提到的名称与用途，都能在实物页里找到对应的地点和当下的样子：'
                '<a href="../kuangwu/jingdezhen-gaoling.html">景德镇的高岭土</a>在江西景德镇高岭村一带，一种细腻到能捏出形状的白土，'
                '它的名字后来成了全世界这类黏土的通用叫法；'
                '<a href="../kuangwu/changle-lanbaoshi.html">昌乐的蓝宝石</a>在山东潍坊昌乐的方山与五图一带，'
                '如今是宝石，几十年前却被当地人当作能擦出火花的乌金火石；'
                '<a href="../kuangwu/yangchun-kongqueshi.html">阳春的孔雀石</a>在广东阳春，'
                '从古代炼铜的矿石变成今天供在案头的观赏石；'
                '<a href="../kuangwu/mengyin-jingangshi.html">蒙阴的钻石</a>在山东临沂蒙阴，'
                '含矿的岩石名称换过几轮，钻石本身的价值却一直没变；'
                '<a href="../yanshi/fangshan-hanbaiyu.html">房山的汉白玉</a>在北京市房山区，'
                '由古代石灰岩变质而成，采石的历史延续了上千年；'
                '<a href="../kuangwu/kekotuohai-kuangmai.html">可可托海的伟晶岩矿物</a>在新疆阿勒泰富蕴县，'
                '一处矿脉把碧玺、海蓝宝石与云母长在同一块岩石里。把这些页面的来历一节对照着读，'
                '能看到一条共同的线索：同一件东西的名字和用场，往往由当时的人需要它做什么来决定，而不是由它本身的性质决定。</p>')
    return page(f'来历与变化 · {SITE}', '../', 'laili/', '\n'.join(body), LAILI_LEAD[:60])


def main():
    pages = {}
    pages['index.html'] = home()
    pages['kuangwu/index.html'] = mod_index(
        'kuangwu', KUANGWU, '矿物实物：十二处可以上手比较的地点',
        '矿物是岩石的组成单元，也是大多数人第一次接触地质时能真正拿在手里的东西。'
        '这一部分选了十二处地点，共同点是矿物能亲眼看到、多半还能上手；每一处都按同样的顺序写：手里这块东西是什么样子，到哪里能见到它，'
        '它的来历与这些年的变化，最后是它为什么长成这样。地点的顺序大致由东向西、由易到难，先看颜色鲜明的，再看需要一点工具才能分辨的。')
    pages['yanshi/index.html'] = mod_index(
        'yanshi', YANSHI, '岩石实物：七处可以看到的岩石',
        '岩石是矿物的集合体，看它与看单颗矿物的方法不同：矿物看颗粒的性质，岩石要看颗粒之间的关系，以及岩石整体的结构与构造。'
        '这一部分选了七处岩石，覆盖了从喷出地表的玄武岩、流纹岩，到深部冷却的花岗岩、辉长岩，再到变质形成的片麻岩、混合岩与榴辉岩。'
        '同样按实物、地点、来历、原理的顺序写，目的都是让一块陌生的石头变得可以描述、可以判断。')
    for c in CASES:
        sub = 'kuangwu' if c['cat'] == '矿物' else 'yanshi'
        pages[f'{sub}/{c["slug"]}.html'] = case_page(c)
    pages['yuanli/index.html'] = yuanli_page()
    pages['duibi/index.html'] = duibi_page()
    pages['laili/index.html'] = laili_page()

    # 就地覆盖 + 清理多余文件（不使用 shutil.rmtree）
    stale = []
    for dp, dn, fn in os.walk(OUT):
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), OUT).replace('\\', '/')
            if rel not in pages and rel != '.nojekyll':
                stale.append(os.path.join(dp, f))
    for p in stale:
        try:
            os.remove(p)
        except OSError:
            pass

    for rel, s in pages.items():
        fp = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, 'w', encoding='utf-8') as fh:
            fh.write(s)
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    print('pages: %d  cases: %d (矿物 %d / 岩石 %d)  sources: %d  removed stale: %d'
          % (len(pages), len(CASES), len(KUANGWU), len(YANSHI),
             sum(len(c['src']) for c in CASES), len(stale)))


if __name__ == '__main__':
    main()
