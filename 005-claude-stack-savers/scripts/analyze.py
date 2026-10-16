import csv, statistics as S, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(f"{D}/results/runs.csv")))
ARMS = ["baseline", "claude_md", "lean", "frontload", "stacked"]
tasks = sorted({r["task"] for r in rows})
# only tasks with all 5 arms, so means are paired
tasks = [t for t in tasks if all(any(r["task"] == t and r["cond"] == a for r in rows) for a in ARMS)]
def runs(t, a): return [r for r in rows if r["task"] == t and r["cond"] == a]
def tcost(t, a): return S.mean(float(r["est_cost_usd"]) for r in runs(t, a))
out = []
for a in ARMS:
    rs = [r for t in tasks for r in runs(t, a)]
    m = lambda k: S.mean(float(r[k]) for r in rs)
    out.append(dict(arm=a, n=len(rs), passed=sum(r["passed"] == "True" for r in rs),
                    cost=round(m("est_cost_usd"), 4), first_prompt=round(m("first_call_cache_creation") + m("first_call_cache_read") + m("first_call_input")),
                    total_tokens=round(m("total_tokens")), output_tokens=round(m("output_tokens")),
                    turns=round(m("num_turns"), 2), tool_calls=round(m("tool_calls"), 2), wall_s=round(m("wall_s"), 1)))
base = out[0]["cost"]
for o in out: o["saving_pct"] = round(100 * (1 - o["cost"] / base), 1)
sv = {o["arm"]: o["saving_pct"] / 100 for o in out}
pred_mult = 100 * (1 - (1 - sv["claude_md"]) * (1 - sv["lean"]) * (1 - sv["frontload"]))
pred_sum = 100 * (sv["claude_md"] + sv["lean"] + sv["frontload"])
per_task = []
for t in tasks:
    b = tcost(t, "baseline")
    per_task.append({"task": t, **{a: round(tcost(t, a), 4) for a in ARMS},
                     "stacked_saving_pct": round(100 * (1 - tcost(t, "stacked") / b), 1)})
w = csv.DictWriter(open(f"{D}/results/summary.csv", "w"), fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
w = csv.DictWriter(open(f"{D}/results/per_task.csv", "w"), fieldnames=list(per_task[0])); w.writeheader(); w.writerows(per_task)
for o in out: print(o)
for p in per_task: print(p)
print(f"predicted stacked saving: multiplicative {pred_mult:.1f}%, simple sum {pred_sum:.1f}%; observed {sv['stacked']*100:.1f}%")

fig, ax = plt.subplots(figsize=(8, 4.6))
labels = ["baseline", "concise\nCLAUDE.md", "lean flags", "front-load\nfiles", "all three\nstacked"]
cols = ["#9aa0a6", "#4a7fc1", "#4a7fc1", "#4a7fc1", "#d17b4a"]
ys = [o["cost"] for o in out]
bars = ax.bar(range(5), ys, 0.6, color=cols)
for i, o in enumerate(out):
    txt = f"${o['cost']:.3f}" + ("" if i == 0 else f"\n{-o['saving_pct']:+.0f}%")
    ax.text(i, o["cost"] + base * 0.01, txt, ha="center", va="bottom", fontsize=9, color="#333")
pred = base * (1 - pred_mult / 100)
ax.axhline(pred, color="#333", ls="--", lw=1)
ax.text(2.6, pred + base * 0.01, f"if the three savings multiplied: ${pred:.3f}", fontsize=8, va="bottom", ha="left", color="#333")
ax.set_xticks(range(5)); ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("mean API-equivalent est. $ per task"); ax.set_ylim(0, base * 1.2)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.yaxis.grid(True, color="#eee"); ax.set_axisbelow(True)
ax.set_title(f"#005 Claude Code savers, alone vs stacked ({len(tasks)} tasks × 2 runs per arm, all passed)", fontsize=11)
plt.tight_layout(); plt.savefig(f"{D}/results/chart.png", dpi=120)
