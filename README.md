# 예지보전 라이트: 노이즈인가, 추세인가 — learn-pdm-lite-hgd

설비 센서 데이터에서 한 번의 튐(노이즈)과 추세적 상승(정비 신호)을 가르는 10분 실습이다. 수업은 Claude Code 스킬 `/learn-pdm-lite-hgd`가 진행한다 (Skills as Curriculum). 이 강의는 mgm99-bit이 course-forge로 직접 만들었다.

- **결과 대시보드**: https://mgm99-bit.github.io/learn-pdm-lite-hgd/
- 처음이면 [GUIDE.md](GUIDE.md)부터. 기본 환경은 Claude 데스크톱 앱(Code 탭). VS Code는 GUIDE 부록 B

![진동 그래프](.claude/skills/learn-pdm-lite-hgd/assets/answers/preview.png)

## 설치 — 한 줄

Claude Code 입력칸에 붙여 넣는다.

```
npx skills add mgm99-bit/learn-pdm-lite-hgd --agent claude-code --global --yes 를 실행해 줘
```

새 세션에서 `/learn-pdm-lite-hgd`를 입력하면 수업이 시작된다. zip을 받았다면 GUIDE.md 2단계대로 설치한다.

## 블록

| Block | 주제 | 끝나면 생기는 것 |
|---|---|---|
| 0 | 준비 (2분) | `~/pdm-lite` 폴더 · 센서 데이터 · `env_check.txt` |
| 1 | 노이즈 vs 추세 (5분) | `anomaly_table.csv` · 진동 그래프 `index.html` · 퀴즈 1문항 |
| 2 | 공개 (3분) | 내 GitHub Pages 주소 · 동료에게 보낼 한 줄 |

## 수업 방식

| 구분 | 내용 |
|---|---|
| 목표 — AI Native | AI에게 맡기는 것이 기본인 방식으로 일한다 |
| 방법 — Skills as Curriculum | 스킬이 블록마다 설명 → 실습 → STOP → 확인·퀴즈를 진행한다 |
| 형식 — 자율학습 | 강사 없이 자기 속도로, 퀴즈로 스스로 점검한다 |

## 원본 강의와 데이터 출처

| 자료 | 출처 | 구분 |
|---|---|---|
| 5일차 본 강의 덱 「자동차 예지보전 AI 활용」 (용어·실습 ③ 전처리·④ 분석 1 프롬프트·실습과제 2 모범답안) | [keerhee/kma-auto-genai-3-1](https://github.com/keerhee/kma-auto-genai-3-1) `Day5_예지보전/` | 강의 자료 |
| 설비 센서 50건 (설비 2대 × 25시점, 진동·온도·압력) | 같은 저장소 `data/Day5/Day5_설비센서_50건_가상.csv` → `assets/lab/sensor_50_virtual.csv` | 가상 데이터(실습용) — 실제 기업 자료 아님 |

## 개정 이력

| 날짜 | 바뀐 점 |
|---|---|
| 2026-10-31 | 첫 판 — 블록 3개, 퀴즈 1문항, 그래프 한 장 |

## 만든 방법

- `/course-forge`로 만들었다. 제작 기록(원본 요약·커리큘럼·검수 결과)은 `forge/`에 있다.
- 출처: 원본 강의 저장소 https://github.com/keerhee/kma-auto-genai-3-1
