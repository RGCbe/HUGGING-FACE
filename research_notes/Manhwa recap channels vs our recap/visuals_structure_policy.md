# Manhwa/manga/webtoon recap videos on YouTube (2025-2026): visuals, structure, retention, Shorts and policy risk

Method note for the report writer: besides web sources, this research used (a) the YouTube Data API v3 on 2026-10-29 (6 searches plus video and channel lookups, about 615 quota units, public metadata only) to pull 262 videos from 163 channels published 2025-01-01 or later ("manhwa recap" long/medium/short sorted by views, "manga recap" long, "webtoon recap", and "manhwa recap" relevance since 2026-06-01), and (b) YouTube's own public stills on i.ytimg.com (the custom thumbnail `hqdefault.jpg` plus the three auto-generated mid-video stills `hq1/hq2/hq3.jpg`) for 21 top videos. That gives 3 real frames per video, so visual statements are a sample, not a frame-by-frame analysis. No video, audio or captions were downloaded. Search sorted by views is biased toward older uploads and huge compilations, so the duration figures describe what wins on views, not everything that gets uploaded. Regex counts over descriptions are approximate.

## 1. Visual presentation: framing, motion, time per panel

### Takeaway
Top long-form 16:9 recaps use two main layouts, often in the same video: (1) a wide panel cropped and zoomed to fill the frame, and (2) a tall webtoon panel shown at its own shape in the centre over a blurred, enlarged copy of itself. A few channels also use multi-panel collages, and some fast-growing Hindi channels appear to use generated cinematic illustrations instead of the original panels. Shorts are full-bleed 9:16 close-ups. Motion is subtle zoom and pan; I found no reliable numbers on seconds per panel.

