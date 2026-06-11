# GOALFORGE v3 — Shorts Edit Pipeline (locked plan)

Target: transformative football analysis Shorts, 1080x1920, retention-optimized,
clean for YPP human review. One pipeline run per source clip.

## 1. Safe-zone layout (fixes the Kane caption problem)

YouTube Shorts UI covers the bottom ~480px (title/channel/audio) and the right
~140px rail (like/comment/share, y≈900–1700). Nothing readable goes there.

| Element            | Position (1080x1920)         |
|--------------------|------------------------------|
| Hook text (0–2s)   | y 480–660, centered          |
| Header/brand band  | y 235–500 ONLY when covering a burned-in source title |
| REPLAY badge       | y 290, centered              |
| Analysis tag       | y 1020–1100, centered        |
| Commentary captions| y 1180–1400, max 2 compact lines, centered, x kept < 920 |
| Nothing            | y > 1440, x > 940            |

Text discipline: center of frame stays clear; captions are a compact lower-third
strip, not screen-filling boxes.

## 2. Picture pipeline (in order, at source resolution first)

1. `minterpolate` 25/30 → 50fps (mci/aobmc/bidir) — ~5 min per 15s clip; QA for
   warping, drop if artifacts.
2. Upscale to 1080x1920 lanczos.
3. Grade: `hqdn3d` light denoise → `unsharp` → curves (crushed blacks),
   `vibrance` (grass + jerseys), `eq` contrast, subtle `vignette`.
4. Crop discipline: every shot framed to exclude scoreboard/clock/broadcaster
   watermark where possible (suspense + cleanliness). Source watermark that
   can't be cropped gets delogo + ball badge.
5. Cut pacing: no single angle > 2s — alternate full frame / punch-in crop /
   freeze. Freeze-frame telestration (circle/arrow) before each key moment.
6. Slow-mo replay (0.4–0.5x) with punch-in on the money shot.
7. Loop engineering: video ends on high-momentum action frame that cuts cleanly
   back to the opening hook frame. NO endcard — follow CTA is a caption line
   near the end instead.

## 3. Audio pipeline

1. Original broadcast audio: never used raw. Crowd bed = source audio
   lowpass 380Hz (kills voice intelligibility, keeps roar dynamics) + pink-noise
   stadium ambience layer.
2. VO: Piper `en-us-libritts-high`, **speaker 66** (locked channel voice,
   male/American). Delivery per line: `length_scale` 0.85 + `noise_scale` 0.55
   for goal/eruption lines, 0.93/0.667 for buildup and analysis lines. Script
   written with contractions and short exclamatory clauses.
3. Broadcast-mic chain on VO: atempo 1.05 → highpass 90 → presence EQ +4dB@3.5k
   → +2dB@140 → compressor 3:1 → soft clip → over the ducked bed.
4. Optional music mode: ONLY claim-safe tracks supplied by user (YouTube Audio
   Library or licensed). Cuts beat-synced to onsets.
5. Master: amix → loudnorm I=-14 TP=-1.5 → limiter. AAC 192k 44.1k stereo.

## 4. Script rules (commentary)

- Mine the original commentary/captions for the core idea, then write fresh.
- Structure: cold-open question/claim → context line → tension line at freeze →
  eruption on the goal → analysis line on replay → engagement question at end.
- Every line timed to a visual beat; captions condense VO, never transcribe it.

## 5. Per-video process checklist

1. Probe (res/fps/duration) → contact sheets → map segments, goal frames, logos,
   burned-in text (measure pixel bounds programmatically).
2. Attempt transcript of source commentary for ideas.
3. Write script + caption set + timeline (output timeline math).
4. Generate VO lines, measure durations, lock timings.
5. Render parts → concat → final overlay+audio pass.
6. QA: frame strip at every text window, safe-zone check, cover checks
   (logo/burned text), volumedetect, duration/fps/size.
7. Deliver full-quality + small mobile preview; commit + push.

## 6. Export

H.264 high quality (CRF 15–17, preset slow), yuv420p, 50fps (interpolated) or
source fps, faststart. Duration target 15–35s.

## Honest constraints (do not promise the user otherwise)

- No edit prevents Content ID visual matching; transformation wins the human
  YPP review and dispute posture, not the matcher.
- Fresh World Cup footage carries manual-strike risk regardless of edit quality.
- Local TTS ≈ near-natural, not guaranteed indistinguishable from human.
