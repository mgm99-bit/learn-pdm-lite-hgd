"""예지보전 라이트 — Block 1 정답.

현재 폴더의 sensor_50_virtual.csv 를 읽어
  1) 설비별 평균 ± 2표준편차(평상 범위)로 이상 후보를 표시하고   (원본 덱 ③ 전처리)
  2) 이상 후보가 노이즈인지 추세인지 가르고 정비 필요 시점을 잡아  (원본 덱 ④ 분석 1)
  3) anomaly_table.csv · index.html(진동 그래프 한 장) · expected.json 을 쓴다.
표준편차는 모표준편차(statistics.pstdev). 표본표준편차로 해도 이상 후보는 같다.
"""
import csv, json, statistics as st
from pathlib import Path

SRC = "sensor_50_virtual.csv"
COLS = [("진동(mm/s)", "진동"), ("온도(℃)", "온도"), ("압력(bar)", "압력")]

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
equips = sorted({r["설비"] for r in rows})          # 설비A…, 설비B…
data = {e: [r for r in rows if r["설비"] == e] for e in equips}


def hhmm(r):
    return r["시간"][-5:]


# 1) 설비별 평상 범위와 이상 후보
stats, table = {}, []
for e in equips:
    for col, short in COLS:
        v = [float(r[col]) for r in data[e]]
        m, sd = st.mean(v), st.pstdev(v)
        lo, hi = m - 2 * sd, m + 2 * sd
        stats[(e, short)] = (m, sd, lo, hi)
        for i, (r, x) in enumerate(zip(data[e], v)):
            if x < lo or x > hi:
                table.append({"설비": e, "시간": hhmm(r), "변수": short, "값": x,
                              "i": i, "하한": round(lo, 2), "상한": round(hi, 2)})


# 2) 노이즈 vs 추세
#    노이즈 = 바로 다음 값이 평상 범위로 돌아온 한 점
#    추세   = 이상 후보로 이어지는 연속 상승 구간. 그 구간의 첫 상승 값이 '정비 필요 시점'
def trend_start(vals, i):
    j = i
    while j > 0 and vals[j - 1] < vals[j]:
        j -= 1
    return j + 1 if j < i else i      # j 는 상승 직전 바닥값, 그다음 점이 상승 시작


judged, maint = [], {}
for t in table:
    e, short = t["설비"], t["변수"]
    col = [c for c, s in COLS if s == short][0]
    vals = [float(r[col]) for r in data[e]]
    lo, hi = stats[(e, short)][2:]
    i = t["i"]
    back = i + 1 < len(vals) and lo <= vals[i + 1] <= hi
    if back:
        kind = "노이즈"
    else:
        kind = "추세"
        if short == "진동":          # 정비 필요 시점은 그래프에 그리는 진동으로만 잡는다
            s = trend_start(vals, i)
            maint.setdefault((e, short), hhmm(data[e][s]))
    judged.append({**t, "판정": kind})

