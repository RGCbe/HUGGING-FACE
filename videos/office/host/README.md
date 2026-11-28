# Manoj, the host of Office Tea Talks (doodle)

The owner drawn in the office stories' doodle style, at his request (22 Nov 2026: "use my photo also"), made with
FLUX.2 [klein] on his own private Space from his own photo (the photo is kept private, never in this repository) and
the stories' style picture. He is the host, not a character: he opens the Short, reacts to a joke, and asks for the
comments at the end. The story's characters stay invented.

| Picture | Use |
|---|---|
| `host_hello.png` | the start: on a bench at a tea stall, tea in hand, waving (a short first shot, weight about 0.7) |
| `host_laugh.png` | after the funniest line, laughing with his tea about to spill |
| `host_think.png` | before the twist or the lesson, hand on chin, eyebrow raised |
| `host_comment.png` | the last line (the comments question): thumbs up, tea in hand, empty speech bubbles |

New poses: `videos/doodle/imagegen.py` with `"edit"` = a story picture (for the style) and `"also"` = one of these
pictures (for his face), and a prompt that says "the man in image 1"; check that he has two hands.

**Talking mouth (22 Nov 2026):** `host_comment.open.png` and `host_comment.closed.png`, and `host_think.closed.png` and
`host_think.open.png`, are the same pictures with only the mouth changed. The mouth was edited on the owner's own Space,
and only the mouth area was copied back into the original. The renderer (doodle/depthmove.py, used by
movies-explained/lore_video.py) switches between the two while the voice speaks, so the host talks.
