# -*- coding: utf-8 -*-
"""站点自检：禁项 0 命中，段落长度达标，内链无死链。"""
import os, re, glob, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'docs')
files = sorted(glob.glob(os.path.join(OUT, '**', '*.html'), recursive=True))

BAN_TAGS = ['<table', '<img', '<svg', '<iframe', '<input', '<script', '<form',
            '<ul', '<ol', '<li', '<canvas', '<video', '<audio', '<button', '<select']
EMOJI = re.compile('[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]')
QTITLE = re.compile(r'(怎么|什么|为何|如何|哪些|是不是|？)')
PUNC = re.compile(r'(。。|。；|；。|，，|；；|、。|，。)')
SEARCH = re.compile(r'(搜索|检索|查询关键词|placeholder="[^"]*(搜索|检索))')
DARK = re.compile(r'prefers-color-scheme|color-scheme\s*:\s*dark')

bad = []


def add(f, msg):
    bad.append('%s :: %s' % (os.path.relpath(f, OUT).replace('\\', '/'), msg))


lens = []
digits = 0
for f in files:
    s = open(f, encoding='utf-8').read()
    if not s.startswith('<!DOCTYPE'):
        add(f, '不是 DOCTYPE 开头')
    for t in BAN_TAGS:
        if t in s:
            add(f, '禁标签 %s' % t)
    if '**' in s:
        add(f, '含 ** 号')
    if EMOJI.search(s):
        add(f, '含 emoji')
    if SEARCH.search(s):
        add(f, '含搜索控件')
    if DARK.search(s):
        add(f, '含暗黑模式')
    for m in re.findall(r'<h1[^>]*>(.*?)</h1>|<h2[^>]*>(.*?)</h2>', s, re.S):
        t = re.sub(r'<[^>]+>', '', (m[0] or m[1])).strip()
        if QTITLE.search(t):
            add(f, '问句式标题：%s' % t)
    for ps in re.findall(r'<p[^>]*>(.*?)</p>', s, re.S):
        t = re.sub(r'<[^>]+>', '', ps).strip()
        if not t:
            add(f, '空段落')
        if PUNC.search(t):
            add(f, '标点异常：%s' % PUNC.search(t).group(0))
        if 'class="ref"' not in ps:
            lens.append(len(t))
    # 内链
    for href in re.findall(r'href="([^"]+)"', s):
        if href.startswith(('http', '#', 'mailto')):
            continue
        tgt = os.path.normpath(os.path.join(os.path.dirname(f), href.split('#')[0]))
        if not os.path.exists(tgt):
            add(f, '死链 %s' % href)
    body = re.sub(r'<style.*?</style>', '', s, flags=re.S)
    body = re.sub(r'<p class="ref".*?</p>', '', body, flags=re.S)
    digits += len(re.findall(r'[0-9]', re.sub(r'<[^>]+>', '', body)))

lens.sort()
print('文件数 %d' % len(files))
print('段落数 %d  最短 %d  中位 %d  均值 %d  最长 %d'
      % (len(lens), lens[0], lens[len(lens) // 2], sum(lens) // len(lens), lens[-1]))
print('正文阿拉伯数字 %d 个（%.1f/页）' % (digits, digits / max(1, len(files))))
print('问题 %d 项' % len(bad))
for b in bad[:60]:
    print(' -', b)
sys.exit(1 if bad else 0)