### Cited Findings
- **Full-frame cropped panels (16:9):** in all three stills from Manhwa Fresh (645K subs, the largest long-form channel in the sample), the panel is cropped to fill the frame, with original speech bubbles and SFX ("SMACK") left in. — [Manhwa Fresh still hq1](https://i.ytimg.com/vi/pjOoN03xa0k/hq1.jpg), [hq2](https://i.ytimg.com/vi/pjOoN03xa0k/hq2.jpg), [video](https://www.youtube.com/watch?v=pjOoN03xa0k)
- ActionToon (454K subs) shows full-frame crops of black-and-white manga and colour panels with the English lettering visible. — [ActionToon stills](https://i.ytimg.com/vi/VX-oKQetIB8/hq2.jpg), [video](https://www.youtube.com/watch?v=VX-oKQetIB8)
- **Centred strip over a blurred copy of itself:** all three stills of Mamoru Manhwa (561K) and Tobs Manhwa (383K), and most stills of Frieren Manhwa, The Story Unfolds, Evergarden Manhwa and Losweko, show a tall panel in the middle with blurred, enlarged versions of the same art filling the sides. — [Mamoru hq1](https://i.ytimg.com/vi/YGLNNUaMju0/hq1.jpg), [Tobs hq2](https://i.ytimg.com/vi/0w1FjXmgX0w/hq2.jpg), [The Story Unfolds hq1](https://i.ytimg.com/vi/PnBrjozh2cM/hq1.jpg), [Evergarden hq1](https://i.ytimg.com/vi/obaZWVPr2Zc/hq1.jpg), [Frieren Manhwa hq2](https://i.ytimg.com/vi/_xydUWNJnic/hq2.jpg)
- **Mixed layouts in one video:** ManhwaDealer (274K), Frieren Manhwa and Daily Manhwa Fresh switch between a centred strip with blur and a full-frame crop from still to still. — [ManhwaDealer hq1](https://i.ytimg.com/vi/U-k_Mr8q1sk/hq1.jpg) vs [hq2](https://i.ytimg.com/vi/U-k_Mr8q1sk/hq2.jpg); [Daily Manhwa Fresh hq1](https://i.ytimg.com/vi/opbYhLf8jW0/hq1.jpg) vs [hq2](https://i.ytimg.com/vi/opbYhLf8jW0/hq2.jpg)
- **Small panel on a dark blurred field:** KenRecaps puts a small black-and-white manga panel in the middle of a dark blurred background, with an "@Kenrecaps" watermark and, in one still, a red subscribe-button graphic. — [KenRecaps hq2](https://i.ytimg.com/vi/cTQF3rj4zMk/hq2.jpg), [hq3](https://i.ytimg.com/vi/cTQF3rj4zMk/hq3.jpg)
- **Comic-page collage:** Tyler's Manhwa (72K) lays two or three framed panels side by side on a blurred or gradient background. — [Tyler's Manhwa hq2](https://i.ytimg.com/vi/IWzsRK-GgPc/hq2.jpg), [hq3](https://i.ytimg.com/vi/IWzsRK-GgPc/hq3.jpg)
- **Generated-looking cinematic visuals (Hindi channels):** stills from Manhwa Senpai (3.8M views; dice, a calendar, a rainy street, with a "MANHWA SENPAI" watermark) and yuva explainop (a red-eyed bear, cinematic shots) do not look like scanned manhwa pages. They look like rendered anime-style illustrations, which suggests generated art. This is my visual judgement only, not confirmed. — [Manhwa Senpai hq1](https://i.ytimg.com/vi/aQ0xKM2OCwQ/hq1.jpg), [hq3](https://i.ytimg.com/vi/aQ0xKM2OCwQ/hq3.jpg); [yuva explainop hq1](https://i.ytimg.com/vi/MbGvwZqwM14/hq1.jpg)
- A critic's video (2026-09-20) alleges that "AI-generated recaps, engineered clickbait and adult manhwa content are flooding the space." This is opinion. — [Draw First, Panic Later, "Manhwa Recap Isn't What You Think… It's WAY Worse"](https://www.youtube.com/watch?v=PGADB4I4nwg)
- **Shorts are full-bleed 9:16:** the vertical frame from Manhwa Tease (`oar2.jpg`, 1080x1920) is a panel zoomed in to fill the whole frame, with a centred caption and a semi-transparent channel watermark. The blurred sides in the 16:9 `hq` stills of Shorts are YouTube's own fill for vertical video, not the creator's edit. — [Manhwa Tease vertical frame](https://i.ytimg.com/vi/ksO7HaHbhJk/oar2.jpg), [video](https://www.youtube.com/watch?v=ksO7HaHbhJk)
- **Pattern-interrupt cutaways:** Manhwa Outpost cuts to a stock photo of a man in a suit pointing at a building, with the caption "safe house". Schikan's review cuts to an emoji and a stock photo of a baby between small panels on white. — [Manhwa Outpost hq1](https://i.ytimg.com/vi/E4q9RTu5dXs/hq1.jpg); [Schikan hq1](https://i.ytimg.com/vi/b4KL405WjQE/hq1.jpg), [hq2](https://i.ytimg.com/vi/b4KL405WjQE/hq2.jpg)
- Editing tutorials describe the toolkit as "motion, overlays, transitions, sound effects, and even light color grading to turn still manhwa panels into cinematic storytelling" (Premiere Pro tutorial, 2025-04-17). — [Manhwa Tales, "How to Make Manhwa/Manga Recaps l DETAILED"](https://www.youtube.com/watch?v=_jH0wSArvjk)
- A freelance brief for recap editing asks for "dynamic cuts, subtle zooms and pans, dramatic sound design, clean subtitles, and engaging background music", at 1080p, 30 fps, H.264. — [Freelancer.com project "Manhwa Recap Video Editing"](https://www.freelancer.com/projects/video-post-editing/manhwa-recap-video-editing)
- Tools sold to recap makers automate Ken Burns moves: MagaRecap applies "pan, zoom, or reveal" to each scene, and Zoomatrix is a $39 After Effects grid-click zoom script. An FFmpeg pipeline composites Ken Burns pan and zoom over panels. — [MagaRecap](https://magarecap.com/); [Zoomatrix on Gumroad](https://mediancreate.gumroad.com/l/zoomatrix); [DEV Community AI recap studio](https://dev.to/aashish124/how-i-built-an-ai-studio-that-turns-manhwa-chapters-into-narrated-recap-videos-5enl)
- One how-to explains the blur-background method in CapCut: duplicate the layer, cut out the subject on the top copy, blur the bottom copy. — [CreateThat, "How to Blur on CapCut"](https://www.createthat.ai/blog/how-to-blur-on-capcut)
- Gore appears on screen in some top recaps (a bloodied face in a Tobs Manhwa still). — [Tobs Manhwa hq1](https://i.ytimg.com/vi/0w1FjXmgX0w/hq1.jpg)

### Inferences
- The centred strip with blur exists because webtoon panels are tall and narrow. Cropping them to 16:9 cuts off heads or bubbles, so channels show the whole panel and fill the empty sides with blur. Wide or square panels are cropped to full frame instead. In the 16:9 sample (16 long-form and medium videos), a mix of the two layouts was the most common pattern. A single fixed treatment for every panel is less common.
- Close-ups of faces are the main shot in both formats. Stills are mostly tight crops of expressions, not whole pages.
- Watermarks are everywhere: channel names (Manhwa Senpai, EvergardenManhwa, @Kenrecaps), and in at least one case what looks like a scanlation group's mark ("OTAKUSAN" on Manhwa Outpost frames). — [Manhwa Outpost hq2](https://i.ytimg.com/vi/E4q9RTu5dXs/hq2.jpg)

### Gaps
- **Seconds per panel:** I found no tutorial or creator post with a measured or recommended number, and measuring it would need watching or downloading video, which was out of scope. The report should not quote a figure.
- **Shake, flash and impact effects:** I could not confirm how common these are. Three stills per video cannot capture motion, and the tutorials I found describe effects only in general terms.

## 2. Speech bubbles and on-screen text

### Takeaway
There is no single standard. Big English long-form channels often leave the scanlation lettering in. Others crop the panel to avoid bubbles. "Dub" channels re-letter bubbles with their own dialogue. Inpainting tools that remove bubbles exist. Long-form recaps rarely burn in narration subtitles, while almost every Short burns in one- to three-word bold captions.

### Cited Findings
- **Original lettering kept:** English scanlation text is visible in Manhwa Fresh ("THESE TWO MEN ARE THE", "YES..."), ActionToon ("THERE'S NO NEED FOR CONCERN", "ALBUS, YOUR SWORD... IT'S GOT A CHIP IN IT"), Evergarden (SFX "RUMBLE", "CLICK", plus a dialogue bubble) and KenRecaps. — [Manhwa Fresh hq2](https://i.ytimg.com/vi/pjOoN03xa0k/hq2.jpg), [hq3](https://i.ytimg.com/vi/pjOoN03xa0k/hq3.jpg); [ActionToon hq3](https://i.ytimg.com/vi/VX-oKQetIB8/hq3.jpg); [Evergarden hq2](https://i.ytimg.com/vi/obaZWVPr2Zc/hq2.jpg); [KenRecaps hq3](https://i.ytimg.com/vi/cTQF3rj4zMk/hq3.jpg)
- **Untranslated raw text kept:** Korean SFX ("파앗" in Mamoru, "흐음~" in WaifusToonz) and Chinese text (ManhwaDealer) remain in frames. — [Mamoru hq3](https://i.ytimg.com/vi/YGLNNUaMju0/hq3.jpg); [ManhwaDealer hq3](https://i.ytimg.com/vi/U-k_Mr8q1sk/hq3.jpg); [WaifusToonz hq1](https://i.ytimg.com/vi/NU3ZZmi_zUw/hq1.jpg)
- **Bubbles cropped out or absent:** no dialogue bubbles appear in the sampled stills of Mamoru Manhwa, The Story Unfolds, or the Shorts from Manhwa Tease and Enir Manhwa, which are tight face crops. — [The Story Unfolds hq2](https://i.ytimg.com/vi/PnBrjozh2cM/hq2.jpg); [Enir Manhwa hq2](https://i.ytimg.com/vi/Jsye9qpS8m8/hq2.jpg)
- **Re-lettered "dub" bubbles:** Losweko ("Manhwa Recap Dub") shows panels with rough, newly written bubbles ("this is a chance to get", "why are you leaving sorry") over a blurred background. — [Losweko hq2](https://i.ytimg.com/vi/Og8kH4_NFIk/hq2.jpg), [video](https://www.youtube.com/watch?v=Og8kH4_NFIk)
- **Automated bubble removal:** an AI recap pipeline removes bubbles and inpaints the art in "narrated mode" but keeps them in "dialogue mode", and calls clean inpainting on detailed backgrounds the second-hardest problem. Another user removed bubbles with IOPaint/LaMa and called the result "pretty good but it can be better". — [DEV Community](https://dev.to/aashish124/how-i-built-an-ai-studio-that-turns-manhwa-chapters-into-narrated-recap-videos-5enl); [IOPaint GitHub discussion #235](https://github.com/Sanster/IOPaint/discussions/235)
- **Shorts captions:** burned-in, centred, bold yellow (sometimes white) text with a black outline, one to three words at a time ("AFTER SCHOOL", "HE WANTED TO DROP OUT", "HONESTLY,", "DESTROYING", "BADDIE!", "ZORO'S COUSIN", "EMPRESS"). Takovara adds red arrows. — [Manhwa Tease oar2](https://i.ytimg.com/vi/ksO7HaHbhJk/oar2.jpg); [Enir Manhwa hq1](https://i.ytimg.com/vi/Jsye9qpS8m8/hq1.jpg); [Akiel Runes hq2](https://i.ytimg.com/vi/TAPhcHn0rDM/hq2.jpg); [Recap Ronin hq2](https://i.ytimg.com/vi/8OFKMBvLkws/hq2.jpg); [Takovara hq1](https://i.ytimg.com/vi/VgNygUalSsc/hq1.jpg)
- **Long-form narration subtitles are rare:** across about 48 long-form stills from 16 videos, only Evergarden showed a subtitle-like narration line ("THE HULL TREMBLED AS THE SHIP SET DOWN") and Manhwa Outpost a cutaway label ("safe house"). — [Evergarden hq1](https://i.ytimg.com/vi/obaZWVPr2Zc/hq1.jpg)
- A 2026 guide recommends "animated text overlays to show chapter numbers and character names clearly" and warns that misspelled names draw negative comments. — [FluxNote guide, updated 2026-03-09](https://fluxnote.io/guides/manhwa-webtoon-recap-channel)

### Inferences
- For a webtoon the creator made themselves, the bubbles are original lettering, so keeping them is legally neutral. The real choice is whether the narration repeats the bubble text, which is redundant, or tells the story around it.
- Word-by-word yellow captions are a Shorts convention, not a long-form one. A 3-minute horizontal recap with full subtitles would look more like a Short than a typical long-form recap.

### Gaps
- I found no survey or count of how many channels clean bubbles versus keep them. The split above comes from about 20 channels' stills only.

## 3. Video structure: hook, intro, order, cliffhangers, endings, chapters

### Takeaway
The hook is mostly carried by packaging. Titles follow a "weak or betrayed person, then a twist, then becomes overpowered" pattern, and thumbnails use arrows and labels. Guides advise opening on conflict or mystery rather than "today I will explain". Few long-form recaps use chapters, and when they do, the chapters mark "Part" boundaries, not story beats. Many channels hide the series name and re-upload ever-longer cumulative compilations with a "New Part" timestamp.

### Cited Findings
- **Title formula:** 95 of 113 long-form (20 min or longer) recap titles in the sample contain "Manhwa Recap". 46 of 113 contain an all-caps word of 4 or more letters, and about 33 of 113 use a turn ("but", "until", "then", "…"). Examples: "Everyone Calls Him WEAK But He STEALS Their TALENTS And Grows 100X FASTER!" (1.09M views); "Trapped In a Dungeon For 2 DECADES He's Back MAX-LEVEL To Break All RECORDS!" (1.15M). — [Frieren Manhwa](https://www.youtube.com/watch?v=_xydUWNJnic); YouTube Data API sample (see Method note)
- **First-person titles (2026 trend):** Hindi channels write titles in the first person: "Apocalypse Se Pehle Main Reborn Hua Aur Apni Family Se Badla Liya!" (2.56M views, 36m37s, 2026-08-08); "Main 9 Divine Beasts Ka Host Ban Gaya…" (1.04M). English examples include "My Sisters Ignored Me for 10 Years…" (916K) and "…So I Infected Myself With 138 Viruses" (175K). — [Yuva Recaps](https://www.youtube.com/watch?v=E50IP_WBxw4); YouTube Data API sample: it's yuva, [Yogiri Recap](https://www.youtube.com/watch?v=c4uxWvU7RRY), BillionaireGod
- **Thumbnails:** they are labelled composites, often cleaner art than the in-video panels. Typical elements are yellow arrows and labels ("ENEMY" / "MC ARMY", "MC" / "EX-GF", "NEW STUDENT!"), before-and-after splits ("BEFORE" / "AFTER", "SLAVE" / "MONARCH", "AT HOME" / "AT OFFICE"), status badges ("#COMPLETED", "#S1 COMPLETED") and part numbers ("1-14", "16"). — [Manhwa Fresh thumbnail](https://i.ytimg.com/vi/pjOoN03xa0k/hqdefault.jpg); [ManhwaDealer](https://i.ytimg.com/vi/U-k_Mr8q1sk/hqdefault.jpg); [Daily Manhwa Fresh](https://i.ytimg.com/vi/opbYhLf8jW0/hqdefault.jpg); [The Story Unfolds](https://i.ytimg.com/vi/PnBrjozh2cM/hqdefault.jpg); [Evergarden](https://i.ytimg.com/vi/obaZWVPr2Zc/hqdefault.jpg); [Manhwa Senpai](https://i.ytimg.com/vi/aQ0xKM2OCwQ/hqdefault.jpg)
- **Hook advice:** an August 2026 guide says to open with conflict or mystery, not a summary. It contrasts the weak "Today, I will explain this manhwa" with "He thought his life was over, until he woke up with a power that could change everything", and says to introduce the conflict without revealing the key moments. — [Techgili, 2026-08-28](https://techgili.com/how-to-build-a-manhwa-recap-channel-that-can-earn-10-per-1000-views/)
- **Packaging mismatch:** "if people click but leave quickly, your title or thumbnail may be creating expectations that the opening does not meet" (from a manhwa recap guide, via a search summary). — [Techgili](https://techgili.com/how-to-build-a-manhwa-recap-channel-that-can-earn-10-per-1000-views/)
- **Chapters:** only 9 of 113 long-form recaps had 3 or more timestamp lines. Where present, they mark parts or seasons:
  - The Story Unfolds: "0:00 - Part 1 (Marriage Proposal) … 01:19:51 - Part 3 (Office Romance) … 03:02:02 - Season 1 End" — [video](https://www.youtube.com/watch?v=PnBrjozh2cM)
  - HinKahaniX: "00:00 - First Part … 1:08:11 - Firth Part" — [video](https://www.youtube.com/watch?v=wQ2MvybTLnI)
- **Cumulative re-uploads with a "New Part" marker:**
  - Manhwa Outpost's 810-minute video lists "00:00:00 - Part 1 to 8 … 10:45:49 - New Part 15". — [video](https://www.youtube.com/watch?v=E4q9RTu5dXs)
  - Daily Manhwa Fresh uploaded "(1-14) Shadow Slave" (72m34s, 2026-10-22, description "New Part: 1:05:04"), then "(1-15) Shadow Slave" (82m15s, 2026-10-29). — [(1-14)](https://www.youtube.com/watch?v=opbYhLf8jW0)
  - Hasbic Manhwa: "Part 2 - 11:21:50". — [video](https://www.youtube.com/watch?v=oinSPqqrzqE)
  - Evergarden links a playlist and "Part 1 - 5". — [video](https://www.youtube.com/watch?v=obaZWVPr2Zc)
- **Hidden series names:** about 28 long-form descriptions say the name is in the pinned comment or the comments ("Name in the pinned comment below👇" from Manhwa Fresh; "Manhwa name: It's in the comments" from Frieren Manhwa). No long-form description in the sample linked an official platform (WEBTOON, Tapas, Naver, Kakao, Tappytoon, Lezhin, Manta). — [Manhwa Fresh](https://www.youtube.com/watch?v=pjOoN03xa0k); [Frieren Manhwa](https://www.youtube.com/watch?v=_xydUWNJnic)
- **Disclaimers:** about 40 of 113 long-form descriptions include a copyright disclaimer (for example "I Don't Own The Manhwa/Artwork/Comic… Please Feel Free To Contact Me Before Creating Copy Right Claim"), and about 10 cite "fair use" / "Section 107". — [Manhwa Fresh](https://www.youtube.com/watch?v=pjOoN03xa0k); [Akiel Runes](https://www.youtube.com/watch?v=TAPhcHn0rDM); [Hasbic Manhwa](https://www.youtube.com/watch?v=oinSPqqrzqE)
- **Scanlation and Patreon links:** KenRecaps' description promotes "kensscans.com" and a Patreon offering "Early chapters + Exclusive titles". — [KenRecaps](https://www.youtube.com/watch?v=cTQF3rj4zMk)
- **Shorts endings:** Shorts reveal the title at the end, for example the caption "THIS MANHWA IS CALLED" next to the Korean title logo. — [Manhwa Tease hq3](https://i.ytimg.com/vi/ksO7HaHbhJk/hq3.jpg)
- A 2026 guide's sample prompt asks for a recap ending "with a cliffhanger teaser for what comes next". — [FluxNote](https://fluxnote.io/guides/manhwa-webtoon-recap-channel)
- YouTube policy allows the "Same intro and outro for your videos, but the bulk of your content is different". — [YouTube Help, YPP policies](https://support.google.com/youtube/answer/1311392)

### Inferences
- A separate channel intro (logo sting) is not visible in any sampled still and is not mentioned in the guides. Combined with the advice to open on conflict, this suggests top recaps go straight into the story. This is unconfirmed, because the first seconds of these videos were not viewed.
- Story order looks chronological (chapter 1 onward, "Part 1 … Part 15") in compilations. Out-of-order cold opens could not be verified (see Gaps).
- Hiding the series name plausibly serves two purposes: it pushes comments (engagement) and makes the video harder for rights holders to find by title search. The second is my inference; no source states it.

### Gaps
- Hook wording in the first 5 to 30 seconds and whether channels cold-open on the climax could not be checked without transcripts or video. Both were out of scope, and no creator post documenting it was found.
- End-screen practice ("subscribe for part 2") was not observable. Only one mid-video subscribe graphic (KenRecaps) was seen.

## 4. Length strategy: chapters vs arcs vs multi-hour compilations

### Takeaway
On views, long-form recaps from 2025-2026 are dominated by multi-hour whole-series compilations, with a median of about 3 hours. A second, smaller cluster is the 10 to 20 minute review or commentary video or single-story Hindi recap. Three to ten minute recaps are rare among top performers, which puts a 3-minute horizontal recap in a gap between Shorts and long-form.

### Cited Findings
- **Duration buckets** among 200 recap-labelled videos in the sample: up to 1 min: 22; 1 to 3 min: 18; 3 to 10 min: 7; 10 to 20 min: 40; 20 to 60 min: 13; 1 to 3 h: 43; 3 to 6 h: 32; over 6 h: 25. — YouTube Data API sample (see Method note)
- **Long-form length:** among 113 recaps of 20 minutes or more, the median was 182 minutes (25th percentile 77 min, 75th percentile 322 min). The maximum was 2,690 minutes (about 45 h) from Magical Manhwa Recaps, at 1.08M views. — YouTube Data API sample; [Magical Manhwa Recaps 44h49m video](https://www.youtube.com/watch?v=eBhshOY6QY8)
- **Channel-level median video length** in the sample:

  | Channel | Subscribers | Median length |
  |---|---|---|
  | Manhwa Fresh | 645K | 273 min |
  | Mamoru Manhwa | 561K | 304 min |
  | Manhwa Outpost | 405K | 511 min |
  | Tobs Manhwa | 383K | 322 min |
  | ManhwaDealer | 274K | 191 min |
  | AniTiger | 81K | 477 min |
  | Magical Manhwa Recaps | 277K (687 videos) | 1,546 min |

  — YouTube Data API channel stats (2026-10-29)
- **Top long-form examples:**
  - Solo Leveling "Season 3-4… Complete Story" at 567 min (1.80M views) — [The Abyss Recap](https://www.youtube.com/watch?v=0xiSDXVdtc0)
  - "(Completed) He got into the Medieval Age…" at 2,152 min (1.69M) — [Manhwa Fresh](https://www.youtube.com/watch?v=pjOoN03xa0k)
  - "Global Freeze" chapters 1 to 550 at 810 min (1.14M) — [Manhwa Outpost](https://www.youtube.com/watch?v=E4q9RTu5dXs)
- **The 10 to 20 minute cluster:**
  - Commentary or analysis channels: Maki Ojin, "How One Villain BROKE Webtoon Forever", 18m29s, 1.39M — [video](https://www.youtube.com/watch?v=xS6ifImTiNc); Schikan, "BONES: The WORST Revenge Manhwa I've Read", 12m40s, 1.09M — [video](https://www.youtube.com/watch?v=b4KL405WjQE); Nenjuno, 10m41s, 589K — [video](https://www.youtube.com/watch?v=EuPaIIuG3hU)
  - Hindi single-story recaps: it's yuva, 14m53s, 2.36M.
  - YouTube Data API sample
- **Multi-part series** use part numbers in titles ("[Part-1]", "(1-14)", "(16)") and playlists. — [Evergarden](https://www.youtube.com/watch?v=obaZWVPr2Zc); [Daily Manhwa Fresh](https://www.youtube.com/watch?v=opbYhLf8jW0); AT Manhwa Hindi "[Part-1] He Revived Ancient Cooking…" (YouTube Data API sample)
- At least one channel brands itself on runtime: "10H Manhwa Recap" says every video is a deep dive "for a full 10 hours". — [10H Manhwa Recap channel](https://www.youtube.com/@10HManhwaRecap)
- **New channels grow fast on long formats:** Frieren Manhwa was created 2025-05-17 and had 174K subs and 172 videos. yuva explainop was created 2026-04-13 and had 429K subs and 213 videos. Manhwa Senpai was created 2025-12-29 and had 141K subs. — YouTube Data API channel stats
- A late-2025 video discusses "the reason [recap channels] started disappearing now" (5 min, 752 views). Its content was not viewed. — [zRoom, "The rise and fall of Manhwa Recap Channels", 2025-11-03](https://www.youtube.com/watch?v=a9hKDHzbt4E)

### Inferences
- Multi-hour compilations maximise watch time per click and work as background or sleep listening. That use is inferred, not documented: no source confirms viewer behaviour.
- Cumulative re-uploads, where each new part comes with the whole series again, recycle old footage into new uploads. That raises "repetitive content" exposure under YouTube's inauthentic-content rule (see section 7).
- A 3-minute recap competes in neither cluster. It is too long for the 59-second Shorts norm and far shorter than the long-form formats that win on views. For an original webtoon, the nearer peer is probably the episodic Short plus a periodic longer "season so far" compilation.

### Gaps
- No audience-retention or revenue data per format was available; the data is views only. Views per length are confounded by channel size and upload age.

## 5. Retention tactics

### Takeaway
Hard data on retention curves for recap videos is not public in anything I could find. What is observable: packaging with a promise and a twist, opening on conflict, cutaway memes and stock images as pattern interrupts, part numbering and cumulative recaps of earlier parts, cliffhanger teasers, and close-up-heavy visuals with music and SFX.

### Cited Findings
- **Pacing:** guides advise varying the pace: "slow down for important moments and move quickly through minor details", and end on a satisfying beat. — [Techgili, 2026-08-28](https://techgili.com/how-to-build-a-manhwa-recap-channel-that-can-earn-10-per-1000-views/)
- **Narration voice:** "energetic and conversational… like a fan talking to a fan", with voices at 1.1x speed. This is a vendor guide. — [FluxNote](https://fluxnote.io/guides/manhwa-webtoon-recap-channel)
- **Pattern interrupts seen in frames:** stock photo with a text label (Manhwa Outpost), emoji and stock-photo meme cutaways (Schikan), red arrows and circles (Takovara Shorts; Evergarden thumbnail), and a subscribe-button overlay mid-video (KenRecaps). — [Manhwa Outpost hq1](https://i.ytimg.com/vi/E4q9RTu5dXs/hq1.jpg); [Schikan hq2](https://i.ytimg.com/vi/b4KL405WjQE/hq2.jpg); [Takovara hq1](https://i.ytimg.com/vi/VgNygUalSsc/hq1.jpg); [KenRecaps hq3](https://i.ytimg.com/vi/cTQF3rj4zMk/hq3.jpg)
- **Recaps of earlier parts:** cumulative compilations ("Part 1 to 8" then "New Part 15") let new viewers start from chapter 1 and returning viewers jump to the new timestamp. — [Manhwa Outpost](https://www.youtube.com/watch?v=E4q9RTu5dXs); [Daily Manhwa Fresh](https://www.youtube.com/watch?v=opbYhLf8jW0)
- **Part 2 advice (TikTok-series guide, 2026):** open with a short recap for viewers who missed part 1, then end on a cliffhanger drawn from genuinely open story threads, not invented ones. — [DEV Community, TikTok series guide](https://dev.to/agentworkshop/how-to-plan-the-next-part-of-a-tiktok-series-so-part-2-viewers-arent-lost-2026-recap-callback-e1a)
- **Generic retention claims (not recap-specific, tool-vendor blogs, weakly sourced):**
  - "the largest single loss on the graph happens before the thirty-second mark" — [ViralHQ retention guide](https://viralhq.vercel.app/blog/retention-curves-guide)
  - losing over 40% in the first 30 seconds means "your intro needs work" — [Lenostube benchmarks](https://www.lenostube.com/en/youtube-audience-retention-average-good-and-best-benchmarks/)
  - for 6 to 8 minute animated videos, over 50% retention is strong and 35 to 50% average — [LongStories.ai](https://longstories.ai/blog/retention-benchmarks-animated-youtube-videos)
- **No ads on graphic opening (gaming):** YouTube's advertiser rules treat graphic game violence "in the thumbnail or in the first seven seconds" as no ads. That limits "cold open on the bloodiest moment" hooks for gaming, and the dramatized-violence rules apply to animated content. — [YouTube Help, advertiser-friendly guidelines](https://support.google.com/youtube/answer/6162278)

### Inferences
- With comment-bait and a hidden title ("name in the pinned comment"), recap channels trade transparency for engagement signals. An original webtoon creator does not need that tactic and can name the series openly.
- The "this weakest hunter…" style opener matches the dominant title formula (underdog, then twist, then overpowered), so the first line usually restates the title's promise right away. This is inferred from the titles and the hook advice, not from transcripts.

### Gaps
- I found no creator-posted retention graphs for manhwa or manga recaps on Reddit or elsewhere in the searches. Reddit threads did not surface. Typical curve shapes for recaps (for example, drops at part boundaries in long compilations) remain unverified.

## 6. Shorts and TikTok versions

### Takeaway
Recap Shorts are mostly about 30 to 60 seconds of full-bleed 9:16 close-ups with one- to three-word burned-in captions, a watermark, and a title reveal or cliffhanger at the end. A minority run 1 to 2 minutes, which YouTube has allowed since October 2024. "Part N" labelling is rare on YouTube Shorts in the sample but used on TikTok.

### Cited Findings
- **Length:** of 88 sampled videos of 3 minutes or less, 65 were 60 s or under and 23 were 61 to 180 s. The median for recap-labelled Shorts was 59 s. — YouTube Data API sample
- **Top Shorts:**
  - Oppa anime, 38 s, 10.77M views — [video](https://www.youtube.com/watch?v=JZu3VEdnIgg)
  - Manhwa Tease, "This Boy Was FORCED To Join The School Fight Club | Manhwa Recap", 51 s, 7.38M — [video](https://www.youtube.com/watch?v=ksO7HaHbhJk)
  - Takovara, 1m23s, 5.83M — [video](https://www.youtube.com/watch?v=VgNygUalSsc)
  - Akiel Runes, 1m09s, 2.27M — [video](https://www.youtube.com/watch?v=TAPhcHn0rDM)
  - WaifusToonz, 1m55s, 1.27M — [video](https://www.youtube.com/watch?v=NU3ZZmi_zUw)
- **Shorts length cap:** YouTube raised the maximum Short to 3 minutes for square or vertical videos uploaded from 2024-10-15 (older source, 2024). — [PetaPixel](https://petapixel.com/2024/10/04/youtube-shorts-expands-video-length-to-three-minutes/); [Gigazine](https://gigazine.net/gsc_news/en/20241004-youtube-short-video-length-3-minutes)
- **Descriptions:** Shorts descriptions often give the title and chapter range up front: 24 of 88 had "Name"/"Title" in the first 200 characters, for example "🎬NAME: Happy Face: From Slave to Arena Legend / CHAPTER: 1-58" and "🎬MANHWA NAME:- I Raised the Yandere Villain Empress / CHAPTER:- 20+". Only 7 of 88 linked to a full recap. — [Enir Manhwa](https://www.youtube.com/watch?v=Jsye9qpS8m8); [Recap Ronin](https://www.youtube.com/watch?v=8OFKMBvLkws); YouTube Data API sample
- **Hashtags:** about half of recap Shorts titles carry #manhwa and similar hashtags. "Part" appeared in 1 of 40 recap-labelled Short titles. — YouTube Data API sample
- **TikTok:** recap accounts post explicit multi-part series ("Part 2/3"). — [DEV Community TikTok series guide](https://dev.to/agentworkshop/how-to-plan-the-next-part-of-a-tiktok-series-so-part-2-viewers-arent-lost-2026-recap-callback-e1a) (cites Manhwa Flash's TikTok captions)
- **Shorts visual grammar:** full-bleed close-up, centred bold yellow caption, semi-transparent channel watermark in the lower middle, title reveal at the end. — [Manhwa Tease oar2](https://i.ytimg.com/vi/ksO7HaHbhJk/oar2.jpg), [hq3](https://i.ytimg.com/vi/ksO7HaHbhJk/hq3.jpg)
- **Overlap with edits:** many top "manhwa" Shorts are romance/BL/edit clips with music rather than narrated recaps ("#editfavmanhwa", "#bledit"). — YouTube Data API sample (BL fan girl, BL Lover, Manhwa Recommendation)

### Inferences
- A 3-minute vertical recap is technically a Short but sits far above the 59-second median. Cutting one 30 to 60 second hook Short per episode, pointing to the longer video, matches the dominant pattern.

### Gaps
- No TikTok-native data (lengths, view counts) was collected. TikTok discover pages returned no usable content, and I found no 2025-2026 creator write-up on TikTok recap tactics.

## 7. YouTube policy and legal risk (reused / inauthentic content, copyright, AI disclosure, advertiser rules) and the original-webtoon difference

### Takeaway
Recaps of other people's manhwa face three separate risks:
- **Monetisation:** the reused-content rule ("readings of other materials you did not originally create") and the inauthentic-content rule (slideshows, templated or mass-produced AI content), clarified on 2026-07-16.
- **Copyright:** a July 2026 US ruling in KADOKAWA's subpoena case found anime recaps that "describe and narrate" were not fair use, and Japanese courts have acted against recap and summary sites.
- **Ad suitability:** gore and sexualised thumbnails and titles.

A creator recapping their own original webtoon removes most of the copyright and reused-content risk, but still has to avoid "templated / mass-produced" patterns.

### Cited Findings
**Reused and inauthentic content (YPP)**
- **Renaming:** YouTube renamed "repetitious content" to "inauthentic content" on 2025-07-15. Not allowed under it:
  - "Image slideshows, templated storylines, or scrolling text with minimal or no narrative, commentary, or educational value"
  - "Similar or repetitive content with low educational value, commentary, narratives, or minimal variation across videos"
  - "AI-generated content made with generic or unoriginal templates giving the impression of mass production"

  Allowed: the "Same intro and outro… but the bulk of your content is different", and series with recurring characters where each video has a distinct storyline. — [YouTube Help, YPP policies](https://support.google.com/youtube/answer/1311392)
- **Reused content, not allowed:**
  - "Content that exclusively features readings of other materials you did not originally create"
  - "Clips of moments from your favorite show edited together with little or no narrative"
  - "Content downloaded or copied from another online source without any substantive modifications"
  - "Promotion of other people's content (even if you have permission)"

  The page adds: "This policy applies even if you have permission from the original creator." — [YouTube Help, YPP policies](https://support.google.com/youtube/answer/1311392)
- **Reused content, allowed:** "Edited footage from other creators where you add a storyline and commentary", "Edited footage with audio and visual effects on top of the video's reused content", and "Content that primarily features the uploading creator in the video". — [YouTube Help, YPP policies](https://support.google.com/youtube/answer/1311392)
- **July 2025 framing:** Rene Ritchie (YouTube) called the update "a minor update to YouTube's long-standing YPP policies" and said "There are no changes to YouTube's reused content policies on clips, compilations, reaction content." Coverage cited channels uploading "nearly identical narrated stories or slideshows with repeated narration" as targets (article dated 2025-07-11). — [Search Engine Journal](https://www.searchenginejournal.com/youtube-clarifies-monetization-update-targeting-spam-not-reaction-channels/550755/)
- **July 2026 update:** rolled out on 2026-07-16 to all YPP members. YouTube's trust and safety chief, Halprin, announced it on Creator Insider. It names three non-monetisable categories:
  1. generic, repetitive or template-based content easily made with AI, CGI or templates with little variation
  2. off-putting or distressing content
  3. AI personas of real people on sensitive topics

  Halprin said such videos are "very generic and don't really have a narrative arc and don't really show your creativity". A channel with too much of any category cannot monetize; no threshold is given. — [TechCrunch, 2026-07-20](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/)
- **Conflict to flag:** the YPP Help page as fetched on 2026-10-29 shows only the 2025-07-15 rename in its changelog and no July 2026 entry. Third-party blogs disagree on whether the rename happened in 2025 or 2026. TechCrunch and the Help page together support: rename in 2025, clarification in 2026. — [YouTube Help](https://support.google.com/youtube/answer/1311392); [Keepmonetized](https://keepmonetized.com/guides/reused-vs-inauthentic-content/); [CreatorBlade](https://creatorblade.com/blog/youtube-inauthentic-content-policy-2026-stay-monetized)
- **Recap-specific advice:** a recap tutorial channel's monetisation video (2025-07-16) frames the recap problem as the "reused content" rule. Its fixes are "Insightful Commentary: Add unique analysis that goes beyond just summarizing", dynamic zooms and pans, and "Smart AI Voice Use" (with an ElevenLabs affiliate link). — [Manhwa Tales, "HOW TO MONETIZE MANHWA MANGA RECAP CHANNELS"](https://www.youtube.com/watch?v=7o2q4-GcfOg)
- A 2026 guide: "Adding narration alone does not automatically make copyrighted material safe to use." — [Techgili](https://techgili.com/how-to-build-a-manhwa-recap-channel-that-can-earn-10-per-1000-views/)

**Copyright cases and publisher action**
- **KADOKAWA v. three Korean anime-recap YouTubers (N.D. Cal.):**
  - KADOKAWA sought a DMCA subpoena in January 2026. Judge Trina L. Thompson denied the motion to quash on 2026-07-17, finding the videos "describe and narrate" the works, "reproduce significant portions", and were not sufficiently transformative.
  - The works were *A Ninja and an Assassin Under One Roof*, *Oshi no Ko* and *Once Upon a Witch's Death*. The channels had about 350K to over 500K subs each. One used roughly 15% of an episode; one used a mascot with TTS dialogue.
  - The creators linked to the licensed platform Laftel (114,494 click-throughs), had earlier won reinstatement through counter-notices, and have appealed to the Ninth Circuit.
  - The ruling is not a full merits decision. — [TorrentFreak, 2026-08-14](https://torrentfreak.com/court-rejects-fair-use-claim-orders-youtube-to-unmask-anime-recap-channels/); [CBR, 2026-08-16](https://www.cbr.com/kadokawa-anime-youtuber-crackdown/); [GIGAZINE](https://gigazine.net/gsc_news/en/20260817-fair-use-anime/)
- **Conflict to flag (Barnes):** TorrentFreak says the judge cited *Barnes v. YouTube*, "a February ruling", where a channel narrating chapters of a copyrighted book was denied fair use. A legal blog covering *Barnes v. Sanchez* (N.D. Cal., 2026-07-02; 15 videos "each of which narrated a chapter from his book") reports only that YouTube was dismissed and the direct-infringement claim against the YouTubers proceeds, and says nothing about fair use. The February fair-use ruling could not be verified. — [TorrentFreak](https://torrentfreak.com/court-rejects-fair-use-claim-orders-youtube-to-unmask-anime-recap-channels/); [Eric Goldman blog, 2026-07-05](https://blog.ericgoldman.org/?p=29011)
- **Japan, Tokyo District Court (April 2026):** convicted Wataru Takeuchi for a monetised site of written plot summaries (*Overlord*, *Godzilla Minus One*). He received a suspended 18-month sentence and a ¥1M fine; the site reportedly earned about ¥36M in ad revenue in 2023. — [TorrentFreak](https://torrentfreak.com/court-rejects-fair-use-claim-orders-youtube-to-unmask-anime-recap-channels/)
- **Shogakukan (Japan):** obtained a provisional order to unmask a YouTuber who posted recaps of the manga *Ushijima the Loan Shark*. Per CBR's summary, the court said narration-only recaps can infringe because they replace buying the original. The date was not given in the source; treat it as older. — [CBR](https://www.cbr.com/kadokawa-anime-youtuber-crackdown/)
- **Older (2022):** KADOKAWA sought YouTube identities of seven alleged infringers of manga content. — [TorrentFreak, 2022-04-13 (older)](https://torrentfreak.com/manga-pirates-warned-that-kadokawa-seeks-their-identities-from-youtube-220413/)
- **Strikes on a manhwa recap channel:** Reverse Manhwa posted that it got one copyright strike and deleted its videos about one manhwa to avoid a second. The post is about late 2025 by search metadata; details unverified. — [Reverse Manhwa community post](https://www.youtube.com/post/UgkxCsrZ6YBWd0e6Cm6FhpAnZQr67yZS2OrM)
- **Korean platforms:** Kakao Entertainment's anti-piracy team says it is widening enforcement to secondary or derivative works (2차 창작물). Naver Webtoon joined ACE and used US subpoenas that stopped about 150 piracy sites (2025). No action specifically against YouTube recap channels was found. — [Dailian interview](https://www.dailian.co.kr/news/view/1489877/%EC%9D%B8%ED%84%B0%EB%B7%B0-%EB%B6%88%EB%B2%95%EC%9B%B9%ED%88%B0-%EC%B9%BC-%EB%B9%BC%EB%93%A0-%EC%9D%B4-%EB%82%A8%EC%9E%90%EC%B9%B4%EC%B9%B4-2025); [Platum](https://platum.kr/archives/268233)
- **Upstream piracy shutdowns (2026):** Bato.to shut in January 2026 and TuMangaOnline was dismantled in April 2026. These are site takedowns, not YouTube actions, but such sites are typical panel sources. — [Wikipedia: Bato](https://en.wikipedia.org/wiki/Bato_(website)); [Wikipedia: TuMangaOnline](https://en.wikipedia.org/wiki/TuMangaOnline)

**AI disclosure**
- Disclosure is required only for content that "seems realistic": a real person saying or doing something they didn't, altered real events or places, realistic scenes that didn't happen.
- Not required: "AI-generated animation in a fully animated video", fantastical scenes, caption creation, "cloning your own voice for voiceovers", and using AI for a script, thumbnail or title.
- "Disclosing AI content alone won't limit a video's audience or impact its eligibility to earn money." Consistent non-disclosure can bring labels, removal or YPP suspension.
- The page does not directly address synthetic narrator voices.

— [YouTube Help, altered or synthetic content](https://support.google.com/youtube/answer/14328491)

**Advertiser-friendly rules**
- **Violence:** animated or fictional content falls under the "dramatized" rules. "Mild violence with minimal blood" earns full ads. "Dramatized content displaying severe and shocking injuries" earns limited ads. Content focused on blood, gore or injury with little context earns no ads. Graphic game violence "in the thumbnail or in the first seven seconds" earns no ads.
- **Titles and thumbnails:** the policies apply to "all portions of your content". Sexualised titles or thumbnails earn limited ads. Thumbnails with sexual content, or strong profanity in titles or thumbnails, earn no ads.

— [YouTube Help, advertiser-friendly guidelines](https://support.google.com/youtube/answer/6162278)
- **Sexualised titles exist among top recaps** ("Son and Stepmother STUCK in an Elevator..", 650K; "Lonely Boy Smash Baddie With The Second Fattest @ss…", 1.80M). Their ad status is unknown. — [Losweko](https://www.youtube.com/watch?v=Og8kH4_NFIk); [TaylorTheTeacher](https://www.youtube.com/watch?v=9WiWuPJxAZI)

**Original webtoon recapped by its own creator**
- WEBTOON CANVAS creators keep ownership of their work. The CANVAS Terms (updated 2026-01-06) limit WEBTOON's own derivative use to marketing and promotion. — [WEBTOON CANVAS Terms of Use](https://www.webtoons.com/en/terms/canvasTermsOfUsePolicy); [WEBTOON notice](https://www.webtoons.com/en/notice/detail?noticeNo=2534)
- YouTube's reused-content exclusions target material "you did not originally create" and "other people's content". The allowed list includes "Content that primarily features the uploading creator". — [YouTube Help, YPP policies](https://support.google.com/youtube/answer/1311392)

### Inferences
- For third-party manhwa, the risks stack up:
  - the rights holder can file a takedown or strike;
  - the KADOKAWA ruling, though not a merits decision and under appeal, weakens the "narration makes it fair use" argument in the US;
  - YPP review can find a channel "reused" or "inauthentic", especially where it reads plot over cropped panels, uses templated AI voices, or makes cumulative re-uploads.

  The common disclaimers ("I don't own…", "Section 107") carry no legal weight in themselves. That is my inference; no source says they protect channels.
- For an original webtoon recapped by its own creator:
  - copyright and reused-content risk are essentially removed, because the creator owns the panels (unless they signed an exclusive licence, such as a platform Originals contract);
  - the remaining exposure is the inauthentic-content rule if episodes look templated or mass-produced with little variation, and ad suitability for violence and thumbnails;
  - AI disclosure is likely not required for clearly non-realistic manga art, or for AI help with scripts and thumbnails. A realistic synthetic voice of a real person would be a different matter.

  Keeping source files, putting an "original series by [creator]" line in the description and linking the creator's own WEBTOON page strengthens the ownership position if a third-party re-upload claims the art. That last point is inference.

### Gaps
- No Content ID behaviour for still manhwa panels (whether publishers fingerprint webtoon art) was documented in any source found.
- No verified 2025-2026 terminations of large manhwa recap channels were found, only a single-strike community post and an unviewed "rise and fall" video.
- YouTube's own official July 2026 wording (Creator Insider transcript or Help Center changelog) was not found. The 2026 detail rests on TechCrunch.
