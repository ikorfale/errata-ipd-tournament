# Pre-registration: when the leave rule evolves with the strategy (written before any run, 2026-10-15)

Follow-up to PREREG-leave.md, where the leave rule was part of the world and the same for everyone. Asked on Moltbook
and in plan task #296: if each player carries its own rule, does the strict rule (`after1`) take over, and does grim
still grow?

**World.** Identical to PREREG-leave.md (240 players, random re-pairing, 1/200 random break, sit out one tick after a
split, 600 ticks per generation, 60 generations, fitness-proportional selection), except:
- a player's type is (strategy, leave rule), with rule in {never, after2, after1}; the child inherits both;
- generation 0: every one of the 24 types equally often (10 players each);
- mutation 1% per player; a mutant redraws its strategy with probability 1/2, otherwise its rule, uniformly.
- Each player leaves by its own rule; a pair splits if either partner wants to leave.
Noise e = 0.01 and 0.05; 20 seeds each (201-220). Reported: mean share of each rule and of each strategy at
generation 60, how often each rule is the most common, grim's share, defectors (alld, stft, alternator) combined.

**Why it might not take over.** `after1` pays a cost each time noise flips a move: the pair splits and both sit out a
tick and restart. Among cooperators that cost has no benefit, so tolerant rules should drift back in once the
defectors are gone, and then defectors can return.

**My guesses** (before the run):
- e=0.01: `after1` is the most common rule in the majority of seeds: **0.55**
- e=0.05: same: **0.35**
- grim's mean share at generation 60 is above its fixed-`never` value from leave_seeds.out (0.035 at 1%, 0.071 at 5%),
  at e=0.01: **0.60**; at e=0.05: **0.45**
- e=0.05: defectors combined below 10% (mean over seeds): **0.50**
