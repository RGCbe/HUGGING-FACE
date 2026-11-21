"""Talking shots with real lip-sync: each shot marked "lipsync" in all_shots.json gets its approved start picture
and its voice line made into a 5-second clip by LongCat-Video-Avatar 1.6 on the owner's own private Space
(space_app.py switches the Space to that app first). Uses his PRO daily GPU time; stops when it runs low and
carries on the next day (clips that exist are kept).

    python3 lipsync_clips.py EPISODE_DIR [--only S11,S17] [--redo]

The voice line goes in 0.3 s after the clip starts, the same place edit.py puts it in the shot, so the lips match
when the clip starts with the shot. Output: EPISODE_DIR/out/clips/SNN_lip.mp4 (edit.py uses it before SNN_a.mp4,
without any speed change); the raw clip stays in out/clips_raw/. Every call goes to EPISODE_DIR/out/clips/lipsync_log.jsonl.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import space_app  # noqa: E402

LEAD, CLIP_S = 0.3, 5.0
NEED_S = 210  # GPU seconds one call may take (the app asks for 200 on half a GPU)
WHO = {"arjun": "the young man in the white kurta", "viktor": "the blonde man in silver armor",
       "meera": "the young woman in the white robe", "raghu": "the huge bald bearded man"}


def prompt_for(s):
    speaker = s["line"][0]
    how = s.get("tag", "").strip("[] ")
    people = [c for c in s.get("cast", []) if c in WHO]
    p = (f"{s['see']}. {WHO[speaker][0].upper() + WHO[speaker][1:]} is talking{', ' + how if how else ''}, "
         f"with natural lip movement, an expressive face and small natural head movements; {s['motion']}. ")
    if len(people) > 1:
        p += "Only he speaks; the others stay silent. " if speaker != "meera" else "Only she speaks; the others stay silent. "
    return p + ("Photorealistic live-action film, real actors, cinematic lighting, anamorphic film look. Keep every "
                "face, costume and the setting exactly as in the picture.")


def driving_audio(voice, out):
    """The voice line 0.3 s in, padded with silence to the clip length, 16 kHz mono."""
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", voice, "-af",
                    f"adelay=delays={int(LEAD * 1000)}:all=1,apad=whole_dur={CLIP_S}", "-ac", "1", "-ar", "16000",
                    "-t", str(CLIP_S), out], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--only")
    ap.add_argument("--redo", action="store_true", help="make the clip again even if it exists")
    a = ap.parse_args()
    ep = os.path.abspath(a.episode)
    only = set(a.only.split(",")) if a.only else None
    flags = {s["id"]: s for s in json.load(open(os.path.join(ep, "all_shots.json")))}
    shots = json.load(open(os.path.join(ep, "shots.json")))["shots"]
    clips, raw_dir = os.path.join(ep, "out", "clips"), os.path.join(ep, "out", "clips_raw")
    os.makedirs(clips, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)
    todo = []
    for s in shots:
        if not flags.get(s["id"], {}).get("lipsync") or (only and s["id"] not in only):
            continue
        if os.path.exists(os.path.join(clips, f"{s['id']}_lip.mp4")) and not a.redo:
            continue
        voice = os.path.join(ep, "voice", f"{s['id']}.wav")
        img = os.path.join(ep, "out", "keyframes_ok", flags[s["id"]]["image"])
        if not (os.path.exists(voice) and os.path.exists(img)):
            print(f"{s['id']}: no voice line or picture, skipped")
            continue
        todo.append((s, voice, img))
    print(f"{len(todo)} talking clips to make", flush=True)
    if not todo:
        return
    from gradio_client import Client, handle_file
    from huggingface_hub import get_zero_gpu_quota
    token = os.environ["HF_TOKEN"]
    left = get_zero_gpu_quota(token=token).remaining
    if left < NEED_S:
        print(f"free GPU time used up for today ({left:.0f} s left). Run again tomorrow.")
        return
    space_app.use("longcat")
    client = Client(space_app.SPACE, token=token, verbose=False)
    log = open(os.path.join(clips, "lipsync_log.jsonl"), "a")
    made = fails = 0
    tmp = os.path.join(raw_dir, "_driving.wav")
    for s, voice, img in todo:
        if fails >= 2:
            print(f"two failures in a row: stopping after {made} clips")
            break
        left = get_zero_gpu_quota(token=token).remaining
        if left < NEED_S:
            print(f"free GPU time used up for today after {made} clips ({left:.0f} s left). Run again tomorrow.")
            break
        t = time.time()
        prompt = prompt_for(s)
        rec = {"name": f"{s['id']}_lip", "prompt": prompt, "seed": 42}
        driving_audio(voice, tmp)
        try:
            try:
                r = client.predict(handle_file(img), handle_file(tmp), prompt, "480p", 42, True, api_name="/talk")
            except Exception as e:  # noqa: BLE001
                if "memory" not in str(e).lower():
                    raise
                print(f"{s['id']}: half a GPU ran out of memory, trying the full GPU", flush=True)
                rec["xl"] = True
                r = client.predict(handle_file(img), handle_file(tmp), prompt, "480p", 42, True, api_name="/talk_xl")
            video = r["video"] if isinstance(r, dict) else r
            raw = os.path.join(raw_dir, f"{s['id']}_lip.mp4")
            shutil.copy(video, raw)
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", raw, "-an", "-c:v", "copy",
                            os.path.join(clips, f"{s['id']}_lip.mp4")], check=True)
            made += 1
            fails = 0
            rec.update(ok=True, took_s=round(time.time() - t),
                       gpu_s=round(left - get_zero_gpu_quota(token=token).remaining))
            print(f"{s['id']}_lip: made in {time.time() - t:.0f} s ({rec['gpu_s']} s of GPU time)", flush=True)
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            rec.update(ok=False, error=msg[:500])
            if "quota" in msg.lower() or "exceeded" in msg.lower():
                log.write(json.dumps(rec) + "\n")
                print(f"free GPU time used up for today after {made} clips. Run again tomorrow.")
                break
            print(f"{s['id']}_lip: FAILED - {msg[:300]}", flush=True)
            fails += 1
        log.write(json.dumps(rec) + "\n")
        log.flush()
    if os.path.exists(tmp):
        os.remove(tmp)
    print(f"done: {made} of {len(todo)} talking clips made")


if __name__ == "__main__":
    main()
