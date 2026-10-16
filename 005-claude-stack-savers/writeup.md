# Stacking Claude Code cost savers: they overlap, and one dominates

I took the three cost savers that worked in earlier experiments and ran them on the same six small bug-fix tasks: a concise CLAUDE.md, the lean flags (`--strict-mcp-config --disable-slash-commands`), and front-loading the file into the prompt. I ran each alone, all three together, and a baseline, with 2 reps per arm. All 60 runs passed. Costs are API-equivalent estimates from Claude Code's `total_cost_usd`; I'm on Pro, so this isn't what I'm billed.

Alone, they saved 15%, 63% and 12%. Stacked, they saved 68%: $0.186 → $0.060 per task. If the savings were independent and multiplied, I'd have expected 72%. Adding the percentages would give 90%, which was never realistic. So they don't cancel, but they overlap, and the lean flags do nearly all the work. Adding the other two on top of lean took me from $0.070 to $0.060.

The lean number is bigger than I expected, and it's about my setup. My default config loads three claude.ai connectors (270 tools) and 63 slash commands. That adds ~13K cache-write tokens to every run, which is most of the baseline bill. Someone with no connectors would see a much smaller lean saving.

The overlap makes sense once I look at token types. Front-loading saves cheap cache reads but adds fresh cache writes for the pasted file. On a lean prompt, those writes are a bigger share of the bill. On N03 (the biggest file), the stacked arm actually cost more than lean alone.

My takeaway: check what your default config loads before tuning prompts. After that, the CLAUDE.md and front-loading are worth roughly 10–15% more. That's real, but small. It's n=6 tasks × 2 reps on toy packages, so I trust the ranking more than the third digit.
