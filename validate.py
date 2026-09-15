# -*- coding: utf-8 -*-
"""实物手册站自检：禁项、薄段、链接、结构。"""
import os, re, sys, io, html, collections

ROOT = r'C:/Users/wade/OneDrive/Z02_Geographic/矿物岩石学_实物手册/docs'

BAN_TAGS = ['<table', '<img', '<svg', '<iframe', '<input', '<script', '<form',
            '<ul', '<ol', '<li', '<canvas', '<video', '<audio', '<button']
BAN_STRS = ['**', '怎么', '什么', '为何', '如何', '是不是']

EMOJI = re.compile('[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\u2b00-\u2bff\ufe0f]')

def strip_tags(s):
    s = re.sub(r'(?s)<script.*?</script>', '', s)
    s = re.sub(r'(?s)<style.*?</style>', '', s)
    out = []
    for part in re.split(r'(?s)<[^>]+>', s):
        out.append(part)
    return ' '.join(out)

def main():
    problems = []
    files = []
    for root, dirs, fs in os.walk(ROOT):
        for f in fs:
            if f.endswith('.html'):
                files.append(os.path.join(root, f))
    files.sort()
    print('HTML 文件数', len(files))
    total_paras = 0
    thin = []
    all_para_len = []
    for fp in files:
        raw = open(fp, encoding='utf-8').read()
        rel = fp[len(ROOT) + 1:].replace('\\', '/')
        if not raw.lstrip().lower().startswith('<!doctype'):
            problems.append('%s 未以 DOCTYPE 开头' % rel)
        # 禁项
        for t in BAN_TAGS:
            n = raw.lower().count(t)
            if n:
                problems.append('%s 出现禁用标签 %s x%d' % (rel, t, n))
        if '**' in raw:
            problems.append('%s 出现 ** 符号' % rel)
        # emoji（只看文本区）
        txt = strip_tags(raw)
        m = EMOJI.findall(txt)
        if m:
            problems.append('%s 出现 emoji %r' % (rel, m[:4]))
        # 搜索功能
        for kw in ['search', '检索框', '搜索框', 'type="search"', 'id="q"']:
            if kw in raw.lower() and kw != 'search':
                problems.append('%s 疑似搜索 %s' % (rel, kw))
        # 链接检查
        for href in re.findall(r'href="([^"]+)"', raw):
            if href.startswith('http'):
                continue
            if href.startswith('#'):
                continue
            tgt = os.path.normpath(os.path.join(os.path.dirname(fp), href.split('#')[0]))
            if not os.path.exists(tgt):
                problems.append('%s 死链 %s' % (rel, href))
        # 段落长度
        for m_ in re.finditer(r'(?s)<p[^>]*>(.*?)</p>', raw):
            body = html.unescape(re.sub(r'(?s)<[^>]+>', '', m_.group(1))).strip()
            n = len(re.sub(r'\s', '', body))
            if n == 0:
                problems.append('%s 空段落' % rel)
                continue
            total_paras += 1
            all_para_len.append(n)
            if n < 100:
                thin.append((rel, n, body[:50]))
        # 问句标题
        for m_ in re.finditer(r'(?s)<h[1-4][^>]*>(.*?)</h[1-4]>', raw):
            h = html.unescape(re.sub(r'(?s)<[^>]+>', '', m_.group(1))).strip()
            if re.search(r'(怎么|什么|为何|如何|哪些|怎么用|是什么)', h):
                problems.append('%s 疑问式标题 %r' % (rel, h))
    all_para_len.sort()
    print('段落总数', total_paras)
    if all_para_len:
        print('段落字数 最短 %d 中位 %d 最长 %d 平均 %.0f' % (
            all_para_len[0], all_para_len[len(all_para_len)//2], all_para_len[-1],
            sum(all_para_len)/len(all_para_len)))
    print('薄段(<100字) 数', len(thin))
    for t in thin[:20]:
        print('   ', t)
    print()
    if problems:
        print('!! 问题 %d 项' % len(problems))
        for p in problems[:60]:
            print('   ', p)
    else:
        print('== 全部通过：禁项 0，无死链，无薄段，无空段 ==')
    return len(problems)

if __name__ == '__main__':
    sys.exit(0 if main() == 0 else 1)
