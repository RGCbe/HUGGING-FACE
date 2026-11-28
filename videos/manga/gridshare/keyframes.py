"""Make an episode's keyframes on a rented GridShare GPU, from its shot list, and bring them back.

    python3 keyframes.py prompts SHOTS.json                 write SHOTS_dir/keyframes_job.json (the prompts) and print one
    python3 keyframes.py run SHOTS.json OUT_DIR [--only S05,S09] [--takes 2] [--node ID] [--max-min 90]
    python3 keyframes.py attach INSTANCE_ID OUT_DIR --run RUN_ID     follow (and finally delete) a running machine

run: uploads the job, the cast face files and the machine scripts to the private drop box (dropbox.py), rents one
machine (gpu_count 1, image gridshare/pytorch) whose GRIDSHARE_START_CMD runs boot.sh, follows its progress, saves
every picture to OUT_DIR as it arrives, and ALWAYS deletes the machine at the end (done, error, no progress for 20
minutes, or --max-min). Needs the GridShare key saved for gridshare.in (the proxy adds it) and CF_* for the drop box.

Prompt rules come from the shot list's "rules" and the director's log (LOG.md): one face file per character as a
reference picture, Indian street details for Mumbai, signs kept unreadable, the dungeon darker.
"""
import argparse
import json
import signal
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dropbox  # noqa: E402

GS = "https://gridshare.in"
STYLE = ("Photorealistic cinematic film still from a big-budget superhero blockbuster, real people, natural realistic skin "
         "and hair, correct human anatomy with five fingers on each hand, anamorphic widescreen movie look, vivid colours, "
         "warm golden key light and teal shadows, crisp detail, shallow depth of field.")
DARK = " This scene is darker: low-key light, deep shadows, lit only by torches and magic light."
STREET = (" Indian street details: strings of marigold flowers, small oil lamps, brass pots, Indian shop fronts; any shop "
          "signs are dark or out of focus so no writing can be read.")
EVENING = " Time: evening after sunset, deep blue sky, all the oil lamps and string lights are lit, warm lamp light on the faces."
NIGHT = " Time: late night, black sky, the plaza lit only by small oil lamps and the blue glow of the Gate."
WHO = {
    "arjun": "Arjun, a young Indian man of 18 with a youthful clean-shaven face, messy short black hair and dark brown skin, "
             "wearing a white collarless cotton kurta with the sleeves rolled up, a red cloth sash at his waist and a red "
             "string bracelet",
    "viktor": "Viktor, a 28-year-old Western man with short slicked-back blonde hair and blue eyes, wearing silver plate "
              "armor with steel gauntlets and a black cape fastened with round silver clasps, no glasses",
    "meera": "Meera, a young Indian woman of 22 with one long black braid, wearing a white robe with gold trim, carrying a "
             "tall carved wooden staff topped with a small green crystal",
    "raghu": "Raghu, a huge bald Indian man of 35 with a thick black beard, wearing dark steel armor, with a tall "
             "rectangular steel tower shield held by a handle on his left arm",
    "ogre": "the ogre, a huge hairy monster three times a man's height with a butcher's cleaver",
    "minotaur": "the minotaur boss, a giant bull-headed monster in black armor with a huge axe and glowing red eyes",
}
CREATURES = {"ogre", "minotaur"}
DUNGEON_SCENES = {1, 7, 8, 9}
STREET_SCENES = {3, 4, 5, 10, 11, 12}


def prompt(shot):
    text = f"{STYLE} Film still: {shot['see']}."
    for i, who in enumerate(shot.get("cast", [])):
        if who in CREATURES:
            text += f" {WHO[who]}: the same creature as in image {i}."
        else:
            text += f" {WHO[who]}; {who.capitalize()} is the person in image {i}, with exactly the same face."
    if shot["scene"] in DUNGEON_SCENES:
        text += DARK
    if shot["scene"] in STREET_SCENES:
        text += STREET
    if shot["scene"] in (3, 4, 5):
        text += EVENING
    if shot["scene"] in (10, 11, 12, 13):
        text += NIGHT
    return text


