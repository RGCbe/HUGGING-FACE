# HUGGING-FACE

Testing and researching models from the Hugging Face Hub.

| Folder | What's in it |
|---|---|
| [`research/`](research/) | Notes on uncensored models: rankings, licenses, where to run them, platform rules. `ugi_rank.py` re-ranks models from the UGI Leaderboard. |
| [`studio/`](studio/) | **Private Studio**, a Hugging Face Space for images and writing about fictional adults, with safety filters built in. See [`studio/README.md`](studio/README.md). |

## Tests

```bash
pip install pytest
pytest
```

The tests cover the studio's safety filter (`studio/safety.py`) and need no GPU or model downloads.
