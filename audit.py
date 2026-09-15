# -*- coding: utf-8 -*-
"""发布后验真：本地字节 vs 线上字节逐页比对 → 端到端断言 → 站规扫描 → 内链抽查。"""
import io, os, re, ssl, urllib.request

ssl._create_default_https_context = ssl._create_unverified_context
BASE = 'https://wadesha.github.io/mineral-rock-handbook'
DOCS = r'C:/Users/wade/OneDrive/Z02_Geographic/矿物岩石学_实物手册/docs'
OUT = r'C:/Users/wade/AppData/Local/Temp/kwyxs/_audit.out'
log = []


def say(*a):
    log.append(' '.join(str(x) for x in a))
    io.open(OUT, 'w', encoding='utf-8').write('\n'.join(log))


def get(url, tries=4):
    last = ''
    for _ in range(tries):
        try:
            r = urllib.request.urlopen(
                urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60)
            return r.status, r.read()
        except Exception as e:
            last = str(e)
    return None, last.encode()


files = []
for dp, dn, fn in os.walk(DOCS):
    for f in fn:
        if f.endswith('.html'):
            files.append(os.path.relpath(os.path.join(dp, f), DOCS).replace('\\', '/'))
files.sort()

same, diff = 0, []
for rel in files:
    local = io.open(os.path.join(DOCS, rel), 'rb').read()
    st, remote = get(BASE + '/' + rel)
    if st == 200 and remote == local:
        same += 1
    else:
        diff.append((rel, st, len(local), len(remote) if remote else 0))
say('本地/线上字节完全一致  %d / %d' % (same, len(files)))
for d in diff:
    say('   DIFF', d)

st, b = get(BASE + '/')
txt = b.decode('utf-8', 'replace')
say('首页 状态', st, '| DOCTYPE', txt.lstrip().startswith('<!DOCTYPE'),
    '| 含中文', '矿物' in txt)

st2, b2 = get(BASE + '/didian/daye-tonglushan.html')
t2 = b2.decode('utf-8', 'replace')
say('实例页 状态', st2, '| DOCTYPE', t2.lstrip().startswith('<!DOCTYPE'),
    '| 关键词', all(k in t2 for k in ['孔雀石', '赤铜矿', '自然铜', '高岭土']))

st3, b3 = get(BASE + '/kuangzhong/')
t3 = b3.decode('utf-8', 'replace')
say('矿种页 状态', st3, '| DOCTYPE', t3.lstrip().startswith('<!DOCTYPE'),
    '| 关键词', all(k in t3 for k in ['方解石', '石榴子石', '石英']))

ban = ['<table', '<img', '<script', '<input', '<ul', '<li', '**']
say('站规扫描（实例页）', {k: t2.count(k) for k in ban})
say('站规扫描（首页）', {k: txt.count(k) for k in ban})

hrefs = [h for h in re.findall(r'href="([^"]+)"', txt) if not h.startswith('http')]
bad = []
for h in hrefs:
    st4, _ = get(BASE + '/' + h.lstrip('/'))
    if st4 != 200:
        bad.append((h, st4))
say('首页内链 %d 条，异常 %s' % (len(hrefs), bad if bad else '无'))
say('AUDIT DONE')
print(io.open(OUT, encoding='utf-8').read())
