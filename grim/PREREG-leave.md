# Pre-registration: does the option to leave kill grim? (written before any run, 2026-10-15)

**World.** 240 players, 30 of each house strategy. Each tick every partnered pair plays one round of the noisy PD
(both moves flipped independently with probability e). A partnership also ends at random with probability 1/200 per
tick (expected length 200 rounds, the same as the tournament). A player without a partner sits out one tick (payoff
0) and is then paired at random with another unpartnered player; its automaton restarts from its start state.
**Leave rules** (the same for everyone, part of the world, not of the strategy): `never`; `after2` = a player leaves
when it has observed D from its partner in two consecutive rounds; `after1` = leaves after any observed D.
**Selection.** A generation is 600 ticks; fitness = mean payoff per tick (sitting out counts as 0). The next
generation's 240 players are drawn with probabilities proportional to fitness share, plus 1% mutation to a random
strategy. 60 generations. Noise e = 0.01 and 0.05; seeds 1, 2, 3.

**Check of the world.** Under `never`, this should look like the round-robin result in grim_survives.out: grim
strong at 1% and 5% noise. If it does not, the difference is in the world (random pairing, finite population,
mutation), and I will say so before reading the leave conditions.

**My guess.** Leaving dissolves grim's lock-ins after a noise flip, so grim stops losing to itself, but it also takes
away its income from Pavlov (Pavlov's partner, or grim's, leaves after two Ds). I expect grim to lose its edge:
- P(grim is the most common strategy at generation 60, majority of seeds) under `after2`, e=0.05: **0.30**
- same under `never`, e=0.05: **0.60**
- under `after1`, defectors (alld, stft, alternator) are below 5% combined at generation 60: **0.75**
