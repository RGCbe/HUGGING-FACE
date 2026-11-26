# Song craft: how a Tamil song is built

What every song run follows (the owner, 26 Nov 2026: study "all elements in the songs", "for our model"). The study
with sources, laid out as a page: https://claude.ai/artifact/9kwFX6kp44Lcr3UoZNMNzt (private to the owner).
`lyrics_check.py` scores lyrics against this file; the skill is `.claude/skills/tamil-song/SKILL.md`.

## The owner's standing wishes (in his words)

| Wish | Date |
|---|---|
| "feel him and his playing in the songs": the song is about the person and what makes them special, with real facts | 25 Nov 2026 |
| "words are crystal clear and understandable, not like the reading or AI script" | 25 Nov 2026 |
| "We need 2 min songs" | 25 Nov 2026 |
| Background music "unique one like a rapkuthu"; he picked sample D (rap-kuthu, 100 BPM) | 25-26 Nov 2026 |
| "use my voice only" (lead, gang, every voice) | 26 Nov 2026 |
| "I want like songs": sung with a melody, never spoken or read | 26 Nov 2026 |

## The parts, in order

A Tamil film song borrows its form from the Carnatic kriti: pallavi, anupallavi, charanam. Since the Ilaiyaraaja era
most film songs have two charanams with instrumental preludes and interludes between them (older songs had three).
For a 2-minute song keep one charanam and one interlude.

| Part | What it does | Length (100 BPM, bar = 2.4 s) |
|---|---|---|
| தொகையறா thogaiyara | Slow, free-rhythm verse before the song, no drums (like the Carnatic viruttam); sets the feeling, then the drums hit | 2-4 short lines, ~12 s |
| முன்னிசை prelude | Instrumental opening with the signature riff | 4 bars |
| பல்லவி pallavi | The hook and the title line; 2-4 easy lines; comes back after every part; singable after one listen | 8 bars (2 a line) |
| அனுபல்லவி anupallavi | "Next to the pallavi": 2-4 lines that climb higher, then land back on the pallavi (optional) | 4 bars |
| இடையிசை interlude | Instrumental break; in kuthu the dance break with call-and-response and crowd shouts | 4 bars |
| சரணம் charanam | The story; every charanam has the same tune; its last line leads back into the pallavi; in rap-kuthu it is rapped | 8 bars (1 a rap line) |
| கூட்டுக்குரல் gang | The crowd answers the lead: "ஹே!", the name, the last word of a line | in brackets in the lyrics |
| சங்கதி sangathi | A repeated line changes its melody a little each time | the last pallavi |
| முடிவு ending | The pallavi a key higher, a final shout or held note, one last hit | ~8 s |

The 2-minute map: thogaiyara 0:00, prelude 0:12, pallavi 0:22, anupallavi 0:41, half pallavi 0:51, interlude 1:00,
charanam 1:10, pallavi (key up) 1:29, ending 1:48-1:56. The hook must be heard by about 0:25.

## Word craft

- **மெட்டு metu first.** In Tamil cinema the composer usually makes the tune and the lyricist writes to it
  (Vairamuthu wrote almost all of his 8,000-odd songs to a tune). The composer shows the syllable pattern with
  **தத்தகாரம் tatthakaram** ("தன னா தன னா").
- **சந்தம் santham.** Long and short syllables sit on the beat; this is what makes words sung, not read. A sung line
  is at most 14 syllables (2 bars at 100 BPM); a rapped line at most 20 (1 bar). Our first song had 12 lines over 14
  and the owner could not follow the words.
- **மோனை monai**: the same first letter: "**வை**பவ் **வ**ந்தா **வெ**றித்தனம்", "**ப**ந்து **ப**றக்குது".
- **எதுகை etukai**: the same second letter in a couplet: "அ**டி**ச்சா சிக்ஸ் தான் / மு**டி**ச்சா மேட்ச் தான்".
- **இயைபு iyaibu**: the same ending: "வயசு தான் **டா** / சிங்கம் **டா**".
- Spoken, everyday Tamil, the way fans talk (சிக்ஸ், பவுலர், ஸ்டாண்டு), never essay Tamil (ஆகிறது, இருக்கின்றன,
  மேலும்). One idea per line. The hook word repeated at least four times. Gang answers in brackets.
- The person's real story and moves, checked in two sources (for Vaibhav: Samastipur, six off his first IPL ball, a
  35-ball hundred at 14; ESPNcricinfo, Sky Sports). A claim from the owner's message is marked as his.

## The beat

Kuthu is led by percussion: parai, thavil and urumi figures layered on each other, clipped accents, hand claps, a
strong downbeat; since the 2000s with big drops and crowd shouts. Rap-kuthu puts 808 bass and hip-hop drums under the
same folk drums: the pallavi is sung (each syllable has room, the last vowel is held), the charanam rapped (two or three
syllables a half-beat, the stressed word on the beat).

## How a song is made, and the step we lack

1. Situation (the story and the feeling). 2. Metu and tatthakaram. 3. Lyrics to the metu. 4. Guide track.
5. **The singer**: several takes, the best phrases joined. 6. Arrangement (interludes, gang, key change).
7. Mix and master (-14 LUFS, true peak -1 dB).

Steps 1-4, 6 and 7 are automatic here. Step 5 in the owner's own voice, sung and clear, is not solved yet. What was
measured (faster-whisper medium, share of the lyric letters heard; sample D = rap-kuthu, verse + chorus, 45 s):

| How the vocal was made | Words heard | The owner |
|---|---|---|
| ACE-Step singer, Tamil script, 128 BPM (sample A) | 37% | - |
| ACE-Step singer, romanised Tamil, 128 BPM (B) | 57% | - |
| ACE-Step singer, Tamil script, 100 BPM (C) | 71% | - |
| ACE-Step singer, romanised Tamil, 100 BPM (D) | 49% | likes the music, "the words I can't understand" |
| Any of these re-voiced by Seed-VC from 15 s of his speech | 0-12% | - |
| The same re-voiced by ElevenLabs' voice changer | 0% | - |
| His ElevenLabs voice speaking each line on the beat, gang of his takes (rap.py) | 84-86% | "voices are good", "like he speaks or reading" |
| His ElevenLabs voice asked to sing, tuned to the key (rap.py, sing) | 74% | still not a song |

So: a slower beat (100 BPM) and short lines help the AI singer most; re-voicing an AI singer from a speech sample
destroys fast Tamil words; text-to-speech is clear but not singing. A real sung take in his voice is what step 5 needs:
his own singing (best), Suno Voices (his app; his voice data goes to Suno, which reportedly may train on it; check
their privacy terms with him first), or a singing model trained on 10-30 minutes of his singing.
