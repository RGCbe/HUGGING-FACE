# YouTube agent skills

Eleven project-local Claude Code skills (`/yt-script`, `/yt-package`, `/yt-edit`, `/yt-comment`,
`/yt-plan`, `/yt-viral`, `/yt-retention`, `/yt-shorts`, `/yt-seo`, `/yt-chapters`, `/yt-audit`)
live in [`../skills/`](../skills). They load automatically when Claude Code runs in this repo.

Vendored unmodified from
[Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill) at
commit `a2feb2104981a375ffd4f87ee04f4f5344ac43c6`, under the MIT licence in [`LICENSE`](LICENSE).

## Voice profile

Every skill reads `~/.claude/youtube/voice.md`. This channel's profile is kept in
[`voice.md`](voice.md), and a `SessionStart` hook in [`../settings.json`](../settings.json) copies it
there at the start of each session, so it survives fresh cloud containers. Edit `voice.md` here, not
the copy in your home directory. [`voice.template.md`](voice.template.md) is the blank upstream
template.

## Tools

Six of the skills ship a Python 3 tool with no dependencies:

```bash
python3 .claude/skills/yt-script/hookscore.py --hook "one line"
python3 .claude/skills/yt-package/title.py --title "..." --thumb "..."
python3 .claude/skills/yt-edit/deadair.py transcript.srt
python3 .claude/skills/yt-chapters/chapters.py transcript.srt
python3 .claude/skills/yt-retention/retention.py retention.csv --duration 600 --transcript transcript.srt
python3 .claude/skills/yt-viral/swipe.py collected.json --min 2.0
```

`retention.py` treats the x axis as a percentage whenever its largest value is 100 or less, so pass
`--duration` (in seconds) with `--transcript` or the cliffs cannot be matched to what was said.

## Updating

```bash
git clone https://github.com/Jakeschincariol/youtube-agent-skill.git /tmp/yt
cp -r /tmp/yt/skills/yt-* .claude/skills/
cp /tmp/yt/templates/voice.md .claude/youtube/voice.template.md
```

Then update the commit hash above.
