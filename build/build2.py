"""Heavy re-edit of input2.mp4 (Kane impossible-angle goal) -> Shorts-ready video.

- Upscale 720x1280 -> 1080x1920 with denoise/sharpen/color boost
- Freeze frame before the goal, endcard after
- Original broadcast audio muted; replaced with crowd rumble + new VO (Piper TTS)
- Bundesliga logo covered by drawn football badge; burned 'THIS ANGLE' caption blurred
- Synced sports captions on the new commentary
"""
import os
import subprocess

SRC = "input2.mp4"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TXT = "build/txt2"
os.makedirs(TXT, exist_ok=True)
os.makedirs("build/clips2", exist_ok=True)

ENH = ("scale=1080:1920:flags=lanczos,hqdn3d=1.5:1.0:2.0:2.0,"
       "unsharp=5:5:0.7:5:5:0.35,eq=contrast=1.05:saturation=1.16")
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


# ---- still frames for freeze + endcard (enhanced, 2x for clean zoompan) ----
ENH2X = ENH.replace("1080:1920", "2160:3840")
run(["-ss", "7.5", "-i", SRC, "-vf", ENH2X, "-frames:v", "1", "build/clips2/frz.png"])
run(["-ss", "15.68", "-i", SRC, "-vf", ENH2X, "-frames:v", "1", "build/clips2/end.png"])

# ---- video parts (silent) ----
run(["-ss", "0", "-t", "7.5", "-i", SRC, "-vf", ENH, "-an"] + VENC + ["build/clips2/pA.mp4"])

zp_f = ("zoompan=z='1+0.07*on/30':x='min(max(1760-(iw/zoom)/2,0),iw-iw/zoom)':"
        "y='min(max(1600-(ih/zoom)/2,0),ih-ih/zoom)':d=30:s=1080x1920:fps=25")
run(["-i", "build/clips2/frz.png", "-filter_complex", f"[0:v]{zp_f},format=yuv420p[v]",
     "-map", "[v]", "-frames:v", "30"] + VENC + ["build/clips2/pF.mp4"])

run(["-ss", "7.5", "-t", "3.2", "-i", SRC, "-vf", ENH, "-an"] + VENC + ["build/clips2/pB.mp4"])
run(["-ss", "10.7", "-i", SRC, "-vf", ENH, "-an"] + VENC + ["build/clips2/pC.mp4"])

zp_e = "zoompan=z='1+0.05*on/40':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=40:s=1080x1920:fps=25"
run(["-i", "build/clips2/end.png", "-filter_complex", f"[0:v]{zp_e},format=yuv420p[v]",
     "-map", "[v]", "-frames:v", "40"] + VENC + ["build/clips2/pE.mp4"])

with open("build/list2.txt", "w") as f:
    for p in ["pA", "pF", "pB", "pC", "pE"]:
        f.write(f"file '{os.path.abspath('build/clips2/' + p + '.mp4')}'\n")
run(["-f", "concat", "-safe", "0", "-i", "build/list2.txt", "-c", "copy",
     "build/clips2/master_silent.mp4"])

# output timeline: A 0-7.5 | freeze 7.5-8.7 | B 8.7-11.9 | C 11.9-16.96 | end 16.96-18.56

# ---- overlay text plan ----
def cap(text, t0, t1, color="white", size=54, y=1430):
    return (f"drawtext=fontfile={FONT}:textfile={tf(text)}:fontsize={size}:expansion=none:"
            f"fontcolor={color}:box=1:boxcolor=black@0.65:boxborderw=16:"
            f"x=(w-text_w)/2:y={y}:enable='between(t,{t0},{t1})'")

