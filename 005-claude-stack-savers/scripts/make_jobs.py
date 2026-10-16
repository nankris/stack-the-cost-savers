# 6 tasks x 5 arms x 2 reps (rep 2 run after rep 1). Arms: baseline, each saver alone, all three stacked.
import os
E = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = "/workspace/work/tig/_harness/fixtures/SUITE14"
TASKS = ["N01_median", "N02_duration", "N03_csv", "T05_stale", "T07_multihunk", "T10_replace_all"]
MD = f"{E}/scripts/short619.md"
LEAN = "--flag=--disable-slash-commands"          # + strict-mcp (run_cc default)
FULL = "--no-mcp-strict"                          # baseline: load default MCP servers
ARMS = {"baseline":  ("bare", FULL, ""),
        "claude_md": ("bare", FULL, f"--claude-md {MD}"),
        "lean":      ("bare", LEAN, ""),
        "frontload": ("frontload", FULL, ""),
        "stacked":   ("frontload", LEAN, f"--claude-md {MD}")}
jobs = []
for rep in (1, 2):
    for t in TASKS:
        for arm, (p, flags, md) in ARMS.items():
            jobs.append(f"--exp {E} --cond {arm} --task {S} --name {t} --rep {rep} --timeout 300 {flags} {md} "
                        f"--check 'cd {t} && node test.js' --prompt \"$(cat {E}/scripts/prompts/{p}__{t}.txt)\"")
open(f"{E}/scripts/jobs.txt", "w").write("\n".join(jobs) + "\n")
print(len(jobs))
