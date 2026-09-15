# -*- coding: utf-8 -*-
"""发布到 GitHub Pages：显式建 blob（utf-8 传原文）+ base_tree + PATCH ref，再轮询 Pages 构建。"""
import base64, io, json, os, ssl, sys, time, urllib.request, urllib.error

ssl._create_default_https_context = ssl._create_unverified_context
TOKEN = io.open(r'C:/Users/wade/.workbuddy/credentials/github-sdgeo.token',
                encoding='utf-8').read().strip()
OWNER = 'wadesha'
REPO = 'mineral-rock-handbook'
API = 'https://api.github.com'
ROOT = r'C:/Users/wade/OneDrive/Z02_Geographic/矿物岩石学_实物手册'
DOCS = os.path.join(ROOT, 'docs')
OUT = r'C:/Users/wade/AppData/Local/Temp/kwyxs/_pub.out'
WIPE = os.environ.get('WIPE') == '1'
log = []


def say(*a):
    log.append(' '.join(str(x) for x in a))
    io.open(OUT, 'w', encoding='utf-8').write('\n'.join(log))


def call(method, path, body=None):
    data = json.dumps(body).encode('utf-8') if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header('Authorization', 'Bearer ' + TOKEN)
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('User-Agent', 'wb-publish')
    if data:
        req.add_header('Content-Type', 'application/json')
    try:
        r = urllib.request.urlopen(req, timeout=90)
        return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')


def collect():
    files = []
    for dp, dn, fn in os.walk(DOCS):
        for f in fn:
            fp = os.path.join(dp, f)
            files.append(('docs/' + os.path.relpath(fp, DOCS).replace('\\', '/'), fp))
    for f in sorted(os.listdir(ROOT)):
        if f.endswith('.py'):
            files.append((f, os.path.join(ROOT, f)))
    return sorted(files)


def main():
    files = collect()
    say('files', len(files))
    st, _ = call('GET', f'/repos/{OWNER}/{REPO}')
    if st == 404:
        st, j = call('POST', '/user/repos', {'name': REPO, 'private': False,
                                             'auto_init': False,
                                             'description': '矿物与岩石实物手册'})
        say('create repo', st, j.get('full_name'))
    else:
        say('repo exists', st)

    st, _ = call('GET', f'/repos/{OWNER}/{REPO}/git/ref/heads/main')
    if st in (404, 409):
        st, j = call('PUT', f'/repos/{OWNER}/{REPO}/contents/.gitkeep',
                     {'message': 'bootstrap',
                      'content': base64.b64encode(b'placeholder').decode(),
                      'branch': 'main'})
        say('bootstrap main', st)
    st, ref = call('GET', f'/repos/{OWNER}/{REPO}/git/ref/heads/main')
    if st != 200:
        say('REF FAIL', st, str(ref)[:200])
        return 1
    head = ref['object']['sha']
    st, cm = call('GET', f'/repos/{OWNER}/{REPO}/git/commits/{head}')
    base_tree = cm['tree']['sha']
    say('head', head[:8], 'base_tree', base_tree[:8])

    blobs = []
    for rel, fp in files:
        txt = io.open(fp, 'rb').read().decode('utf-8')
        st, j = call('POST', f'/repos/{OWNER}/{REPO}/git/blobs',
                     {'content': txt, 'encoding': 'utf-8'})
        if st not in (200, 201):
            say('BLOB FAIL', rel, st, str(j)[:200])
            return 1
        blobs.append({'path': rel, 'mode': '100644', 'type': 'blob', 'sha': j['sha']})
    say('blobs ok', len(blobs))

    payload = {'tree': blobs}
    if not WIPE:
        payload['base_tree'] = base_tree
    st, t = call('POST', f'/repos/{OWNER}/{REPO}/git/trees', payload)
    if st not in (200, 201):
        say('TREE FAIL', st, str(t)[:300])
        return 1
    st, c = call('POST', f'/repos/{OWNER}/{REPO}/git/commits',
                 {'tree': t['sha'], 'parents': [head],
                  'message': '按地点重构：22 处能去看的地点，逐处列出可见矿种与共生关系'})
    if st not in (200, 201):
        say('COMMIT FAIL', st, str(c)[:300])
        return 1
    st, _ = call('PATCH', f'/repos/{OWNER}/{REPO}/git/refs/heads/main', {'sha': c['sha']})
    say('ref', st, c['sha'][:8])

    st, p = call('GET', f'/repos/{OWNER}/{REPO}/pages')
    if st == 404:
        st, p = call('POST', f'/repos/{OWNER}/{REPO}/pages',
                     {'source': {'branch': 'main', 'path': '/docs'}})
        say('pages create', st, str(p)[:160])
    else:
        say('pages exists', st, p.get('html_url'))

    for i in range(40):
        st, b = call('GET', f'/repos/{OWNER}/{REPO}/pages/builds/latest')
        if isinstance(b, dict) and b.get('status') == 'built':
            say('pages built after', i * 8, 's')
            break
        time.sleep(8)
    else:
        say('pages build not confirmed')
    say('DONE')
    return 0


if __name__ == '__main__':
    sys.exit(main())
