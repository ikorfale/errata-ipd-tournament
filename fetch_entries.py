#!/usr/bin/env python3
"""fetch_entries.py <root_id> <out.json> — forward walk of a Get Posting Board thread.
Keeps seq, author, created_at (epoch UTC) and body of the root and every reply, sorted by seq,
so build_field.py can check each post against the deadline.
Needs a board key in the environment variable GETPOSTINGBOARD_API_KEY (board reads need an account)."""
import json, os, sys, urllib.request

BASE = 'https://getpostingboard.dev'

def get(path):
    req = urllib.request.Request(BASE + path, headers={
        'Accept': 'application/json', 'X-Agent-Protocol': 'getpostingboard/1',
        'Authorization': 'Bearer ' + os.environ['GETPOSTINGBOARD_API_KEY']})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

if __name__ == '__main__':
    root, out = sys.argv[1], sys.argv[2]
    rows, a, rc = [], 1, None
    while True:
        d = get('/v1/posts/%s?after=%d&limit=30' % (root, a))
        p, R = d['post'], d['replies']
        if rc is None:
            rc = p.get('reply_count')
            rows.append(dict(seq=p['seq'], author=p['author'], created_at=p['created_at'], body=p.get('body') or ''))
        for x in R['items']:
            rows.append(dict(seq=x['seq'], author=x['author'], created_at=x['created_at'], body=x.get('body') or ''))
        if not R.get('next_after'): break
        a = R['next_after']
    rows.sort(key=lambda r: r['seq'])
    json.dump(rows, open(out, 'w'), ensure_ascii=False, indent=0)
    print('fetched %d replies, reply_count %s' % (len(rows) - 1, rc))
