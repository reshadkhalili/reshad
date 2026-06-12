"""Hwang In-Beom skill + goal (South Korea, WC2026 game 2) -> 9:16 viral Short.

Source: input4.mp4 (720x1280@30, 24.6s; Verizon outro cut at 19.5).
Base: build/interp50_h.mp4 (50fps). Already vertical: no reframe, only covers.
Output timeline (26.32s):
  p0 hook    0.00- 2.44  src 4.40-5.50 @0.45
  p1 build   2.44- 5.14  src 1.20-3.90
  p2 freeze  5.14- 6.94  still @4.20, ball circled
  p3 move    6.94- 9.64  src 3.90-6.60
  p4 slowmo  9.64-13.42  src 3.90-5.60 @0.45, punch-in
  p5 goal   13.42-17.82  src 8.80-13.20
  p6 after  17.82-24.12  src 13.20-19.50
  p7 q-card 24.12-26.32  still @19.45 (prediction/question close, loops to hook)
"""
import os
import subprocess

BASE = "build/interp50_h.mp4"
SRC = "input4.mp4"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TXT = "build/txt4"
CLIPS = "build/clips4"
os.makedirs(TXT, exist_ok=True)
os.makedirs(CLIPS, exist_ok=True)

ENH = ("scale=1080:1920:flags=lanczos,hqdn3d=1.5:1.0:2.0:2.0,"
       "unsharp=5:5:0.6:5:5:0.3,"
       "curves=master='0/0 0.08/0.05 0.5/0.52 1/1',"
       "vibrance=intensity=0.25,eq=contrast=1.06:saturation=1.12,"
       "vignette=angle=PI/5:mode=backward")
VENC = ["-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p"]

_n = 0


def tf(text):
    global _n
    _n += 1
    p = f"{TXT}/t{_n}.txt"
    with open(p, "w") as f:
        f.write(text)
    return p


def run(args):
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + args, check=True)


run(["-ss", "4.4", "-t", "1.1", "-i", BASE,
     "-vf", f"{ENH},setpts=PTS/0.45,fps=50", "-an"] + VENC + [f"{CLIPS}/p0.mp4"])
run(["-ss", "1.2", "-t", "2.7", "-i", BASE, "-vf", ENH, "-an"] + VENC + [f"{CLIPS}/p1.mp4"])
zp = ("zoompan=z='1+0.06*on/90':"
      "x='min(max(972-(iw/zoom)/2,0),iw-iw/zoom)':"
      "y='min(max(3240-(ih/zoom)/2,0),ih-ih/zoom)':"
      "d=90:s=1080x1920:fps=50")
run(["-i", "build/comp_frz4.png", "-filter_complex", f"[0:v]{zp},format=yuv420p[v]",
     "-map", "[v]", "-frames:v", "90"] + VENC + [f"{CLIPS}/p2.mp4"])
run(["-ss", "3.9", "-t", "2.7", "-i", BASE, "-vf", ENH, "-an"] + VENC + [f"{CLIPS}/p3.mp4"])
# slow-mo punch-in on the move (crop 80% centered on Hwang/ball zone)
run(["-ss", "3.9", "-t", "1.7", "-i", BASE,
     "-vf", f"crop=576:1024:60:200,{ENH},setpts=PTS/0.45,fps=50", "-an"]
    + VENC + [f"{CLIPS}/p4.mp4"])
run(["-ss", "8.8", "-t", "4.4", "-i", BASE, "-vf", ENH, "-an"] + VENC + [f"{CLIPS}/p5.mp4"])
run(["-ss", "13.2", "-t", "6.3", "-i", BASE, "-vf", ENH, "-an"] + VENC + [f"{CLIPS}/p6.mp4"])
zp2 = "zoompan=z='1+0.05*on/110':x='(iw-iw/zoom)/2':y='min(1700-(ih/zoom)/2,ih-ih/zoom)':d=110:s=1080x1920:fps=50"
run(["-i", "build/frz4_end.png", "-filter_complex", f"[0:v]{zp2},format=yuv420p[v]",
     "-map", "[v]", "-frames:v", "110"] + VENC + [f"{CLIPS}/p7.mp4"])

with open("build/list4.txt", "w") as f:
    for i in range(8):
        f.write(f"file '{os.path.abspath(CLIPS)}/p{i}.mp4'\n")
run(["-f", "concat", "-safe", "0", "-i", "build/list4.txt", "-c", "copy",
     f"{CLIPS}/master4.mp4"])

DUR = 26.32


def cap(text, t0, t1, color="white", size=50, y=1190):
    return (f"drawtext=fontfile={FONT}:textfile={tf(text)}:fontsize={size}:expansion=none:"
            f"fontcolor={color}:box=1:boxcolor=black@0.62:boxborderw=14:"
            f"x=(w-text_w)/2:y={y}:enable='between(t,{t0},{t1})'")

