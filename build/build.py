"""Build final_impossible_angles_goalforge_9x16.mp4 from input.mp4.

Output timeline: hook -> 5x (buildup / freeze+telestration / goal / replay) -> CTA.
All clips rendered 1080x1920@30 h264+aac, then concatenated.
"""
import os
import subprocess

SRC = "input.mp4"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TXT = "build/txt"
CLIPS = "build/clips"
VENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p"]
AENC = ["-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2"]

os.makedirs(TXT, exist_ok=True)
os.makedirs(CLIPS, exist_ok=True)

_txt_n = 0


def tf(text):
    """Write text to a file, return drawtext textfile path (avoids escaping)."""
    global _txt_n
    _txt_n += 1
    p = f"{TXT}/t{_txt_n}.txt"
    with open(p, "w") as f:
        f.write(text)
    return p


def header(label, brand="GOALFORGE  |  ANGLE BREAKDOWN"):
    """Banner covering the source's burned-in title (y 250-465, plus zoom drift)."""
    return (
        "drawbox=x=0:y=235:w=1080:h=265:color=black@0.85:t=fill,"
        "drawbox=x=0:y=500:w=1080:h=5:color=0xFFD400:t=fill,"
        f"drawtext=fontfile={FONT}:textfile={tf(brand)}:fontsize=28:expansion=none:"
        "fontcolor=0xFFD400:x=(w-text_w)/2:y=300,"
        f"drawtext=fontfile={FONT}:textfile={tf(label)}:fontsize=54:expansion=none:"
        "fontcolor=white:x=(w-text_w)/2:y=365"
    )


def captions(lines, enable=None):
    """Commentary lines anchored to the bottom area."""
    out = []
    n = len(lines)
    for i, line in enumerate(lines):
        y = 1730 - 85 * (n - i)
        en = f":enable='{enable}'" if enable else ""
        out.append(
            f"drawtext=fontfile={FONT}:textfile={tf(line)}:fontsize=46:expansion=none:"
            f"fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=14:"
            f"x=(w-text_w)/2:y={y}{en}"
        )
    return ",".join(out)


def tag(text, y=1330, color="0xFFD400"):
    """Big yellow analysis tag."""
    return (
        f"drawtext=fontfile={FONT}:textfile={tf(text)}:fontsize=58:expansion=none:"
        f"fontcolor={color}:box=1:boxcolor=black@0.7:boxborderw=20:"
        f"x=(w-text_w)/2:y={y}"
    )


def badge(text):
    """Small red REPLAY badge under the header."""
    return (
        f"drawtext=fontfile={FONT}:textfile={tf(text)}:fontsize=36:expansion=none:"
        "fontcolor=white:box=1:boxcolor=0xC8102E@0.9:boxborderw=14:"
        "x=(w-text_w)/2:y=540"
    )


def run(args):
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + args, check=True)


BASE = "scale=1080:1920:flags=lanczos"
clips = []


def clip(name, args):
    out = f"{CLIPS}/{name}.mp4"
    run(args + [out])
    clips.append(out)
    print(name)


def play(name, ss, t, overlays):
    """Normal-speed source segment with overlays."""
    clip(name, ["-ss", str(ss), "-t", str(t), "-i", SRC,
                "-vf", f"{BASE},fps=30,{overlays}",
                "-af", "aresample=44100"] + VENC + AENC)


def slowmo(name, ss, t, crop, overlays, factor=0.5):
    """Slowed, punched-in replay. crop = (w,h,x,y) in 720x1280 source coords."""
    cw, ch, cx, cy = crop
    setpts = {0.5: "2*PTS", 0.4: "2.5*PTS"}[factor]
    atempo = {0.5: "atempo=0.5", 0.4: "atempo=0.8,atempo=0.5"}[factor]
    clip(name, ["-ss", str(ss), "-t", str(t), "-i", SRC,
                "-vf", f"crop={cw}:{ch}:{cx}:{cy},{BASE},setpts={setpts},fps=30,{overlays}",
                "-af", f"{atempo},aresample=44100"] + VENC + AENC)


