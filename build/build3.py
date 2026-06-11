"""World Cup opener edit: Mexico's first goal (Quinones) -> 9:16 Shorts, v3 pipeline.

Source: input3.mp4 (1276x718 @30fps, 17.5s). Base: build/interp50.mp4 (50fps).
Ball-tracking 9:16 crop (342x608 @ y96) excludes scoreboard + FOX watermark.
Output timeline:
  p0 hook   0.00-2.00   src 6.65-7.55 @0.45 slow-mo
  p1 build  2.00-6.00   src 2.80-6.80 panned
  p2 freeze 6.00-7.50   still @6.80 telestrated
  p3 goal   7.50-8.32   src 6.80-7.62
  p4 celeb  8.32-11.52  src 7.62-10.80
  p5 replay 11.52-13.81 src 6.55-7.58 @0.45 punch-in
  p6 end    13.81-17.59 src 10.80-14.58 (loops back to hook)
"""
import os
import subprocess

BASE = "build/interp50.mp4"
SRC = "input3.mp4"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TXT = "build/txt3"
CLIPS = "build/clips3"
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


def lerp(t0, t1, x0, x1):
    return f"({x0}+({x1}-{x0})*(t-{t0})/({t1}-{t0}))"


# piecewise pan expressions (local clip time)
PAN_BUILD = f"if(lt(t,2.2),{lerp(0,2.2,290,460)},{lerp(2.2,4.0,460,470)})"
PAN_GOAL = (f"if(lt(t,0.3),{lerp(0,0.3,470,520)},"
            f"if(lt(t,0.6),{lerp(0.3,0.6,520,697)},697))")
PAN_HOOK = (f"if(lt(t,0.45),{lerp(0,0.45,480,520)},"
            f"if(lt(t,0.75),{lerp(0.45,0.75,520,697)},697))")
PAN_REPLAY = (f"if(lt(t,0.55),{lerp(0,0.55,505,510)},"
              f"if(lt(t,0.9),{lerp(0.55,0.9,510,715)},715))")

CROP = "crop=342:608:x='{pan}':y=96"
CROP_TIGHT = "crop=306:544:x='{pan}':y=110"

# p0 hook
run(["-ss", "6.65", "-t", "0.9", "-i", BASE,
     "-vf", CROP.format(pan=PAN_HOOK) + f",{ENH},setpts=PTS/0.45,fps=50", "-an"]
    + VENC + [f"{CLIPS}/p0.mp4"])
# p1 build
run(["-ss", "2.8", "-t", "4.0", "-i", BASE,
     "-vf", CROP.format(pan=PAN_BUILD) + f",{ENH}", "-an"] + VENC + [f"{CLIPS}/p1.mp4"])
# p2 freeze still (telestrated comp made separately by make_frz3.py -> comp_frz3.png)
N = 75
zp = ("zoompan=z='1+0.06*on/75':"
      "x='min(max(1040-(iw/zoom)/2,0),iw-iw/zoom)':"
      "y='min(max(1640-(ih/zoom)/2,0),ih-ih/zoom)':"
      "d=75:s=1080x1920:fps=50")
run(["-i", "build/comp_frz3.png", "-filter_complex", f"[0:v]{zp},format=yuv420p[v]",
     "-map", "[v]", "-frames:v", str(N)] + VENC + [f"{CLIPS}/p2.mp4"])
# p3 goal
run(["-ss", "6.8", "-t", "0.82", "-i", BASE,
     "-vf", CROP.format(pan=PAN_GOAL) + f",{ENH}", "-an"] + VENC + [f"{CLIPS}/p3.mp4"])
# p4 celebration
run(["-ss", "7.62", "-t", "3.18", "-i", BASE,
     "-vf", CROP.format(pan="467") + f",{ENH}", "-an"] + VENC + [f"{CLIPS}/p4.mp4"])
# p5 replay (tight punch-in, slowed)
run(["-ss", "6.55", "-t", "1.03", "-i", BASE,
     "-vf", CROP_TIGHT.format(pan=PAN_REPLAY) + f",{ENH},setpts=PTS/0.45,fps=50", "-an"]
    + VENC + [f"{CLIPS}/p5.mp4"])
# p6 end
run(["-ss", "10.8", "-t", "3.78", "-i", BASE,
     "-vf", CROP.format(pan="467") + f",{ENH}", "-an"] + VENC + [f"{CLIPS}/p6.mp4"])

with open("build/list3.txt", "w") as f:
    for i in range(7):
        f.write(f"file '{os.path.abspath(CLIPS)}/p{i}.mp4'\n")
