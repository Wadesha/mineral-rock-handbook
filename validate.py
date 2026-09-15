# -*- coding: utf-8 -*-
"""自检：禁项、问句标题、死链、标点、数字密度、段落长度。"""
import os, re, html

ROOT = r'C:/Users/wade/OneDrive/Z02_Geographic/矿物岩石学_实物手册/docs'
BAN_TAGS = ['<table', '<img', '<svg', '<iframe', '<input', '<script', '<form',
            '<ul', '<ol', '<li', '<canvas', '<video', '<audio', '<button', '<select']
EMOJI = re.compile('[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\u2b00-\u2bff\ufe0f]')


def text_of(s):
    s = re.sub(r'(?s)<style.*?</style>', '', s)
    s = re.sub(r'(?s)<script.*?</script>', '', s)
    return re.sub(r'(?s)<[^>]+>', ' ', s)


def main():
    probs = []
    files = []
    for dp, dn, fn in os.walk(ROOT):
        for f in fn:
            if f.endswith('.html'):
                files.append(os.path.join(dp, f))
    files.sort()
    lens, digits, paras = [], 0, 0
    print('HTML 文件数', len(files))
    for fp in files:
        raw = open(fp, encoding='utf-8').read()
        rel = os.path.relpath(fp, ROOT).replace('\\', '/')
        if not raw.lstrip().lower().startswith('<!doctype'):
            probs.append('%s 未以 DOCTYPE 开头' % rel)
        for t in BAN_TAGS:
            if t in raw.lower():
                probs.append('%s 出现禁用标签 %s' % (rel, t))
        for b in ['**', 'type="search"', 'id="q"']:
            if b in raw:
                probs.append('%s 出现禁用内容 %s' % (rel, b))
        if EMOJI.search(text_of(raw)):
            probs.append('%s 出现 emoji' % rel)
        for href in re.findall(r'href="([^"]+)"', raw):
            if href.startswith(('http', '#')):
                continue
            tgt = os.path.normpath(os.path.join(os.path.dirname(fp), href.split('#')[0]))
            if not os.path.exists(tgt):
                probs.append('%s 死链 %s' % (rel, href))
        for m in re.finditer(r'(?s)<h[1-4][^>]*>(.*?)</h[1-4]>', raw):
            h = html.unescape(re.sub(r'(?s)<[^>]+>', '', m.group(1))).strip()
            if re.search(r'(怎么|什么|为何|如何|哪些|是不是|？)', h):
                probs.append('%s 疑问式标题 %r' % (rel, h))
        for m in re.finditer(r'(?s)<p[^>]*>(.*?)</p>', raw):
            body = html.unescape(re.sub(r'(?s)<[^>]+>', '', m.group(1))).strip()
            n = len(re.sub(r'\s', '', body))
            if n == 0:
                probs.append('%s 空段落' % rel)
                continue
            paras += 1
            lens.append(n)
            digits += len(re.findall(r'\d', body))
        for b in ['。。', '。；', '；。', '，，', '；；', '、。', '，。']:
            if b in raw:
                probs.append('%s 标点异常 %s' % (rel, b))
    lens.sort()
    print('段落总数 %d  最短 %d  中位 %d  最长 %d  平均 %.0f'
          % (len(lens), lens[0], lens[len(lens) // 2], lens[-1], sum(lens) / len(lens)))
    print('正文阿拉伯数字总数 %d（平均每页 %.1f）' % (digits, digits / max(len(files), 1)))
    if probs:
        print('\n!! 问题 %d 项' % len(probs))
        for p in probs[:40]:
            print('   ', p)
    else:
        print('\n== 全部通过：禁项 0，无死链，无问句标题，无标点异常 ==')
    return len(probs)


if __name__ == '__main__':
    raise SystemExit(0 if main() == 0 else 1)