def freeze(name, key, dur, overlays):
    """Zoom-in on a composed 2160x3840 still, silent audio."""
    n = int(dur * 30)
    cx2, cy2 = FREEZE_CENTER[key]
    zp = (f"zoompan=z='1+0.06*on/{n}':"
          f"x='min(max({cx2}-(iw/zoom)/2,0),iw-iw/zoom)':"
          f"y='min(max({cy2}-(ih/zoom)/2,0),ih-ih/zoom)':"
          f"d={n}:s=1080x1920:fps=30")
    clip(name, ["-i", f"build/comps/comp_{key}.png",
                "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo",
                "-filter_complex", f"[0:v]{zp},format=yuv420p,{overlays}[v]",
                "-map", "[v]", "-map", "1:a", "-frames:v", str(n)] + VENC + AENC)


# zoom focus per freeze comp, in 2160x3840 coords (2x circle centers).
# cy capped at 1920 so the zoom window's top edge stays at 0 and the source's
# burned-in title never drifts above the header banner.
FREEZE_CENTER = {"5.5": (230, 1770), "15.4": (1824, 1910), "27.2": (1260, 1560),
                 "42.0": (1580, 1920), "55.4": (1280, 1800)}

# ---------------------------------------------------------------- hook (2s)
hook_texts = (
    f"drawbox=x=0:y=0:w=1080:h=1920:color=black@0.35:t=fill,"
    + header("ANGLE BREAKDOWN — TOP 5") + ","
    f"drawtext=fontfile={FONT}:textfile={tf('THESE GOALS')}:fontsize=108:fontcolor=white:"
    f"box=1:boxcolor=black@0.55:boxborderw=18:x=(w-text_w)/2:y=600,"
    f"drawtext=fontfile={FONT}:textfile={tf('SHOULD BE')}:fontsize=108:fontcolor=white:"
    f"box=1:boxcolor=black@0.55:boxborderw=18:x=(w-text_w)/2:y=760,"
    f"drawtext=fontfile={FONT}:textfile={tf('IMPOSSIBLE')}:fontsize=120:fontcolor=white:"
    f"box=1:boxcolor=0xC8102E@0.92:boxborderw=22:x=(w-text_w)/2:y=920,"
    + tag("WAIT FOR #1", y=1430) + ","
    + captions(["These goals should have been impossible."])
)
clip("c00_hook", ["-ss", "56.0", "-t", "1.0", "-i", SRC,
                  "-ss", "7.4", "-t", "2.0", "-i", SRC,
                  "-filter_complex",
                  f"[0:v]{BASE},setpts=2*PTS,fps=30,{hook_texts}[v];"
                  "[1:a]afade=t=in:d=0.15,afade=t=out:st=1.55:d=0.45,aresample=44100[a]",
                  "-map", "[v]", "-map", "[a]"] + VENC + AENC)

# ---------------------------------------------------------------- #5 Lampard
h5 = header("#5 · LAMPARD — 13° ANGLE")
play("c01_intro", 0.5, 5.0,
     h5 + "," + captions(["Every coach says", "don't shoot from here…"],
                         enable="between(t,0,2.6)")
        + "," + captions(["…but these players ignored that."],
                         enable="between(t,2.6,5)"))
cap5 = captions(["Most players cross this.",
                 "Lampard sees the keeper leaning",
                 "and punishes him."])
freeze("c02_frz5", "5.5", 1.4, h5 + "," + tag("99% OF PLAYERS CROSS HERE") + "," + cap5)
play("c03_goal5", 5.5, 3.5, h5 + "," + cap5)
slowmo("c04_rep5", 5.6, 1.7, (540, 960, 40, 250),
       h5 + "," + badge("REPLAY · 0.5x") + ","
       + captions(["Watch the keeper — he's already", "leaning the wrong way."]))

# ---------------------------------------------------------------- #4 Dybala
h4 = header("#4 · DYBALA — 10° ANGLE")
cap4 = captions(["Dybala finds the one angle the",
                 "defender didn't even think existed."])
play("c05_build4", 13.2, 2.2, h4 + "," + cap4)
freeze("c06_frz4", "15.4", 1.4, h4 + "," + tag("NO ANGLE? NO PROBLEM") + "," + cap4)
play("c07_goal4", 15.4, 2.2, h4 + "," + cap4)
play("c08_rep4", 19.85, 2.4,
     h4 + "," + badge("SECOND ANGLE") + ","
     + captions(["Another angle — look how little", "net he actually has."]))

