# -*- coding: utf-8 -*-
import io, re, os

BASE = r'C:\Users\wade\AppData\Local\Temp\kwyxs'

def parse_block(block):
    d = {'ore':[], 'why':[], 'how':[], 'now':[], 'src':[]}
    cur = None; buf = None
    def flush():
        nonlocal buf
        if buf is not None and cur is not None:
            kind, key = cur[0], cur[1]
            val = buf.strip()
            if kind == 'single':
                d[key] = val
            elif kind == 'list':
                if key == 'ore':
                    if '｜' in val:
                        nm, tx = val.split('｜',1); d['ore'].append((nm.strip(), tx.strip()))
                elif key == 'src':
                    if ' | ' in val:
                        t,u = val.split(' | ',1); d['src'].append((t.strip(), u.strip()))
                else:
                    d[key].append(val)
        buf = None
    for line in block.splitlines():
        if not line.strip():
            continue
        m = re.match(r'^#(slug|name|en|where|bg|ore|why|how|now|src)\b\s*(.*)$', line)
        if m:
            flush()
            tag = m.group(1); rest = m.group(2)
            cur = ('single', tag) if tag in ('slug','name','en','where','bg') else ('list', tag, None)
            buf = rest
        else:
            if buf is not None:
                buf = buf + ' ' + line.strip()
    flush()
    return d

def parse_file(path):
    txt = io.open(path, encoding='utf-8').read()
    places=[]
    for blk in txt.split('@@PLACE'):
        if '@@END' in blk: blk = blk.split('@@END')[0]
        blk = blk.strip()
        if not blk: continue
        d = parse_block(blk)
        if d.get('slug'): places.append(d)
    return places

def q(s):
    return repr(s)

def dump(places, n):
    out=[]
    out.append('# -*- coding: utf-8 -*-')
    out.append('"""自动生成：本组地点数据（联网核查后写成）。"""')
    out.append('')
    out.append('P%d = [' % n)
    for d in places:
        out.append('{')
        out.append(" 'slug': %s," % q(d['slug']))
        out.append(" 'name': %s," % q(d['name']))
        out.append(" 'en': %s," % q(d['en']))
        out.append(" 'where': %s," % q(d['where']))
        out.append(" 'bg': %s," % q(d['bg']))
        ores='['+', '.join('(%s, %s)'%(q(n),q(t)) for n,t in d['ore'])+']'
        out.append(" 'ores': %s," % ores)
        why='['+', '.join(q(x) for x in d['why'])+']'
        out.append(" 'why': %s," % why)
        how='['+', '.join(q(x) for x in d['how'])+']'
        out.append(" 'how': %s," % how)
        now='['+', '.join(q(x) for x in d['now'])+']'
        out.append(" 'now': %s," % now)
        src='['+', '.join('(%s, %s)'%(q(t),q(u)) for t,u in d['src'])+']'
        out.append(" 'src': %s," % src)
        out.append('},')
    out.append(']')
    return '\n'.join(out)+'\n'

groups=[('a',11),('b',12),('c',13),('d',14)]
total=0
for tag,n in groups:
    places=parse_file(os.path.join(BASE,'raw_%s.txt'%tag))
    fn=os.path.join(BASE,'d_p%d.py'%n)
    io.open(fn,'w',encoding='utf-8').write(dump(places, n))
    print('wrote', fn, 'places=%d'%len(places))
    total+=len(places)

# update build_site.py in Temp
bs=io.open(os.path.join(BASE,'build_site.py'),encoding='utf-8').read()
imp_old="from d_p10 import P10"
imp_new=imp_old+'\n'.join("\nfrom d_p%d import P%d"%(i,i) for i in (11,12,13,14))
assert imp_old in bs, 'import anchor missing'
bs=bs.replace(imp_old, imp_new, 1)
pl_old="PLACES = P1 + P2 + P3 + P4 + P5 + P6 + P7 + P8 + P9 + P10"
pl_new=pl_old+" + P11 + P12 + P13 + P14"
assert pl_old in bs, 'PLACES anchor missing'
bs=bs.replace(pl_old, pl_new, 1)
io.open(os.path.join(BASE,'build_site.py'),'w',encoding='utf-8').write(bs)
print('build_site.py updated, total new places=%d'%total)
