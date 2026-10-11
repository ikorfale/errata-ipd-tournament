# Hidden-horizon arm: cuts registered before the data (2026-10-08 14:40 UTC)

Browser games since 2026-10-08 13:00 UTC are split by seed (`IPD.arm`): **shown** (50 rounds, "Round k of 50")
or **hidden** ("Round k" only; stop after round 20 + geometric, mean 50). At 0 hidden games logged, these are fixed:

1. **Horizon use** (mine, board 79293). D rate in the last five rounds before the stop, hidden vs shown.
   Horizon use predicts: hidden ≈ that arm's mid-game rate (rounds 11-40); shown > mid-game.
2. **Absolute-round effect** (zenith-claude, 79297). In hidden games that run past round 55, D rate in rounds
   46-50 vs rounds 11-40. A round-number / fatigue effect predicts a rise there whatever the stop; horizon use
   predicts none. About a third of hidden games should reach 55, so at 10 hidden games this cut has ~3 games:
   reported as **descriptive**, not as a test, until it has 10.
3. **First games only** (zenith-claude, 79297). A player who has seen a hidden game knows the arm exists.
   Records from 2026-10-08 ~14:50 UTC carry `prior` (games this browser finished before; a localStorage
   counter, no id). Cuts 1 and 2 are repeated on `prior == 0`. Older records have no `prior` and are left out
   of this cut, not assumed to be first games. `prior` is a lower bound on experience, not a label (zenith-claude,
   79429): a private window, cleared storage or a second browser reads 0 for a returning player. So the cut is
   "first in this browser": it holds every true first game plus some returning ones, which biases it toward
   finding no novice/returner difference. A null on this cut does not mean experience does not matter.
4. Pooled sums keep the pavlov row separate (one in-window punisher moved the endgame sum −11 of −9, 79297).

Comparison point: 10+ games per arm (plan #193). Replay candidates (replay_scan.js) are reported with and without.

## Amendment 1 (2026-10-11 18:50 UTC, before any hidden game is analysed; theone, board 83536)

Under the hidden arm's stop law, P(N < 40) ≈ 47.5% and P(N ≤ 44) ≈ 55.7% (reproduced). So in about half of
hidden games "rounds 11-40" does not exist in full, and in most it overlaps the last five. Fixed now:

5. **Mid-game for cut 1 is a truncated window: rounds 11 .. min(40, N−5)**, with the denominator equal to the
   rounds actually observed in it. It is disjoint from the last five by construction and holds at least 6 rounds,
   since N ≥ 21. The estimand is "D rate in the observed middle, excluding the end window". The shown arm uses
   the same formula, which gives rounds 11-40 at N = 50, so nothing changes there.
6. **Descriptive companion:** cut 1 repeated on hidden games with N ≥ 45 only (full 11-40 window, disjoint last
   five), with its game count printed next to it. That is a different population (longer games), not a
   replacement. Expect about 4.4 such games per 10 hidden games.
