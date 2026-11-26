"""Fix the lines the AI singer sang wrong, one at a time, like a studio punch-in: find each lyric line in the take,
score how well its words came out, and for the bad ones have the song model sing just that part again (/repaint on
the private Space) with a few seeds, keeping the take whose words are heard best.

    python3 fixlines.py SONG.json SEED [--below 0.55] [--tries 2]
        -> WORK/take_SEED.fixed.flac and WORK/take_SEED.fixlog.json

The owner (26 Nov 2026): "Now voice is clear but I cant understand it what the songs is": the AI singer
mispronounced the Tamil (கனவு sung as கானவர், வைபவ் வந்தா as பயப்போ வந்தா). Words are judged with faster-whisper
medium (no-speech filters off) on the vocal of each part, separated with torchaudio's HDemucs (weights-only load).
Where data goes: the song and its lyrics only to the owner's private Space, with HF_TOKEN.
"""
import argparse
import difflib
import json
import os
import shutil
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import song as S  # noqa: E402
from lyrics_check import sections, sung_text  # noqa: E402

SR = S.SR


def lyric_lines(lyrics):
    return [sung_text(l) for s in sections(lyrics) for l in s["lines"] if S.norm_text(sung_text(l))]


class Ears:
    """Separates the vocal of a stretch of song and hears its words."""

    def __init__(self):
        import torch
        from faster_whisper import WhisperModel
        from torchaudio.pipelines import HDEMUCS_HIGH_MUSDB_PLUS as bundle
        torch.set_num_threads(os.cpu_count() or 4)
        self.torch = torch
        self.sep = bundle.get_model()  # torch.load with weights_only=True (PyTorch's default)
        self.asr = WhisperModel("medium", device="cpu", compute_type="int8")

    def vocals(self, x):
        """x: (2, n) at 44.1 kHz -> mono vocal, 16 kHz."""
        import librosa
        n = x.shape[1]
        x = np.pad(x, ((0, 0), (0, (-n) % 4096)))  # HDemucs wants whole STFT hops
        t = self.torch.from_numpy(x.copy())
        ref = t.mean(0)
        t = (t - ref.mean()) / (ref.std() + 1e-8)
        with self.torch.no_grad():
            y = self.sep(t[None])[0][..., :n]
        v = (y[list(self.sep.sources).index("vocals")] * (ref.std() + 1e-8) + ref.mean()).mean(0).numpy()
        return librosa.resample(v, orig_sr=SR, target_sr=16000)

    def words(self, v16, with_times=False):
        segs, _ = self.asr.transcribe(v16, language="ta", beam_size=5, vad_filter=False,
                                      condition_on_previous_text=False, no_speech_threshold=None,
                                      log_prob_threshold=None, compression_ratio_threshold=None,
                                      word_timestamps=with_times)
        if not with_times:
            return " ".join(s.text.strip() for s in segs)
        return [(w.word.strip(), w.start, w.end) for s in segs for w in (s.words or [])]


def ratio(a, b):
    a, b = S.norm_text(a), S.norm_text(b)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def recall(line, heard_text):
    """Share of the line's letters heard (extra words from the next line around it do not count against it)."""
    a, b = S.norm_text(line), S.norm_text(heard_text)
    if not a or not b:
        return 0.0
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return sum(m.size for m in sm.get_matching_blocks()) / len(a)


def align(lines, words):
    """Each lyric line -> (start, end, score), in order: the run of heard words that matches the line best."""
    out, p = [], 0
    for line in lines:
        n_words = max(1, len(line.split()))
        best = (0.0, p, p)
        for s in range(p, min(len(words), p + 6)):
            for q in range(s + 1, min(len(words), s + n_words + 5) + 1):
                r = ratio(line, " ".join(w for w, _, _ in words[s:q]))
                if r > best[0]:
                    best = (r, s, q)
        r, s, q = best
        if r >= 0.25 and q > s:
            out.append([words[s][1], words[q - 1][2], r])
            p = q
        else:
            out.append([None, None, 0.0])
    # lines never found sit between their neighbours
    for i, row in enumerate(out):
        if row[0] is None:
            prev = next((out[j][1] for j in range(i - 1, -1, -1) if out[j][1] is not None), 0.0)
            nxt = next((out[j][0] for j in range(i + 1, len(out)) if out[j][0] is not None), prev + 4.0)
            row[0], row[1] = prev, max(prev + 1.5, nxt)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("seed", type=int)
    ap.add_argument("--below", type=float, default=0.55, help="fix lines whose words score below this")
    ap.add_argument("--tries", type=int, default=2, help="new takes per bad line")
    a = ap.parse_args()
    song = json.load(open(a.song))
    d = S.work(song)
    cur = os.path.join(d, f"take_{a.seed}.fixed.flac")
    if not os.path.exists(cur):
        shutil.copy(os.path.join(d, f"take_{a.seed}.flac"), cur)
    lines = lyric_lines(song["lyrics"])
    ears = Ears()
    x = S.load(cur).T.copy()
    print("finding the lines ...", flush=True)
    spans = align(lines, ears.words(ears.vocals(x), with_times=True))
    log = []
    from gradio_client import Client, handle_file
    client = None
    for i, (line, (t0, t1, score)) in enumerate(zip(lines, spans)):
        if score >= a.below:
            log.append({"line": line, "start": round(t0, 2), "end": round(t1, 2), "score": round(score, 2)})
            continue
        s0, s1 = max(0.0, t0 - 0.3), min(x.shape[1] / SR, t1 + 0.3)

        def heard(xx):
            w0, w1 = int(max(0, s0 - 1.0) * SR), int(min(xx.shape[1] / SR, s1 + 1.0) * SR)
            return recall(line, ears.words(ears.vocals(xx[:, w0:w1])))
        base = heard(x)
        best, best_path = base, None
        for k in range(a.tries):
            client = client or S.client()
            try:
                p = client.predict(handle_file(cur), song["caption"], song["lyrics"], s0, s1, 1000 + 37 * i + k,
                                   song["language"], song.get("bpm", 0), api_name="/repaint")
            except Exception as e:  # noqa: BLE001 (a GPU quota or a busy Space: keep what is fixed so far)
                print(f"   repaint stopped: {str(e)[:160]}", flush=True)
                log.append({"line": line, "start": round(s0, 2), "end": round(s1, 2), "score": round(base, 2),
                            "stopped": True})
                json.dump(log, open(os.path.join(d, f"take_{a.seed}.fixlog.json"), "w"), ensure_ascii=False, indent=1)
                return
            y = S.load(p).T.copy()
            n = min(x.shape[1], y.shape[1])
            cand = x.copy()
            cand[:, :n] = y[:, :n]
            r = heard(cand)
            if r > best:
                best, best_path = r, cand
        if best_path is not None:
            x = best_path
            sf.write(cur, x.T, SR)
        log.append({"line": line, "start": round(s0, 2), "end": round(s1, 2), "score": round(base, 2),
                    "fixed": round(best, 2) if best_path is not None else None})
        print(f"{i + 1:2d}. {line[:40]:40s} {base:.2f} -> {best:.2f}", flush=True)
        json.dump(log, open(os.path.join(d, f"take_{a.seed}.fixlog.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(log, open(os.path.join(d, f"take_{a.seed}.fixlog.json"), "w"), ensure_ascii=False, indent=1)
    bad = [r for r in log if r.get("score", 1) < a.below]
    print(f"done: {len(bad)} line(s) re-sung; {sum(1 for r in bad if r.get('fixed'))} improved -> {cur}")


if __name__ == "__main__":
    main()
