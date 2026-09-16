# -*- coding: utf-8 -*-
import io, re, os

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
        if '@@END' in blk:
            blk = blk.split('@@END')[0]
        blk = blk.strip()
        if not blk: continue
        d = parse_block(blk)
        if d.get('slug'):
            places.append(d)
    return places

for tag in 'abcd':
    p = parse_file(r'C:\Users\wade\AppData\Local\Temp\kwyxs\raw_%s.txt' % tag)
    print('=== raw_%s : %d places ===' % (tag, len(p)))
    for d in p:
        miss=[]
        for k in ('slug','name','en','where','bg'):
            if not d.get(k): miss.append(k)
        for k in ('ore','why','how','now','src'):
            if not d.get(k): miss.append(k)
        print('  %-22s ores=%d why=%d how=%d now=%d src=%d %s' % (
            d.get('slug'), len(d.get('ore',[])), len(d.get('why',[])),
            len(d.get('how',[])), len(d.get('now',[])), len(d.get('src',[])),
            ('MISSING:%s'%','.join(miss)) if miss else ''))
