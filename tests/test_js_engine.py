"""The JS engine (play/engine.js) must give the same scores as ipd.py on the same random stream:
every pairing of the house and the final field, 200 rounds, noise 0.05, seeds 1..20."""
import json, os, subprocess, sys, shutil, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import ipd
from rng32 import Mulberry32

def py_scores(fname):
    S = ipd.load(os.path.join(ROOT, 'field', fname)); out = []
    for seed in range(1, 21):
        rng = Mulberry32(seed)
        for i in range(len(S)):
            for j in range(i, len(S)):
                x, y = ipd.match(S[i], S[j], 200, 0.05, rng)
                out.append([seed, S[i]['name'], S[j]['name'], x, y])
    return out

@unittest.skipUnless(shutil.which('node'), 'node not installed')
class JsEngine(unittest.TestCase):
    def check(self, fname):
        js = json.loads(subprocess.run(['node', os.path.join(HERE, 'js_vs_py.js'), fname],
                                       capture_output=True, text=True, check=True).stdout)
        py = py_scores(fname)
        self.assertEqual(len(js), len(py))
        for a, b in zip(js, py): self.assertEqual(a, b)
    def test_house(self): self.check('house.txt')
    def test_final_field(self): self.check('final.txt')

if __name__ == '__main__':
    unittest.main()
