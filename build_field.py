#!/usr/bin/env python3
"""build_field.py <entries.json from fetch_entries.py> <out field.txt> [withdrawn,authors] [commitments.json]
House strategies first, then each author's latest parseable block, sorted by author.
Strategy names get the author as a prefix so they stay unique.
Open entries count only if posted by the deadline (created_at <= DEADLINE).
A committed author (commitments.json: {author: {"seq": commit_seq, "hex": prefix}}) counts only with a block
posted in (DEADLINE, REVEAL] whose sha256 (UTF-8, lines joined by \\n, no trailing newline) starts with the prefix,
and only if the commitment post itself is dated by the deadline. Open blocks from a committed author are ignored."""
import hashlib, json, re, sys, ipd
DEADLINE, REVEAL = 1790769600, 1790791200  # 2026-09-30 12:00Z and 18:00Z
src, out = sys.argv[1], sys.argv[2]
withdrawn = set(a for a in sys.argv[3].split(',') if a) if len(sys.argv) > 3 else set()  # authors who withdrew in words
commits = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else {}
house = open('house.txt').read().rstrip('\n').split('\n---\n')
rows = {r['seq']: r for r in json.load(open(src))}
for author, c in commits.items():
    r = rows.get(c['seq'])
    ok = r and r['author'] == author and c['hex'] in r['body'] and r['created_at'] <= DEADLINE
    print('commitment', author, c['seq'], 'ok' if ok else 'INVALID (missing, wrong author, prefix not in post, or late)')
    c['valid'] = bool(ok)
latest = {}
for seq in sorted(rows):
    r = rows[seq]; author = r['author']
    if author == 'fable-terminal' or seq == min(rows): continue
    for blk in re.findall(r'```[a-z]*\n(.*?)```', r['body'], re.S):
        if 'start:' not in blk: continue
        blk = blk.rstrip('\n')
        try: ipd.parse(blk)
        except ValueError as e: print('rejected', seq, author, e); continue
        if author in commits:
            h = hashlib.sha256(blk.encode()).hexdigest()
            if not (DEADLINE < r['created_at'] <= REVEAL): print('ignored', seq, author, 'committed author, block outside reveal window'); continue
            if not commits[author]['valid']: print('rejected', seq, author, 'commitment invalid'); continue
            if not h.startswith(commits[author]['hex']): print('rejected', seq, author, 'hash', h[:32], '!= commitment'); continue
            print('reveal ok', seq, author, h)
        elif r['created_at'] > DEADLINE:
            print('late', seq, author); continue
        latest[author] = (seq, blk)  # rows walked in seq order, so the last one wins
blocks = house[:]
for author in sorted(latest):
    if author in withdrawn: print('withdrawn', author); continue
    seq, blk = latest[author]
    blk = re.sub(r'(?im)^name:\s*(.*)$', lambda m: 'name: %s/%s' % (author, m.group(1).strip()), blk, count=1)
    blocks.append(blk); print('entry', seq, author)
for author in commits:
    if author not in latest: print('no valid reveal', author)
open(out, 'w').write('\n---\n'.join(blocks) + '\n')
