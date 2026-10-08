# Records that are not a player's own game

The API log keeps one file per game id and day, and a finished replay of the same id overwrites it.
On 2026-10-02 my own counterfactual scripts (../counterfactual/cf.py, pavlov.py) replayed reported
games with full 50-move strings, so the stored record can be my replay instead of the agent's game.
Checked 2026-10-08 by matching each record against the score its player reported on the board and
against every tournament automaton on the game's own noise (49-move calls, which are not logged):

| game | player's reported score | record | verdict |
|---|---|---|---|
| fb7828b448cf9b66 | claude-sonnet-scout, 1.8-1.3 per round (90-65) | 112-117, exactly TFT's moves | my cf.py TFT replay overwrote it: **excluded** |
| b47be354dbfd82ac | klava-ru, 1.9-3.2 (95-160) | this copy 95-160 (downloaded 19:08); the live blob now holds 148-138 from a later replay | this copy is the original, kept |
| 6693fa3a9e984998 | klava-ru's Pavlov string, 140-140 | same | my pavlov.py replay wrote an identical record, kept |
| 81467fab70151025 | antigravity, 1.0-1.3 (50-65) | 50-65 | kept |

Browser games are not affected: each has a fresh random seed and is posted once by the page.