# ---------------------------------------------------------------- #3 Maicon
h3 = header("#3 · MAICON — 6° ANGLE")
cap3 = captions(["This Maicon shot still makes no",
                 "sense. It starts outside the goal",
                 "and bends back in."])
play("c09_build3", 24.6, 2.6, h3 + "," + cap3)
freeze("c10_frz3", "27.2", 1.4, h3 + "," + tag("PHYSICS LEFT THE CHAT") + "," + cap3)
play("c11_goal3", 27.2, 2.1, h3 + "," + cap3)
slowmo("c12_rep3", 26.9, 1.5, (540, 960, 90, 180),
       h3 + "," + badge("REPLAY · 0.5x") + ","
       + captions(["Outside the post… then it bends",
                   "back in. Physics left the chat."]))

# ---------------------------------------------------------------- #2 Areso
h2 = header("#2 · ARESO — 2° ANGLE")
cap2 = captions(["From here the keeper should have",
                 "everything covered… somehow",
                 "Areso still scores."])
play("c13_build2", 39.8, 2.2, h2 + "," + cap2)
freeze("c14_frz2", "42.0", 1.4, h2 + "," + tag("ZERO DEGREES OF SPACE") + "," + cap2)
play("c15_goal2", 42.0, 2.6, h2 + "," + cap2)
slowmo("c16_rep2", 42.0, 1.3, (540, 960, 60, 240),
       h2 + "," + badge("REPLAY · 0.5x") + ","
       + captions(["Near post. Two degrees of angle."]))

# ---------------------------------------------------------------- #1 Carlos
h1 = header("#1 · ROBERTO CARLOS — 1° ANGLE")
play("c17_build1", 53.0, 2.4,
     h1 + "," + captions(["Roberto Carlos from this angle", "is just unfair."]))
cap1 = captions(["Be honest — did he mean this?"])
freeze("c18_frz1", "55.4", 1.6, h1 + "," + tag("DID HE MEAN IT?") + "," + cap1)
play("c19_goal1", 55.4, 3.2, h1 + "," + cap1)
slowmo("c20_rep1", 55.3, 2.0, (540, 960, 90, 200),
       h1 + "," + badge("REPLAY · 0.4x") + ","
       + captions(["No angle. No chance.", "It still goes in."]), factor=0.4)

# ---------------------------------------------------------------- CTA (3s)
cta_n = 90
cta_zp = (f"zoompan=z='1+0.06*on/{cta_n}':x='(iw-iw/zoom)/2':"
          f"y='min(max(1800-(ih/zoom)/2,0),ih-ih/zoom)':"
          f"d={cta_n}:s=1080x1920:fps=30")
cta_texts = (
    "drawbox=x=0:y=0:w=1080:h=1920:color=black@0.55:t=fill,"
    + header("FULL TIME — YOUR VERDICT") + ","
    + f"drawtext=fontfile={FONT}:textfile={tf('WHICH GOAL WAS')}:fontsize=92:fontcolor=white:"
      "x=(w-text_w)/2:y=640,"
    + f"drawtext=fontfile={FONT}:textfile={tf('ACTUALLY THE BEST?')}:fontsize=92:fontcolor=white:"
      "x=(w-text_w)/2:y=770,"
    + tag("COMMENT YOUR #1  ▼", y=1000) + ","
    + f"drawtext=fontfile={FONT}:textfile={tf('FOLLOW FOR MORE ANGLE BREAKDOWNS')}:fontsize=34:"
      "fontcolor=white@0.85:x=(w-text_w)/2:y=1180"
)
clip("c21_cta", ["-i", "build/comps/comp_cta.png",
                 "-ss", "58.5", "-i", SRC,
                 "-filter_complex",
                 f"[0:v]{cta_zp},format=yuv420p,{cta_texts}[v];"
                 "[1:a]apad,atrim=0:3,afade=t=out:st=2.0:d=1.0,aresample=44100[a]",
                 "-map", "[v]", "-map", "[a]", "-frames:v", str(cta_n)] + VENC + AENC)

# ---------------------------------------------------------------- concat
with open("build/list.txt", "w") as f:
    for c in clips:
        f.write(f"file '{os.path.abspath(c)}'\n")

run(["-f", "concat", "-safe", "0", "-i", "build/list.txt",
     "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
     "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
     "-movflags", "+faststart", "final_impossible_angles_goalforge_9x16.mp4"])
print("DONE")