def job_for(shots_file, only=None, takes=2):
    d = json.load(open(shots_file))
    images = []
    for s in d["shots"]:
        if s.get("kind") != "ai" or (only and s["id"] not in only):
            continue
        for k in range(takes):
            images.append({"name": f"{s['id']}_{'abc'[k]}", "seed": 1 + k, "prompt": prompt(s), "refs": s.get("cast", [])})
    cast = sorted({c for im in images for c in im["refs"]})
    return {"model": "black-forest-labs/FLUX.2-klein-4B", "width": 1664, "height": 928, "steps": 4, "cast": cast,
            "images": images}, os.path.join(os.path.dirname(os.path.abspath(shots_file)), "..", "..", "cast")


def gs(method, path, body=None):
    req = urllib.request.Request(GS + path, data=json.dumps(body).encode() if body else None, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            b = r.read()
            return json.loads(b) if b.strip() else {}
    except urllib.error.HTTPError as e:  # say GridShare's reason (e.g. "the machine is fully rented")
        sys.exit(f"GridShare {method} {path}: HTTP {e.code} {e.read()[:400].decode('utf-8', 'replace')}")


def run(a):
    only = set(a.only.split(",")) if a.only else None
    job, cast_dir = job_for(a.shots, only, a.takes)
    os.makedirs(a.out_dir, exist_ok=True)
    todo = [im for im in job["images"] if not os.path.exists(os.path.join(a.out_dir, im["name"] + ".jpg"))]
    if not todo:
        print("every picture is already in", a.out_dir)
        return
    job["images"] = todo
    run_id = time.strftime("%Y%m%d-%H%M%S")
    print(f"{len(todo)} pictures, cast {job['cast']}, run {run_id}")
    # a fresh run folder in the drop box, so an old DONE or old pictures are never mistaken for this run's
    for name in ("job.json",):
        dropbox.put(f"{run_id}/{name}", json.dumps(job).encode(), "application/json")
    for c in job["cast"]:
        dropbox.put(f"{run_id}/cast/{c}.jpg", open(os.path.join(cast_dir, f"{c}.jpg"), "rb").read(), "image/jpeg")
    for f in ("boot.sh", "keyframes_worker.py"):
        dropbox.put(f"{run_id}/{f}", open(os.path.join(HERE, f), "rb").read())
    # the machine sees only this run's folder: DROP_URL/NAME is the drop box's file RUN_ID/NAME
    env = {"DROP_URL": f"{dropbox.base()}/files/{run_id}", "NVIDIA_DRIVER_CAPABILITIES": "all",
           "GRIDSHARE_START_CMD": "bash -c 'curl -fsS -A gs-machine \"$DROP_URL/boot.sh\" | bash'"}
    body = {"image": "gridshare/pytorch:latest", "label": "flux-keyframes", "gpu_count": 1, "disk_gb": 60,
            "job_type": "ondemand", "exposed_ports": [], "env": env, "reliability_tier": "bronze",
            # keep /workspace (the model is in /workspace/models) so the next machine starts with it
            "workspace_save": True, "workspace_private_models": True}
    if a.restore:  # start from the files saved by an earlier machine (its /workspace/models has the model)
        body["restore_from_instance_id"] = a.restore
    # GridShare picks the machine by size when min_vram_gb is sent, even with a node_id (it once gave us an Apple
    # M3 Max that cannot run CUDA): send only the node_id, like GridShare's own SDK, and check what we got
    if a.node:
        body["node_id"] = body["preferred_node_id"] = a.node
    else:
        body["min_vram_gb"] = a.min_vram
    inst = gs("POST", "/v1/instances/", body)
    iid = inst["id"]
    print(f"machine {iid[:8]} {inst.get('status')} at ₹{inst.get('rate_per_hr_inr')}/hour, run {run_id}", flush=True)
    if a.max_rate and (inst.get("rate_per_hr_inr") or 0) > a.max_rate:
        print(f"rate ₹{inst.get('rate_per_hr_inr')} is above --max-rate {a.max_rate}: stopping")
        return delete(iid, run_id, a.out_dir, set())
    got = (gs("GET", f"/v1/instances/{iid}").get("node_id") or "")
    if a.node and got != a.node:
        print(f"GridShare gave machine {got[:8]}, not the chosen {a.node[:8]}: stopping")
        return delete(iid, run_id, a.out_dir, set())
    watch(iid, run_id, a.out_dir, a.max_min)


def watch(iid, run_id, out_dir, max_min, stall_min=25):
    """Follow a running machine: print its progress, save its pictures, and ALWAYS delete it at the end."""
    os.makedirs(out_dir, exist_ok=True)
    t0 = last_change = time.time()
    seen = {f for f in os.listdir(out_dir) if f.endswith((".jpg", ".mp4"))}
    last_status, finished = "", False
    try:
        while time.time() - t0 < max_min * 60 and time.time() - last_change < stall_min * 60:
            time.sleep(30)
            status = (dropbox.get(f"{run_id}/out/status.txt") or b"").decode("utf-8", "replace")
            if status != last_status:
                new = status[len(last_status):] if status.startswith(last_status) else status
                print(new.strip()[-1500:], flush=True)
                last_status, last_change = status, time.time()
            for name in dropbox.names(f"{run_id}/out/"):
                short = name.split("/out/", 1)[1]
                if short.endswith((".jpg", ".mp4")) and short not in seen:
                    open(os.path.join(out_dir, short), "wb").write(dropbox.get(name))
                    seen.add(short)
            if dropbox.get(f"{run_id}/out/DONE") or "ALL DONE" in status or "STOPPED WITH AN ERROR" in status:
                finished = True
                break
            st = gs("GET", f"/v1/instances/{iid}")
            if st.get("status") in ("error", "stopped"):
                print("the machine stopped by itself:", st.get("status"), st.get("error_msg") or st.get("display_message"))
                break
        if not finished:
            print("stopping: " + ("time limit" if time.time() - t0 >= max_min * 60 else f"no progress for {stall_min} minutes"))
    finally:
        delete(iid, run_id, out_dir, seen)


def delete(iid, run_id, out_dir, seen):
    """Stop the machine (billing ends; its saved /workspace, with the model, stays for the next one).
    If stopping fails, delete it, so it never keeps running."""
    try:
        gs("POST", f"/instances/{iid}/stop")
        print(f"machine stopped (files kept; next time: --restore {iid})", flush=True)
    except Exception as e:  # noqa: BLE001
        print("stop failed, deleting instead:", e, flush=True)
        try:
            gs("DELETE", f"/v1/instances/{iid}")
            print("machine deleted", flush=True)
        except Exception as e2:  # noqa: BLE001
            print("DELETE FAILED, delete it in the GridShare app:", iid, e2, flush=True)
    time.sleep(15)
    try:
        st = gs("GET", f"/v1/instances/{iid}")
        print(f"final: {st.get('status')}, ran {st.get('running_seconds')} s, cost ₹{st.get('total_cost_inr')}")
    except Exception:  # noqa: BLE001
        pass
    log = dropbox.get(f"{run_id}/out/run.log")
    if log:
        open(os.path.join(out_dir, f"run_{run_id}.log"), "wb").write(log)
    print(f"{len(seen)} files in {out_dir}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prompts", "run", "attach"])
    ap.add_argument("shots")
    ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--only")
    ap.add_argument("--takes", type=int, default=2)
    ap.add_argument("--node")
    ap.add_argument("--min-vram", type=float, default=23)
    ap.add_argument("--max-rate", type=float, default=35)
    ap.add_argument("--max-min", type=float, default=90)
    ap.add_argument("--run", help="attach: the run id")
    ap.add_argument("--stall", type=float, default=25, help="end the machine after this many minutes without progress")
    ap.add_argument("--restore", help="start from this stopped machine's saved files (the model)")
    a = ap.parse_args()
    signal.signal(signal.SIGTERM, lambda *_: sys.exit("terminated"))  # so the machine is still deleted (finally)
    if a.cmd == "prompts":
        job, _ = job_for(a.shots, set(a.only.split(",")) if a.only else None, a.takes)
        out = os.path.join(os.path.dirname(os.path.abspath(a.shots)), "keyframes_job.json")
        json.dump(job, open(out, "w"), indent=1, ensure_ascii=False)
        print(f"{len(job['images'])} pictures, cast {job['cast']} -> {out}\n\nexample:\n{job['images'][0]['prompt']}")
    elif a.cmd == "attach":  # keyframes.py attach INSTANCE_ID OUT_DIR --run RUN_ID
        watch(a.shots, a.run, a.out_dir, a.max_min, a.stall)
    else:
        run(a)