run(["-f", "concat", "-safe", "0", "-i", "build/list3.txt", "-c", "copy",
     f"{CLIPS}/master3.mp4"])


# ---- overlays (output timeline), Shorts-safe zones ----
def cap(text, t0, t1, color="white", size=50, y=1240):
    return (f"drawtext=fontfile={FONT}:textfile={tf(text)}:fontsize={size}:expansion=none:"
            f"fontcolor={color}:box=1:boxcolor=black@0.62:boxborderw=14:"
            f"x=(w-text_w)/2:y={y}:enable='between(t,{t0},{t1})'")

texts = [
    (f"drawtext=fontfile={FONT}:textfile={tf('WORLD CUP 2026')}:fontsize=78:expansion=none:"
     "fontcolor=white:box=1:boxcolor=0xC8102E@0.92:boxborderw=20:"
     "x=(w-text_w)/2:y=470:enable='between(t,0.05,2.0)'"),
    (f"drawtext=fontfile={FONT}:textfile={tf('THE FIRST GOAL')}:fontsize=92:expansion=none:"
     "fontcolor=0xFFD400:box=1:boxcolor=black@0.7:boxborderw=20:"
     "x=(w-text_w)/2:y=610:enable='between(t,0.05,2.0)'"),
    cap("MEXICO vs SOUTH AFRICA", 2.4, 5.8, y=1190),
    cap("WATCH THE RUN…", 4.2, 5.8, y=1300),
    cap("KEEPER'S ALREADY DOWN", 6.0, 7.5, color="0xFFD400", size=58, y=1020),
    cap("QUIÑONES MAKES THEM PAY", 7.55, 9.4, color="0xFFD400", size=54),
    cap("THE FIRST GOAL OF THE TOURNAMENT", 9.6, 11.45, size=46),
    (f"drawtext=fontfile={FONT}:textfile={tf('REPLAY')}:fontsize=40:expansion=none:"
     "fontcolor=white:box=1:boxcolor=0xC8102E@0.9:boxborderw=14:"
     "x=(w-text_w)/2:y=290:enable='between(t,11.52,13.81)'"),
    cap("ONE TOUCH. NO CHANCE.", 11.7, 13.81),
    cap("FOLLOW FOR EVERY WORLD CUP GOAL", 14.2, 17.5, color="0xFFD400", size=46),
]

vf = "[0:v][1:v]overlay=0:0[lg];[lg]" + ",".join(texts) + "[vout]"

# ---- audio ----
VO = {"L1": 0.10, "L2": 2.50, "L3": 6.30, "L4": 7.70, "L5": 9.80,
      "L6": 11.75, "L7": 15.25}
vo_inputs, vo_filters, vo_tags = [], [], []
for i, (name, at) in enumerate(VO.items()):
    vo_inputs += ["-i", f"build/vo3/{name}.wav"]
    ms = int(at * 1000)
    vo_filters.append(
        f"[{3 + i}:a]atempo=1.05,highpass=f=90,equalizer=f=3500:t=q:w=1.2:g=4,"
        f"equalizer=f=140:t=q:w=1.5:g=2,"
        f"acompressor=threshold=-18dB:ratio=3:attack=5:release=120:makeup=4,"
        f"asoftclip=type=tanh,aformat=channel_layouts=stereo,aresample=44100,"
        f"adelay={ms}|{ms}[vo{i}]")
    vo_tags.append(f"[vo{i}]")

af = (
    "[2:a]lowpass=f=380,volume='0.85+0.55*between(t,7.5,12.0)':eval=frame,"
    "apad,atrim=0:17.59,afade=t=out:st=16.7,afade=t=in:d=0.3[bed];"
    "anoisesrc=color=pink:r=44100:amplitude=0.05:d=17.59,"
    "lowpass=f=2200,highpass=f=150,tremolo=f=0.4:d=0.3,"
    "aformat=channel_layouts=stereo,volume=0.5[amb];"
    + ";".join(vo_filters) + ";"
    "[bed][amb]" + "".join(vo_tags) +
    f"amix=inputs={2 + len(VO)}:duration=first:normalize=0,"
    "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[aout]"
)

run([f"-i", f"{CLIPS}/master3.mp4", "-i", "build/ball_logo.png", "-i", SRC]
    + vo_inputs +
    ["-filter_complex", vf + ";" + af,
     "-map", "[vout]", "-map", "[aout]",
     "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
     "-r", "50", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
     "-movflags", "+faststart", "final_wc2026_first_goal_9x16.mp4"])
print("DONE")