texts = [
    (f"drawtext=fontfile={FONT}:textfile={tf('WORLD CUP 2026')}:fontsize=72:expansion=none:"
     "fontcolor=white:box=1:boxcolor=0xC8102E@0.92:boxborderw=20:"
     "x=(w-text_w)/2:y=470:enable='between(t,0.05,2.35)'"),
    (f"drawtext=fontfile={FONT}:textfile={tf('HE FOOLED EVERYONE')}:fontsize=84:expansion=none:"
     "fontcolor=0xFFD400:box=1:boxcolor=black@0.7:boxborderw=20:"
     "x=(w-text_w)/2:y=605:enable='between(t,0.05,2.35)'"),
    cap("SOUTH KOREA — GAME 2", 2.7, 5.0),
    cap("3 DEFENDERS. NO WAY OUT?", 5.2, 6.9, color="0xFFD400", size=56, y=1020),
    cap("ONE TOUCH…", 7.0, 9.5),
    (f"drawtext=fontfile={FONT}:textfile={tf('THE MOVE · 0.45x')}:fontsize=40:expansion=none:"
     "fontcolor=white:box=1:boxcolor=0xC8102E@0.9:boxborderw=14:"
     "x=(w-text_w)/2:y=290:enable='between(t,9.7,13.4)'"),
    cap("HE SELLS THE PASS — THEN HE'S GONE", 9.8, 13.4, color="0xFFD400", size=46),
    cap("AND IT ENDS IN A GOAL", 16.4, 18.4, color="0xFFD400", size=54),
    cap("KOREA LOOK SCARY GOOD", 19.9, 22.7),
    cap("BEST MOVE OF THE CUP — YES OR NO?", 23.0, DUR, color="0xFFD400", size=46, y=1130),
    cap("COMMENT BELOW", 23.4, DUR, size=40, y=1290),
]

vf = (
    # FOX logo: smear + ball badge on top-right
    "[0:v]delogo=x=880:y=135:w=185:h=125[d];"
    "[d][1:v]overlay=822:-33[lg];"
    # previous editor's caption pill: blur + panel, full duration
    "[lg]split[m][m2];[m2]crop=880:240:120:1100,gblur=sigma=30[bl];"
    "[m][bl]overlay=120:1100[cv0];"
    "[cv0]drawbox=x=120:y=1100:w=880:h=240:color=black@0.82:t=fill[cv];"
    "[cv]" + ",".join(texts) + "[vout]"
)

VO = {"L1": 0.15, "L2": 2.60, "L3": 6.30, "L4": 10.0, "L5": 16.4,
      "L6": 20.0, "L7": 23.3}
vo_inputs, vo_filters, vo_tags = [], [], []
for i, (name, at) in enumerate(VO.items()):
    vo_inputs += ["-i", f"build/vo4/{name}.wav"]
    ms = int(at * 1000)
    vo_filters.append(
        f"[{3 + i}:a]atempo=1.05,highpass=f=90,equalizer=f=3500:t=q:w=1.2:g=4,"
        f"equalizer=f=140:t=q:w=1.5:g=2,"
        f"acompressor=threshold=-18dB:ratio=3:attack=5:release=120:makeup=4,"
        f"asoftclip=type=tanh,aformat=channel_layouts=stereo,aresample=44100,"
        f"adelay={ms}|{ms}[vo{i}]")
    vo_tags.append(f"[vo{i}]")

af = (
    f"[2:a]atempo={19.5 / DUR:.4f},lowpass=f=380,"
    f"volume='0.85+0.5*between(t,16.2,20.5)':eval=frame,"
    f"apad,atrim=0:{DUR},afade=t=in:d=0.3,afade=t=out:st={DUR - 1.0}[bed];"
    f"anoisesrc=color=pink:r=44100:amplitude=0.05:d={DUR},"
    "lowpass=f=2200,highpass=f=150,tremolo=f=0.4:d=0.3,"
    "aformat=channel_layouts=stereo,volume=0.5[amb];"
    + ";".join(vo_filters) + ";"
    "[bed][amb]" + "".join(vo_tags) +
    f"amix=inputs={2 + len(VO)}:duration=first:normalize=0,"
    "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[aout]"
)

run([f"-i", f"{CLIPS}/master4.mp4", "-i", "build/ball_logo.png", "-i", SRC]
    + vo_inputs +
    ["-filter_complex", vf + ";" + af,
     "-map", "[vout]", "-map", "[aout]",
     "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
     "-r", "50", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
     "-movflags", "+faststart", "final_hwang_skill_9x16.mp4"])
print("DONE")
