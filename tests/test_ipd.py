import os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest, ipd, exact_ipd

HOUSE = os.path.join(os.path.dirname(__file__), '..', 'field', 'house.txt')
S = {s['name']: s for s in ipd.load(HOUSE)}

def test_house_field_parses():
    assert list(S) == ['allc', 'alld', 'tft', 'stft', 'grim', 'pavlov', 'tf2t', 'alternator']

@pytest.mark.parametrize('bad', [
    'name: x\nstart: A\nA: C ; C->A D->Z',            # missing target state
    'name: x\nstart: B\nA: C ; C->A D->A',            # start is not a state
    'name: x\nstart: A\nA: X ; C->A D->A',            # move is not C or D
    'name: x\nstart: S0\n' + '\n'.join('S%d: C ; C->S0 D->S0' % i for i in range(9)),   # nine states
])
def test_parse_rejects(bad):
    with pytest.raises(ValueError):
        ipd.parse(bad)

def test_eight_states_is_the_limit():
    ok = 'name: x\nstart: S0\n' + '\n'.join('S%d: C ; C->S0 D->S0' % i for i in range(8))
    assert len(ipd.parse(ok)['states']) == 8

def test_noiseless_payoffs():
    rng = random.Random(0)
    assert ipd.match(S['allc'], S['alld'], 200, 0.0, rng) == (0.0, 5.0)
    assert ipd.match(S['tft'], S['tft'], 200, 0.0, rng) == (3.0, 3.0)
    assert ipd.match(S['alld'], S['alld'], 200, 0.0, rng) == (1.0, 1.0)

def test_exact_allc_alld_under_noise():
    # both players flip independently with p=0.05: allc plays C w.p. .95, alld plays D w.p. .95
    n = 0.05; pc, pd = 1 - n, n            # P(allc shows C), P(alld shows C)
    want_a = pc * pd * 3 + pc * (1 - pd) * 0 + (1 - pc) * pd * 5 + (1 - pc) * (1 - pd) * 1
    a, _ = exact_ipd.exact(S['allc'], S['alld'])
    assert a == pytest.approx(want_a, abs=1e-12)

def test_sampling_agrees_with_exact():
    a, b = S['pavlov'], S['tf2t']
    ea, eb = exact_ipd.exact(a, b)
    rng = random.Random(1); xs = [ipd.match(a, b, 200, 0.05, rng) for _ in range(400)]
    sa = sum(x for x, _ in xs) / len(xs); sb = sum(y for _, y in xs) / len(xs)
    assert sa == pytest.approx(ea, abs=0.03) and sb == pytest.approx(eb, abs=0.03)

def test_replicator_keeps_simplex():
    M = [[3, 0], [5, 1]]                   # C vs D: D takes over
    h = ipd.replicator(M, gens=200)
    assert all(abs(sum(p) - 1) < 1e-9 for p in h)
    assert h[-1][1] > 0.99

def test_seed_depends_on_salt(tmp_path):
    f = tmp_path / 'f.txt'; f.write_bytes(b'x')
    assert ipd.seed_of(str(f), 'a') != ipd.seed_of(str(f), 'b')
