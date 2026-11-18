"""Make an episode's keyframes on a rented GridShare GPU, from its shot list, and bring them back.

    python3 keyframes.py prompts SHOTS.json                 write SHOTS_dir/keyframes_job.json (the prompts) and print one
    python3 keyframes.py run SHOTS.json OUT_DIR [--only S05,S09] [--takes 2] [--node ID] [--max-min 90]

run: uploads the job, the cast face files and the machine scripts to the private drop box (dropbox.py), rents one
machine (gpu_count 1, image gridshare/pytorch) whose GRIDSHARE_START_CMD runs boot.sh, follows its progress, saves
every picture to OUT_DIR as it arrives, and ALWAYS deletes the machine at the end (done, error, no progress for 20
minutes, or --max-min). Needs the GridShare key saved for gridshare.in (the proxy adds it) and CF_* for the drop box.

Prompt rules come from the shot list's "rules" and the director's log (LOG.md): one face file per character as a
reference picture, Indian street details for Mumbai, signs kept unreadable, the dungeon darker.
"""
import argparse
import json
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
DARK = " This scene is darker: low-key light, deep shadows, only torches, glowing mushrooms or magic light."
STREET = (" Indian street details: strings of marigold flowers, small oil lamps, brass pots, Indian shop fronts; any shop "
          "signs are dark or out of focus so no writing can be read.")
WHO = {
    "arjun": "Arjun, a young Indian man of 18 with a youthful clean-shaven face, messy short black hair and dark brown skin, "
             "wearing a white collarless cotton kurta with the sleeves rolled up, a red cloth sash at his waist and a red "
             "string bracelet",
    "viktor": "Viktor, a 28-year-old Western man with short slicked-back blonde hair and blue eyes, wearing silver plate "
              "armor with steel gauntlets and a black cape fastened with round silver clasps",
    "meera": "Meera, a young Indian woman of 22 with one long black braid, wearing a white robe with gold trim, carrying a "
             "tall carved wooden staff topped with a small green crystal",
    "raghu": "Raghu, a huge bald Indian man of 35 with a thick black beard, wearing dark steel armor, with a tall "
             "rectangular steel tower shield held by a handle on his left arm",
}
DUNGEON_SCENES = {1, 7, 8, 9}
STREET_SCENES = {3, 4, 5, 10, 11, 12}


def prompt(shot):
    text = f"{STYLE} Film still: {shot['see']}."
    for i, who in enumerate(shot.get("cast", [])):
        text += f" {WHO[who]}; {who.capitalize()} is the person in image {i}, with exactly the same face."
    if shot["scene"] in DUNGEON_SCENES:
        text += DARK
    if shot["scene"] in STREET_SCENES:
        text += STREET
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
    with urllib.request.urlopen(req, timeout=90) as r:
        b = r.read()
        return json.loads(b) if b.strip() else {}


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
    body = {"image": "gridshare/pytorch:latest", "label": "keyframes", "gpu_count": 1, "min_vram_gb": a.min_vram,
            "disk_gb": 60, "job_type": "ondemand", "exposed_ports": [], "env": env}
    if a.node:
        body["node_id"] = a.node
    inst = gs("POST", "/v1/instances/", body)
    iid = inst["id"]
    print(f"machine {iid[:8]} {inst.get('status')} at ₹{inst.get('rate_per_hr_inr')}/hour", flush=True)
    t0 = last_change = time.time()
    seen, last_status, finished = set(), "", False
    try:
        if a.max_rate and (inst.get("rate_per_hr_inr") or 0) > a.max_rate:
            print(f"rate ₹{inst.get('rate_per_hr_inr')} is above --max-rate {a.max_rate}: stopping")
            return
        while time.time() - t0 < a.max_min * 60 and time.time() - last_change < 25 * 60:
            time.sleep(30)
            status = (dropbox.get(f"{run_id}/out/status.txt") or b"").decode("utf-8", "replace")
            if status != last_status:
                new = status[len(last_status):] if status.startswith(last_status) else status
                print(new.strip()[-1500:], flush=True)
                last_status, last_change = status, time.time()
            for name in dropbox.names(f"{run_id}/out/"):
                short = name.split("/out/", 1)[1]
                if short.endswith(".jpg") and short not in seen:
                    open(os.path.join(a.out_dir, short), "wb").write(dropbox.get(name))
                    seen.add(short)
            if dropbox.get(f"{run_id}/out/DONE") or "ALL DONE" in status or "STOPPED WITH AN ERROR" in status:
                finished = True
                break
            st = gs("GET", f"/v1/instances/{iid}")
            if st.get("status") in ("error", "stopped"):
                print("the machine stopped by itself:", st.get("status"), st.get("error_msg") or st.get("display_message"))
                break
        if not finished:
            print("stopping: " + ("time limit" if time.time() - t0 >= a.max_min * 60 else "no progress for 25 minutes"))
    finally:
        try:
            gs("DELETE", f"/v1/instances/{iid}")
            print("machine deleted", flush=True)
        except Exception as e:  # noqa: BLE001
            print("DELETE FAILED, delete it in the GridShare app:", iid, e, flush=True)
        time.sleep(15)
        try:
            st = gs("GET", f"/v1/instances/{iid}")
            print(f"final: {st.get('status')}, ran {st.get('running_seconds')} s, cost ₹{st.get('total_cost_inr')}")
        except Exception:  # noqa: BLE001
            pass
        log = dropbox.get(f"{run_id}/out/run.log")
        if log:
            open(os.path.join(a.out_dir, f"run_{run_id}.log"), "wb").write(log)
        print(f"{len(seen)} pictures saved in {a.out_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prompts", "run"])
    ap.add_argument("shots")
    ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--only")
    ap.add_argument("--takes", type=int, default=2)
    ap.add_argument("--node")
    ap.add_argument("--min-vram", type=float, default=23)
    ap.add_argument("--max-rate", type=float, default=35)
    ap.add_argument("--max-min", type=float, default=90)
    a = ap.parse_args()
    if a.cmd == "prompts":
        job, _ = job_for(a.shots, set(a.only.split(",")) if a.only else None, a.takes)
        out = os.path.join(os.path.dirname(os.path.abspath(a.shots)), "keyframes_job.json")
        json.dump(job, open(out, "w"), indent=1, ensure_ascii=False)
        print(f"{len(job['images'])} pictures, cast {job['cast']} -> {out}\n\nexample:\n{job['images'][0]['prompt']}")
    else:
        run(a)