texts = [
    # hook
    (f"drawtext=fontfile={FONT}:textfile={tf('HE SCORED FROM HERE?!')}:fontsize=72:"
     "expansion=none:fontcolor=white:box=1:boxcolor=0xC8102E@0.92:boxborderw=22:"
     "x=(w-text_w)/2:y=560:enable='between(t,0.2,2.4)'"),
    cap("BAYERN BREAK AT SPEED", 0.5, 3.2),
    cap("THE ONE SPOT NOBODY SHOOTS FROM", 3.2, 6.7, size=48),
    cap("NO ANGLE. NO SPACE.", 7.5, 8.7, color="0xFFD400", size=64, y=1330),
    cap("HE FINDS THE ROOF OF THE NET", 8.8, 10.6, color="0xFFD400", size=50),
    cap("ARE YOU SERIOUS?!", 10.6, 11.9, size=60),
    (f"drawtext=fontfile={FONT}:textfile={tf('REPLAY — THE ANGLE')}:fontsize=40:"
     "expansion=none:fontcolor=white:box=1:boxcolor=0xC8102E@0.9:boxborderw=14:"
     "x=(w-text_w)/2:y=250:enable='between(t,11.9,16.9)'"),
    cap("WATCH THE ANGLE AGAIN", 12.0, 14.4, y=1410),
    cap("THIS SHOULD NOT BE POSSIBLE", 14.5, 16.9, color="0xFFD400", size=50, y=1410),
    # endcard
    ("drawbox=x=0:y=0:w=1080:h=1920:color=black@0.55:t=fill:enable='gte(t,16.96)'"),
    (f"drawtext=fontfile={FONT}:textfile={tf('FOLLOW FOR MORE')}:fontsize=88:"
     "expansion=none:fontcolor=white:x=(w-text_w)/2:y=830:enable='gte(t,17.1)'"),
    (f"drawtext=fontfile={FONT}:textfile={tf('INSANE FINISHES · DAILY')}:fontsize=46:"
     "expansion=none:fontcolor=0xFFD400:x=(w-text_w)/2:y=980:enable='gte(t,17.1)'"),
]

vf = (
    # smear the source logo, then place our ball badge over it
    "[0:v]delogo=x=40:y=150:w=200:h=170[d];"
    "[d][1:v]overlay=0:0[lg];"
    # blur + darken the burned 'THIS ANGLE' caption (measured: x268-845, y1407-1514)
    "[lg]split[m][m2];[m2]crop=660:175:230:1375,gblur=sigma=35[bl];"
    "[m][bl]overlay=230:1375:enable='between(t,11.8,16.96)'[cv0];"
    "[cv0]drawbox=x=230:y=1375:w=660:h=175:color=black@0.85:t=fill:"
    "enable='between(t,11.8,16.96)'[cv];"
    "[cv]" + ",".join(texts) + "[vout]"
)

# ---- audio: crowd rumble bed + pink-noise ambience + VO lines ----
VO = {"L1": 0.50, "L2": 7.55, "L3": 9.45, "L4": 13.0, "L5": 14.9, "L6": 17.15}
vo_inputs, vo_filters, vo_tags = [], [], []
for i, (name, at) in enumerate(VO.items()):
    vo_inputs += ["-i", f"build/vo/{name}.wav"]
    ms = int(at * 1000)
    vo_filters.append(f"[{3 + i}:a]aresample=44100,aformat=channel_layouts=stereo,"
                      f"adelay={ms}|{ms},volume=1.0[vo{i}]")
    vo_tags.append(f"[vo{i}]")

af = (
    # bed: original audio split to match the edited timeline, voice band removed
    "[2:a]asplit=3[b1][b2][b3];"
    "[b1]atrim=0:7.56[s1];"
    "[b2]atrim=6.34:7.56,asetpts=PTS-STARTPTS[s2];"
    "[b3]atrim=7.44:15.74,asetpts=PTS-STARTPTS[s3];"
    "[s1][s2]acrossfade=d=0.06[s12];"
    "[s12][s3]acrossfade=d=0.06[bedraw];"
    "[bedraw]lowpass=f=380,volume='0.9+0.5*between(t,8.6,12.2)':eval=frame,"
    "apad,atrim=0:18.56,afade=t=out:st=17.4:d=1.1[bed];"
    # synthetic crowd hiss to mask seams
    "anoisesrc=color=pink:r=44100:amplitude=0.05:d=18.56,"
    "lowpass=f=2200,highpass=f=150,tremolo=f=0.4:d=0.3,"
    "aformat=channel_layouts=stereo,volume=0.5[amb];"
    + ";".join(vo_filters) + ";"
    "[bed][amb]" + "".join(vo_tags) +
    f"amix=inputs={2 + len(VO)}:duration=first:normalize=0,"
    "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[aout]"
)

run(["-i", "build/clips2/master_silent.mp4", "-i", "build/ball_logo.png",
     "-i", SRC] + vo_inputs +
    ["-filter_complex", vf + ";" + af,
     "-map", "[vout]", "-map", "[aout]",
     "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
     "-r", "25", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
     "-movflags", "+faststart", "final_kane_angle_edit_9x16.mp4"])
print("DONE")
