# -*- coding: utf-8 -*-
"""发布后端到端验真：本地文件字节 vs 线上响应字节全量比对。"""
import os, ssl, re, sys, urllib.request, urllib.error

ssl._create_default_https_context = ssl._create_unverified_context
BASE = 'https://wadesha.github.io/mineral-rock-handbook/'
DOCS = r'C:\Users\wade\OneDrive\Z02_Geographic\矿物岩石学_实物手册\docs'

files = []
for dp, dn, fn in os.walk(DOCS):
    for f in fn:
        fp = os.path.join(dp, f)
        files.append(os.path.relpath(fp, DOCS).replace('\\', '/'))
files = [f for f in sorted(files) if f != '.nojekyll']

bad = []
for rel in files:
    req = urllib.request.Request(BASE + rel, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        r = urllib.request.urlopen(req, timeout=60)
        on = r.read()
    except urllib.error.HTTPError as e:
        bad.append('%s HTTP %s' % (rel, e.code))
        continue
    lo = open(os.path.join(DOCS, rel), 'rb').read()
    if on != lo:
        bad.append('%s 字节不一致 (%d vs %d)' % (rel, len(on), len(lo)))
        continue
    head = on[:15].decode('utf-8', 'ignore')
    if '<!DOCTYPE' not in head:
        bad.append('%s 不是 DOCTYPE 开头：%s' % (rel, head))

# 旧目录必须已消失
for old in ['kuangzhong/index.html']:
    try:
        urllib.request.urlopen(urllib.request.Request(BASE + old,
                               headers={'User-Agent': 'Mozilla/5.0'}), timeout=30)
        bad.append('旧页面仍可访问：%s' % old)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            bad.append('旧页面返回 %s' % e.code)

# 首页关键词
req = urllib.request.Request(BASE, headers={'User-Agent': 'Mozilla/5.0'})
home = urllib.request.urlopen(req, timeout=60).read().decode('utf-8')
for kw in ['能去看的地点', 'didian/']:
    if kw not in home:
        bad.append('首页缺少 %s' % kw)
if 'prefers-color-scheme' in home:
    bad.append('首页仍有暗黑模式')
if '按矿种找地点' in home:
    bad.append('首页仍有按矿种找地点')

print('比对 %d 个文件，问题 %d 项' % (len(files), len(bad)))
for b in bad:
    print(' -', b)
sys.exit(1 if bad else 0)