with open("anomaly_table.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["설비", "시간", "변수", "값", "평상범위 하한", "평상범위 상한", "판정"])
    for t in judged:
        w.writerow([t["설비"], t["시간"], t["변수"], t["값"], t["하한"], t["상한"], t["판정"]])
    for (e, short), tm in maint.items():
        w.writerow([e, tm, short, "", "", "", "정비 필요 시점(추세 시작)"])


# 3) 진동 그래프 한 장 (외부 라이브러리 없이 SVG)
A, B = equips
times = [hhmm(r) for r in data[A]]
W, H, L, R, T, Bm = 720, 380, 48, 16, 24, 40
ymax = 4.0
x = lambda i: L + i * (W - L - R) / (len(times) - 1)
y = lambda v: T + (1 - v / ymax) * (H - T - Bm)
color = {A: "#2563eb", B: "#ea580c"}
label = {A: "설비A 프레스 메인모터", B: "설비B 차체 용접로봇 감속기"}

svg = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="설비별 진동 추이">']
for g in range(0, 5):                                   # 가로 눈금
    svg.append(f'<line x1="{L}" x2="{W-R}" y1="{y(g):.1f}" y2="{y(g):.1f}" class="grid"/>'
               f'<text x="{L-8}" y="{y(g)+4:.1f}" class="ax" text-anchor="end">{g}</text>')
for i, tm in enumerate(times):                         # 세로 눈금(1시간마다)
    if tm.endswith(":00"):
        svg.append(f'<text x="{x(i):.1f}" y="{H-Bm+18}" class="ax" text-anchor="middle">{tm}</text>')
for e in equips:
    v = [float(r["진동(mm/s)"]) for r in data[e]]
    hi = stats[(e, "진동")][3]
    pts = " ".join(f"{x(i):.1f},{y(val):.1f}" for i, val in enumerate(v))
    svg.append(f'<line x1="{L}" x2="{W-R}" y1="{y(hi):.1f}" y2="{y(hi):.1f}" stroke="{color[e]}" class="lim"/>')
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{color[e]}" stroke-width="2.5"/>')
for t in judged:
    if t["변수"] == "진동":
        svg.append(f'<circle cx="{x(t["i"]):.1f}" cy="{y(t["값"]):.1f}" r="6" class="dot"/>'
                   f'<text x="{x(t["i"])-8:.1f}" y="{y(t["값"])-10:.1f}" class="note" text-anchor="end">{t["값"]} {t["판정"]}</text>')
if (B, "진동") in maint:
    i = times.index(maint[(B, "진동")])
    svg.append(f'<line x1="{x(i):.1f}" x2="{x(i):.1f}" y1="{T}" y2="{H-Bm}" class="mt"/>'
               f'<text x="{x(i)-6:.1f}" y="{T+12}" class="note" text-anchor="end">정비 필요 시점 {maint[(B, "진동")]}</text>')
svg.append("</svg>")

a_hi, b_hi = stats[(A, "진동")][3], stats[(B, "진동")][3]
a_an = [t for t in judged if t["설비"] == A and t["변수"] == "진동"]
b_an = [t for t in judged if t["설비"] == B and t["변수"] == "진동"]
b_tp = [t for t in judged if t["설비"] == B and t["변수"] == "온도"]
summary = (f"설비A는 {a_an[0]['시간']} 진동 {a_an[0]['값']} 한 점만 튀고 돌아온 <b>노이즈</b>, "
           f"설비B는 {maint[(B, '진동')]}부터 꾸준히 오른 <b>추세</b> — 정비 신호는 설비B다.")

html = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>예지보전 라이트 — 노이즈 vs 추세</title>
<style>
:root {{ --bg:#fff; --fg:#1f2937; --mute:#6b7280; --line:#e5e7eb; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#111827; --fg:#f3f4f6; --mute:#9ca3af; --line:#374151; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font-family:system-ui,-apple-system,"Malgun Gothic",sans-serif; }}
main {{ max-width:760px; margin:0 auto; padding:24px 16px; }}
h1 {{ font-size:1.35rem; margin:0 0 4px; }}
.tag {{ color:var(--mute); font-size:.85rem; margin:0 0 12px; }}
.sum {{ margin:0 0 16px; line-height:1.55; }}
svg {{ width:100%; height:auto; display:block; }}
.grid {{ stroke:var(--line); }} .ax {{ fill:var(--mute); font-size:12px; }}
.lim {{ stroke-dasharray:6 5; stroke-width:1.5; }}
.dot {{ fill:none; stroke:#dc2626; stroke-width:2.5; }}
.note {{ fill:var(--fg); font-size:12px; }}
.mt {{ stroke:#dc2626; stroke-dasharray:3 4; }}
.legend {{ display:flex; flex-wrap:wrap; gap:6px 16px; font-size:.85rem; margin:8px 0 0; padding:0; list-style:none; }}
.legend i {{ display:inline-block; width:14px; height:3px; vertical-align:middle; margin-right:6px; }}
footer {{ color:var(--mute); font-size:.8rem; margin-top:16px; line-height:1.5; }}
</style></head>
<body><main>
<h1>노이즈인가, 추세인가 — 설비 2대 진동 (mm/s)</h1>
<p class="tag">가상 데이터(실습용) · 2026-09-15 08:00~16:00 · 20분 간격</p>
<p class="sum">{summary}</p>
{''.join(svg)}
<ul class="legend">
<li><i style="background:{color[A]}"></i>{label[A]} (점선: 평상범위 상한 {a_hi:.2f})</li>
<li><i style="background:{color[B]}"></i>{label[B]} (점선: 평상범위 상한 {b_hi:.2f})</li>
<li><i style="background:#dc2626"></i>이상 후보 · 정비 필요 시점</li>
</ul>
<footer>평상 범위 = 설비별 평균 ± 2표준편차. 한 번 튀고 돌아오면 노이즈, 임계선을 향해 꾸준히 오르면 추세 — 상승의 시작점이 정비 신호.<br>
데이터: keerhee/kma-auto-genai-3-1 · data/Day5/Day5_설비센서_50건_가상.csv (가상 데이터, 실제 기업 자료 아님)</footer>
</main></body></html>
"""
Path("index.html").write_text(html, encoding="utf-8")

# 기준값
fmt_pts = lambda ts: " · ".join(f"{t['시간']} {t['값']}" for t in ts)
values = {
    "rows": {"value": len(rows), "decimals": 0, "block": 0},
    "equipments": {"value": len(equips), "decimals": 0, "block": 0},
    "rows_per_equipment": {"value": len(data[A]), "decimals": 0, "block": 0},
    "a_vib_upper": {"value": round(a_hi, 2), "decimals": 2, "block": 1},
    "b_vib_upper": {"value": round(b_hi, 2), "decimals": 2, "block": 1},
    "a_vib_anomaly": {"value": fmt_pts(a_an), "decimals": None, "block": 1},
    "b_vib_anomalies": {"value": fmt_pts(b_an), "decimals": None, "block": 1},
    "b_temp_anomaly": {"value": fmt_pts(b_tp), "decimals": None, "block": 1},
    "b_trend_start": {"value": maint[(B, "진동")], "decimals": None, "block": 1},
}
Path("expected.json").write_text(json.dumps({"values": values}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(values, ensure_ascii=False))
