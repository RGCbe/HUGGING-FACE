# Manoj's voice recordings (30 Oct 2026)

What the owner records so the AI voice speaks like a storyteller instead of reading an announcement.
The voice copies the delivery of its sample as well as its sound, so each sample is read in the
mood it stands for. The words below are the exact text of each recording (the voice needs them word
for word). Each one becomes, in the private dataset `Rggroups/super-kural-voice`:

| File the owner sends | Stored as | Used for |
| --- | --- | --- |
| 1 storyteller | `teabreak/storyteller.opus` + `.txt` | every line without a tag (the main voice) |
| 2 excited | `teabreak/emotion/excited.opus` + `.txt` | `[excited]` lines |
| 3 mysterious | `teabreak/emotion/mysterious.opus` + `.txt` | `[mysterious]` lines |
| 4 funny | `teabreak/emotion/funny.opus` + `.txt` | `[funny]` lines |
| 5 shocked | `teabreak/emotion/shocked.opus` + `.txt` | `[shocked]` lines |
| 6 serious | `teabreak/emotion/serious.opus` + `.txt` | `[serious]` lines |
| 7 warm | `teabreak/emotion/warm.opus` + `.txt` | `[warm]` lines (the greeting, calm moments) |

Before storing, check each recording with Whisper against its text, trim it to whole words with
`videos/kural/ref_prep.py`, and keep it between 8 and 16 seconds.

## How to record

- A quiet room: no fan, no AC, no TV. A room full of clothes is best.
- Phone 15 to 20 cm from the mouth, a little to the side; the voice memo app; the same place for all
  seven.
- The deepest voice that is comfortable, never forced. Slower than normal talking.
- Act the mood a little MORE than feels natural: the AI tones it down.
- "..." means a real pause, about one second.
- One second of silence before and after. If you stumble, start that one again.
- Read each two or three times and send the best take of each, named 1 to 7.

## The words

**1. Storyteller (calm, confident, the main voice; about 15 seconds)**

Let me tell you a story. There's a boy who sells tea next to a monster Gate. Ten rupees a glass.
Nobody looks at him twice... but one night, everything changes.

**2. Excited**

And then it happened! Golden light, everywhere! One swing, and the giant monster was gone. Can you
believe that? I couldn't stop smiling!

**3. Mysterious (quiet, slow)**

But here's the strange part... nobody knew where the tea came from. No shop. No farm. Just an old
clay cup... and a boy who never told anyone his secret.

**4. Funny (a smile in the voice, deadpan on the last words)**

So the general marched his whole army into the field... to fight birds. Big, angry birds. And
honestly? The birds won. Twice.

**5. Shocked**

Wait, what? Thirty-eight minutes? That's it? The whole war was over before my tea even got cold!
How is that even possible?

**6. Serious (low, steady, no smile)**

This wasn't a game anymore. People were hungry, soldiers were tired, and one wrong move could start
a real war. Everyone was waiting to see who would blink first.

**7. Warm (friendly, like greeting a friend)**

Hello friends, I'm Manoj. Grab your tea, sit back, and let me tell you something that really
happened. And if you know a story like this, tell me in the comments.
