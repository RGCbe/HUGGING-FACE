# Narration and audio of top manga/manhwa/webtoon recap channels (2025-2026)

Research date: 2026-10-29. Method: web search and fetch, plus public YouTube Data API v3 metadata only (search.list, videos.list, channels.list; about 790 quota units in total, no video, audio or captions downloaded). The API sample covers 262 videos from six searches ("manhwa recap" long, medium and short, "manga recap" long, "webtoon recap", recent "manhwa recap"; published 2025-01-01 or later, sorted by views), plus a 50-video "manga dub" search. 177 of the 262 have "recap", "explained" or "summary" in the title. Throughout, "own API sample" means my own count from that data ([API reference](https://developers.google.com/youtube/v3/docs/search/list)). Reddit was not reachable: the search tool blocks reddit.com, and the YouTube comments endpoint refused this token for lack of the `youtube.force-ssl` scope. So viewer opinion below is thinner than planned. The owner sees the voiceover as the main thing, so **sections 9 (the voice spec) and 10 (the script written for the voice) are the deepest sections**. Section 8 covers his two reference videos and compares dubs with narrator recaps.

## 1. Narration voice: AI or human, which tools and voices, one fixed brand voice?

### Takeaway
Top English manhwa recap channels almost never say in public which voice they use. None of the big channels in the sample credits a voice tool. The clearest signal is that the biggest narrator's voice has been copied: a community voice clone called "FRESH MANHWA" on Fish Audio, described as a calm, deep, resonant male voice that is "clear and measured" with "a touch of mystery", has been used by about 3,400 creators. Every channel sticks to one narrator voice as its sound, and smaller channels copy the leader's voice rather than inventing their own.

### Cited Findings
**What the top channels disclose (own API sample)**
- Across 262 recap-search videos, only 1 description mentioned ElevenLabs and 1 mentioned CapCut, and both were the same *tutorial* video (Albert AI, "Generating AI Voiceovers With ElevenLabs … Editing Everything in CapCut"). No top recap channel credited a voice tool. 0 descriptions mentioned Murf, Speechify, Play.ht or "TTS". — [Albert AI tutorial](https://www.youtube.com/watch?v=XQaMZDUHBBI); own API sample.
- Only 2 descriptions mentioned "AI voice" at all, and both were tutorials. Outside the sample, one channel says outright: "AI voice narration is used only for clear and consistent audio" (Daily Summary, 4h recap, 269,750 views, Oct 2026). — [Daily Summary video](https://www.youtube.com/watch?v=Se-kPzsE1As)
- Another channel says "All my stories are original and assisted by AI" (MovieStar Recaps, Oct 2026). — [MovieStar Recaps video](https://www.youtube.com/watch?v=YKuM72DHzW0)
- The largest English long-form recap channels share almost identical boilerplate descriptions: a disclaimer, the title "in the pinned comment", and the same copied tag block ("the manhwa man, high school mercenary, teenage mercenary …"). This appears on Manhwa Fresh, Mamoru Manhwa, AniTiger, The Librarian, Noob Manhwa and Tobs Manhwa. None names a voice or music source. — [Manhwa Fresh video](https://www.youtube.com/watch?v=9OSXs52aICI), [Mamoru Manhwa video](https://www.youtube.com/watch?v=YGLNNUaMju0), [Tobs Manhwa video](https://www.youtube.com/watch?v=0w1FjXmgX0w), [The Librarian video](https://www.youtube.com/watch?v=jFdoZ-LScKQ)
- Tobs Manhwa's description says "i do all my scripts while reading", which implies a hand-written script. The voice is not stated. — [Tobs Manhwa video](https://www.youtube.com/watch?v=0w1FjXmgX0w)

**Manhwa Fresh, the channel owner's reference video**
- "He's a Trash Prince Hated by Everyone, but Only He Can Save His Kingdom! - Manhwa Recap": 2h05m49s, posted 2026-10-27, 169,134 views, 3,363 likes and 159 comments when fetched on 2026-10-29. Audio language en-US. The description gives no voice or music credit; the manhwa's name is "in the pinned comment"; it links a Patreon. — [video](https://www.youtube.com/watch?v=9OSXs52aICI) (API metadata)
- Channel: 645K subscribers, 240 videos, 122.2M total views, created 2023-05-29, country US. Its top 2025-2026 videos in the sample are 1,565,623 views (291 min) and 1,551,522 views (448 min). It had 18 videos in the sample, more than any other channel. — [Manhwa Fresh channel](https://www.youtube.com/channel/UCz3IjVYoX-tmmPPTedhXQEQ); own API sample
- Fish Audio hosts a community voice clone titled "FRESH MANHWA" (creator listed as Yasir Majeed). Fish Audio describes it as "calm and professional male voice with a deep, resonant tone", "clear and measured, with a touch of mystery", tagged young-sounding and for storytelling and narration. It has been used by over 3,400 creators. (This comes from search-result snippets; a direct fetch of the page returned 404.) — [Fish Audio "FRESH MANHWA"](https://fish.audio/m/7714042439c24509ba4ef61c53671799/)
- I found no source saying whether Manhwa Fresh's own narration is a human recording, an AI voice, or a clone of a human. See Gaps.

**Named AI voices that guides and vendors recommend**
- ElevenLabs' own blog (published March 2025, updated October 2026) names these voices for faceless YouTube: Dan ("measured, serious", documentaries), Bill ("weathered, textured", true crime and storytelling), Robert (calm explainer), Nichalia (educational), Alex ("upbeat, energetic male", Shorts and gaming), Allison (bright, for lists and reactions), Emma and Amelia (kids). It also offers Instant Voice Cloning from about 1 minute of clean audio. — [ElevenLabs blog](https://elevenlabs.io/blog/the-5-best-ai-voices-for-youtube-automation-and-faceless-videos)
- Third-party roundups most often name Rachel (clear, warm), Adam (deep, authoritative; "most popular male voice" for AI and tech channels), David Castlemore and "David, British Storyteller" (mystery, thriller, storytelling), and Dan, Bill and Josh (documentary). They add that Antoni has been retired. These are affiliate-style blogs. — [mivicai](https://mivicai.com/best-elevenlabs-voices-for-faceless-youtube-channels/), [nerdynav](https://nerdynav.com/elevenlabs-review/), [aivoicereview](https://aivoicereview.com/blog/best-elevenlabs-voices-2026)
- A lawsuit alleges that ElevenLabs' "Adam" and "Bella" voices are based on two voice actors' voices. This is an allegation, not a ruling. — [The Voice Realm](https://www.thevoicerealm.com/blog/a-look-into-the-elevenlabs-lawsuit/)
- YTVoice.app, a vendor page for anime recap channels (undated; site © 2024-2026), names these voices: Dave ("sounds like a fan explaining the arc to you", for arc and season recaps), Liam ("hits the hook hard and keeps momentum", for fast recaps and Shorts), Jeremy ("excited and high-energy", for fight breakdowns), Sam ("raspier tone that matches heavier material", for seinen) and Aria (female, expressive). — [YTVoice.app](https://ytvoice.app/use-cases/anime-recap-youtube)
- FluxNote's 2026 guide to manhwa recap channels (March 9, 2026) recommends "an enthusiastic, fast-paced narration voice", its "Alex" or "Jordan" voices at 1.1x speed, and a tone that is "excited and conversational like a fan talking to a fan". — [FluxNote guide](https://fluxnote.io/guides/manhwa-webtoon-recap-channel)
- Fish Audio also hosts an "Anime recap" community voice: English, male, middle-aged, 435 uses. — [Fish Audio "Anime recap"](https://fish.audio/m/53f5f830ca6145459d70fda879245e80/)
- Fish Audio's newer "Drama 3" model is marketed for "multi-character scenes and long-form content". — [Fish Audio blog](https://fish.audio/blog/fish-audio-drama-3/)
- Tools that make recaps end to end (Magarecap, RecapManga Voice Studio, RecapSynth) bundle AI voiceover. Magarecap's page only says "choose a voice, listen to a sample" and names no voices. — [Magarecap](https://magarecap.com/), [RecapManga blog, June 2026](https://recapmanga.com/blog/manhwa-recap-scripts-ai-guide)
- Human voice is also on sale: Fiverr gigs offer manhwa or anime recap voiceover from about $5, and full recap production from $20. — [Fiverr listing via search](https://block.fiverr.com/gigs/manhwa-recap?page=2)

### Inferences
- The leading English recap sound is a **single, calm-to-measured, deep or low-mid male narrator**, not a hype voice. The "FRESH MANHWA" clone description and its 3,400+ uses are the best evidence, and they point to low pitch, steady delivery and a slightly mysterious colour. Vendor guides push "energetic" and "fan-to-fan" voices, but the most-watched channel is described the opposite way. A small channel should test both styles. My reading is that the calm, deep storyteller sound is what viewers associate with "a proper manhwa recap".
- Because the voice is the brand, top channels keep one narrator across hundreds of hours. Channels copying Manhwa Fresh's voice through clones shows that the voice itself is seen as valuable.
- Not disclosing tools appears to be deliberate. Given the July 2025 "inauthentic content" policy (see section 7), channels avoid drawing attention to AI use.

### Gaps
- Whether Manhwa Fresh (or Frieren Manhwa, Mamoru, Tobs, Outpost) uses a human narrator, an ElevenLabs stock voice, or a custom clone. No public statement was found, and audio analysis was out of scope.
- Which CapCut text-to-speech voices recap channels use. I found no source naming CapCut voices for manhwa recaps.
- Usage numbers for ElevenLabs voices in this niche. The ElevenLabs help article on popular voices returned 403.

## 2. Point of view and script style

### Takeaway
English top-tier recaps are framed in **third person** ("He …"), and their titles state the premise in the style "X happens, but Y". First person ("I …") is common in **Hindi** recaps and in Japanese-style **manga dubs**, where the protagonist speaks. Guides recommend summarising rather than reading every speech bubble, crediting each quoted line to its speaker, and ending on a cliffhanger.

### Cited Findings
- Title point of view in English recap titles (own API sample; titles are only a proxy for the narration): 63 of 146 use He or She, and 20 use I, My or Me. Among the 40 most-viewed English recaps of 10 minutes or more: 19 He/She, 2 first person. — own API sample; e.g. [Manhwa Fresh](https://www.youtube.com/watch?v=gecmpeZXDos) "He Copies the Skills of Any Hunter with a Single Touch!", [Frieren Manhwa](https://www.youtube.com/watch?v=_xydUWNJnic)
- Hindi recap titles: 13 of 31 are first person ("Maine Ghar Ko Bana Diya…" means "I turned my house into…"; "Main 9 Divine Beasts Ka Host Ban Gaya" means "I became the host of 9 divine beasts"), against 12 using He/She. — [yuva explainop](https://www.youtube.com/watch?v=MbGvwZqwM14), [yuva explainop 2](https://www.youtube.com/watch?v=vE3H7IP5UOs); own API sample
- English manga-dub titles are in first person, taken from Japanese light-novel-style premises ("[Manga Dub] The cool beautiful girlfriend was hugging my best friend..."). — [Kanon's RomCom Mangas](https://www.youtube.com/channel/UCG0bIjs1DXYKvaCO4t6irAQ); own API sample
- RecapManga (June 2026): use "a limited selection of panels — the beats your commentary actually needs"; "Lead with analysis, reaction or criticism, not a panel-by-panel readthrough"; attribute lines so narration doesn't become "a wall of unattributed quotes". It lists five styles: Commentary, Educational, Humorous, Narrative and Dramatic. — [RecapManga blog](https://recapmanga.com/blog/manhwa-recap-scripts-ai-guide)
- FluxNote (March 2026): cover the main plot events and character development, use a fan-to-fan conversational tone, and end with a cliffhanger teaser. It also warns that viewers in this niche "notice inaccuracies", so check fan wikis. — [FluxNote guide](https://fluxnote.io/guides/manhwa-webtoon-recap-channel)
- Intros: the descriptions of top channels open with the title being "in the pinned comment" and a business email, not a host persona (Manhwa Fresh, Frieren Manhwa: "Manhwa name: It's in the comments"). Mamoru's description signs off "Mamoru here". — [Manhwa Fresh](https://www.youtube.com/watch?v=9OSXs52aICI), [Frieren Manhwa](https://www.youtube.com/watch?v=_xydUWNJnic), [Mamoru Manhwa](https://www.youtube.com/watch?v=YGLNNUaMju0)
- A commentary sub-style exists alongside plain recaps. Schikan's "BONES: The WORST Revenge Manhwa I've Read" (1.09M views) is opinion-led and comedic ("it's really funny, just how bad it truly is"). — [Schikan video](https://www.youtube.com/watch?v=b4KL405WjQE)

### Inferences
- For an English channel that wants to sound like the top recaps: third-person narration with a past/present mix, and the protagonist's key lines quoted with "he says" attribution. Paraphrase most dialogue rather than reading every bubble.
- First-person "I woke up as…" narration is a different genre signal. It sounds like Hindi recaps or Japanese manga dubs, not the US/EN long-form recap leaders.

### Gaps
- Whether top videos open with a spoken channel intro ("Hello friends…") or start straight in the story. That needs the audio or captions, which were out of scope. Tense, joke frequency and the share of dialogue read aloud are also unmeasured.

## 3. Pacing: words per minute, pauses, chapters per minute

### Takeaway
No source measures recap channels' words per minute. General long-form voiceovers measure a median of about 166 WPM, and recap guides push "brisk" delivery with 1.1x voice speed. Long recaps are extremely long (median about 97 minutes, often 2 to 13 hours), which forces heavy compression: about 1.5 minutes of video per chapter in one 13.5-hour recap.

### Cited Findings
- OverseerOS measured 53 long-form voiceovers (Sept 2025 to Oct 2026, 3 to 30 minutes): median 166.5 WPM, middle half 159.7 to 177.4, 10th to 90th percentile 149.4 to 186.4. These are not recap-specific, and pauses are included in the figure. It also notes that AI narration "often has fewer" breaths and hesitations than humans, so it runs shorter. — [OverseerOS](https://www.overseeros.com/blog/youtube-script-length-word-count)
- Common planning figures are 130 to 165 WPM, with 150 WPM as the default. — [OverseerOS](https://www.overseeros.com/blog/youtube-script-length-word-count), [flowshorts](https://flowshorts.app/blog/words-per-minute-speaking)
- FluxNote recommends 1.1x voice speed and "energetic" pace. YTVoice says AI voice keeps a "brisk, dynamic pace" across long recaps. — [FluxNote](https://fluxnote.io/guides/manhwa-webtoon-recap-channel), [YTVoice.app](https://ytvoice.app/use-cases/anime-recap-youtube)
- ElevenLabs: for Shorts, use a "quick, natural pace", and articulation should hold up at 1.5x playback on phone speakers. — [ElevenLabs blog](https://elevenlabs.io/blog/the-5-best-ai-voices-for-youtube-automation-and-faceless-videos)
- Video lengths in the own API sample (147 recap-titled videos of 4 minutes or more): median 97.3 minutes, middle half 19 to 228 minutes. 71 of 147 run over 2 hours, 20 run 1 to 2 hours, 39 run 10 to 30 minutes. Example: Manhwa Outpost, 810 minutes, chapters 1-550, 1,136,671 views. That works out to about 1.5 minutes per chapter. — [Manhwa Outpost video](https://www.youtube.com/watch?v=E4q9RTu5dXs); own API sample
- English manga dubs are much shorter: mostly 13 to 31 minutes (Kanon's, Sarubedo, Runa's, Kawaii). The reference Akatsuki video is 21m03s. — own API "manga dub" sample; [Akatsuki video](https://www.youtube.com/watch?v=EZ8X1glKoMM)

### Inferences
- A sensible target for an English recap narrator is about 155 to 175 WPM, with short beat pauses (about 0.3 to 0.8 s) after reveals. This is the general long-form norm. Calm, deep narrators like the Manhwa Fresh style probably sit at the lower end, with more pauses; the Shorts style sits higher.
- A recap moves fast through the story (about 1 to 2 minutes per chapter), but the voice itself does not race. The speed comes from cutting content, not from talking fast.

### Gaps
- Measured WPM or panels per minute for any named recap channel. That would need captions or audio, which were out of scope.

## 4. Music

### Takeaway
Few channels credit music. Those that do use free "no copyright" beds from YouTube creators or sites: chill lo-fi hip hop (massobeats), kawaii pop (Piki), funky house (tubebackr), and Chosic free music. They do not use epic orchestral stems. Many top channels give no credit and use a blanket "all footage, music & images belong to their respective owners" fair-use notice. Mixing guides say to keep music about 18 to 24 dB under the voice, with W3C's rule of at least 20 dB as a safe anchor.

### Cited Findings
- 16 of 262 descriptions mention "music". Credited examples:
  - Gido Cuni Mahwa: "[No Copyright Background Music] Chill Luxury Vintage Hip Hop Beat sable by massobeats" (377,731 views, 1h29m); "Cute Kawaii Fun Kids Positive Intro Beat 3pm, moshi moshi by Piki" (305,690 views, 4h49m); "Funky, Soulful, House No Copyright Music Believe In You by tubebackr". — [video 1](https://www.youtube.com/watch?v=JMw7NsRdW3E), [video 2](https://www.youtube.com/watch?v=JKopzR_gDDk), [video 3](https://www.youtube.com/watch?v=QlSRmvZxDhA)
  - Schikan: "Credits: Music: https://www.chosic.com/free-music/all/". — [Schikan video](https://www.youtube.com/watch?v=b4KL405WjQE)
  - Takovara (5.8M and 4.3M views): "All footage, music & images used belong to their respective companies" (fair-use notice, no track names). — [Takovara video](https://www.youtube.com/watch?v=VgNygUalSsc)
  - Comic-dub creator DeadJosey: "Voice: @DeadJosey … Music: @junemay88junemay88". — own API manga-dub sample, [Deadjosey channel](https://www.youtube.com/channel/UCoxSGpW1YLvSjioonRaLbBg)
- 42 of 262 descriptions cite "fair use" and 70 have copyright disclaimers. — own API sample
- Chosic epic tracks are "free to use with attribution even commercially". Paid packs on Gumroad provide a licence certificate for Content ID disputes. — [Chosic epic](https://www.chosic.com/free-music/epic/), [Gumroad pack](https://basspartout.gumroad.com/l/rlsrX)
- FluxNote says to "add narration voiceover and background music" but gives no genre or level. — [FluxNote](https://fluxnote.io/guides/manhwa-webtoon-recap-channel)
- Levels: guides suggest music about 18 to 24 dB below the voice during speech (ranges given run from 15 to 25 dB); one documentary analysis found 24 to 31 dB. W3C G56 recommends non-speech sound at least 20 dB below speech. Ducking of about 6 to 10 dB with a 300 to 600 ms release is suggested. — [Umbrella Creators](https://umbrellacreators.com/blog/background-music-volume-under-voiceover), [W3C G56](https://www.w3.org/WAI/WCAG20/Techniques/general/G56), [MusicVivo](https://musicvivo.com/blog/music-under-voiceover), [OverseerOS](https://www.overseeros.com/blog/background-music-volume-under-voiceover)

### Inferences
- The multi-hour recaps seem to use one or a few looping, low-key beds (lo-fi, chill hip hop, light pop). The music is not scored scene by scene, and its job is to fill silence under a very long narration. Mood-matched cues (tense, sad, epic) are more likely in shorter, edited recaps and Shorts.
- For a small channel: use licensed or self-made beds, keep them at least 20 dB under the voice, and switch the cue at story-act changes rather than every scene.

### Gaps
- Whether top channels (Manhwa Fresh, Frieren, Mamoru) switch music by mood. They credit nothing, and the audio was not analysed.
- Measured LUFS of the music bed in actual top recaps.

## 5. Sound effects

### Takeaway
Sound effects are expected but sparse. Creators mention adding whooshes and sparks to match visual effects (glow, electricity, zooms). One channel promised that "the next recap will have sound effects as well!", which suggests viewers notice when they are missing. No source gives frequency, or a convention for the "level-up" chime on system windows.

### Cited Findings
- KenRecaps (July 2025): "the next recap will have sound effects as well!" in the description of a recap made without them. — [KenRecaps video](https://www.youtube.com/watch?v=ZJ1ub_26s8A)
- The Toolify guide (older, about 2025) suggests syncing panels to narration, zooming into the most expressive part of each panel, and adding electricity or glow effects with matching whooshes and sparks. — [Toolify guide](https://www.toolify.ai/ai-news/creating-engaging-manhwa-recaps-a-stepbystep-guide-3528091)
- Editor SFX packs sold for this kind of edit contain "Whooshes, Risers, Camera Shutters, Keyboards, Mouse Clicks, Gears, Slices". — [Hornet Media pack](https://hornetmedia.gumroad.com/l/editpack)
- Magarecap applies "pan, zoom, and reveal" motion to every scene. Sound is not described. — [Magarecap](https://magarecap.com/)

### Inferences
- A practical rule is one short SFX per visual "event": a whoosh on panel transitions or zooms, an impact on hits, a shimmer or chime on system windows. Keep them under the voice and avoid stacking them on every panel. This follows from the visual-effect pairing above but is not measured.

### Gaps
- SFX frequency per minute in top recaps, and whether system-window "ding" chimes are standard. No source found.

## 6. Loudness and mixing norms

### Takeaway
Aim for about -14 LUFS integrated, with true peak around -1 dBTP. Keep the voice clearly on top, with music at least 20 dB under it during speech. YouTube turns louder uploads down toward about -14 LUFS, so mastering hotter gains nothing.

### Cited Findings
- YouTube lowers louder content toward about -14 LUFS. — [Wikipedia: Audio normalization](https://en.wikipedia.org/wiki/Audio_normalization)
- Guides converge on -14 LUFS for YouTube. One suggests voice peaks around -12 to -6 dB, with music lower during speech and higher in intros, outros and b-roll. — [Pure Audio Insight](https://pureaudioinsight.com/blogs/content-production/perfect-youtube-audio-levels-creators-technical-guide), [MusicVivo](https://musicvivo.com/blog/music-under-voiceover)
- A bed about 20 to 25 dB below a voice averaging about -16 LUFS short-term fits a -14 LUFS master. — [MusicVivo](https://musicvivo.com/blog/music-under-voiceover)
- Manga-dub casting calls ask for "a decent sounding mic, no background noise/a quiet recording space". — [CastingCall.club (Nov 2023, older)](https://www.castingcall.club/projects/voice-actors-needed-for-manga-dubs)
- Japanese manga-video studios offer casting, recording and 整音 (audio clean-up and mastering) as a single package. — [Digital Shokunin](https://digishoku.co.jp/video/)

### Inferences
- A standard voice chain (general audio practice, not sourced in this research): high-pass about 80 Hz, gentle EQ for presence at 2 to 5 kHz, de-esser at 5 to 8 kHz, about 3:1 compression with 3 to 6 dB of gain reduction, a limiter at -1 dBTP. Music ducked by sidechain.

### Gaps
- Measured loudness or EQ of any named recap channel. No published measurements found.

## 7. What viewers and creators praise or complain about

### Takeaway
Direct viewer quotes could not be gathered here: Reddit was blocked and the comments API needs a scope this token lacks. The indirect signals all point the same way. AI voices carry a stigma that creators try to defuse with disclaimers or by dropping AI entirely. Accuracy errors are noticed by an engaged fan base. YouTube's July 2025 "inauthentic content" rule targets templated, mass-produced output rather than AI voice as such.

### Cited Findings
- Anime Therapist (33.7K subs, comic-dub channel): "NO MORE AI VOICES OR ANY GENERATIVE AI WILL BE USED IN MY VIDEOS. I apologize for ever using them." — [Anime Therapist channel](https://www.youtube.com/channel/UCGaZzFFejptMje4j93BaUvg) (channel About text via API)
- Daily Summary's defensive disclaimer, "AI voice narration is used only for clear and consistent audio", shows that creators expect criticism. — [Daily Summary video](https://www.youtube.com/watch?v=Se-kPzsE1As)
- Amazon pulled AI-generated English anime dubs after ridicule. Critics called the voices flat and awkward, and the National Association of Voice Actors called them "AI slop". (I did not confirm the exact date from the article.) — [AOL report](https://www.aol.com/articles/amazon-removes-ai-generated-anime-070348147.html)
- The Toolify guide frames a "robotic voiceover" as the mark of a low-effort recap. — [Toolify guide](https://www.toolify.ai/ai-news/creating-engaging-manhwa-recaps-a-stepbystep-guide-3528091)
- Vendors sell against the robotic sound: YTVoice markets voices for anime and manga channels "without sounding robotic". ElevenLabs recommends pronunciation dictionaries to fix mispronounced names and terms. — [YTVoice.app](https://ytvoice.app/use-cases/anime-recap-youtube), [ElevenLabs blog](https://elevenlabs.io/blog/the-5-best-ai-voices-for-youtube-automation-and-faceless-videos)
- FluxNote: viewers in this niche are "passionate and notice inaccuracies". — [FluxNote](https://fluxnote.io/guides/manhwa-webtoon-recap-channel)
- YouTube renamed "repetitious content" to "inauthentic content" on July 15, 2025, covering mass-produced or templated content. Commentators say the rule targets templates, not AI as such. — [Gulf News](https://gulfnews.com/technology/youtube-updates-monetisation-policies-ai-and-repetitive-content-ban-begins-july-15-1.500192660), [Medium analysis](https://mateostarcevicfilipovic.medium.com/youtube-quietly-demonetizes-faceless-ai-channels-since-july-2025-30b3d2daaf2e)
- An older signal (2012): forum users said they stopped videos as soon as they heard synthesized voices. — [AnandTech forum (2012, old)](https://forums.anandtech.com/threads/whats-with-the-robotic-voices-on-youtube-videos.2451856/post-37778408)

### Inferences
- The known complaint areas are robotic or flat delivery, mispronounced Korean, Japanese and Chinese names and skill terms, factual mistakes, and AI disclosure. A pronunciation list per series and a consistent, natural voice address the first two.

### Gaps
- Real comment threads (praise for Manhwa Fresh's narrator, "music too loud", "too fast") could not be collected. Next step: an OAuth token with the `youtube.force-ssl` scope for commentThreads.list (1 unit per call), or manual reading.

## 8. Dub (acted character voices) versus narrator recap, the two reference videos, and vocabulary for a great recap voice

### Takeaway
The owner's two references are two different formats. **Akatsuki's RomCom Mangas** is a professional manga *dub*: a localised Japanese "manga douga" channel whose English version is produced by Lab316 Inc. with human voice actors performing the characters. **Manhwa Fresh** is a single-narrator *recap*: one calm, deep, measured male voice telling a story for over 2 hours. What pulls viewers in is a *performed* voice: real emotional range, deliberate pauses and character colour. Our recap probably lacks that. Either mimic the narrator style with an expressive voice and direction, or move toward a dub with a narrator plus 2 to 4 character voices.

### Cited Findings
**Akatsuki and the manga-dub business**
- Reference video "[Manga Dub] The failure they sent to the ruthless beauty CEO: 'A contract's impossible' [RomCom]": 21m03s, posted 2026-10-29 12:00 UTC, 6,837 views, 326 likes and 17 comments at fetch time. The description is a generic "We are Akatsuki's RomCom Mangas! … New RomCom videos everyday!" with no cast credits. — [video](https://www.youtube.com/watch?v=EZ8X1glKoMM)
- Channel: 95.8K subs, 839 videos, 48.3M views, created 2023-07-31. It calls itself "official English Akatsuki's RomCom Mangas" and links the Japanese channel. — [Akatsuki EN channel](https://www.youtube.com/channel/UCuHA9fYQn63yCN-UZ0Q2Ybg)
- The Japanese parent channel is あかつき高校漫画部 (Akatsuki High School Manga Club): 243K subs, 1,038 videos, created 2021-07-13. Its premise is four fictional club members, one of whom appears at the start of each manga introduction ("マンガ紹介の冒頭では私、ハル君、秋音、冬真君の誰か１人が登場する"). It recruits manga artists. — [Japanese channel](https://www.youtube.com/channel/UCGaNTtJCiBroWCXivNrXOfQ)
- Manga Dubpedia says the English channel was "created and dubbed by Lab316" on July 31, 2023. IMDb lists Rebecca Danae and Raina Meginley as top-billed cast for the "series". (Both come from search snippets; the pages returned 403. The roles are not shown.) — [Manga Dubpedia](https://mangadubs.miraheze.org/wiki/Akatsuki's_RomCom_Mangas), [IMDb](https://www.imdb.com/title/tt28664241/)
- Lab316 Inc. localises Japanese manga, anime and game YouTube videos into English, Spanish, Chinese, Korean, French, German and Portuguese. Its services include translation, "dubbing by local voice actors" (現地の声優による吹き替え), editing and channel operation. — [Lab316](https://lab316.me/)
- Other Lab316 English channels say: "We are always hiring new voice actors, translators!" and "English Channel Creation and Management: Lab316 Inc." These are Kanon's RomCom Mangas (641K subs, 1,924 videos), Kawaii RomCom Mangas (294K), RomCom Manga Lab (53.2K) and Tokikuro Isekai Romance (15.9K). Sarubedo RomCom Mangas (193K) and Manga Sarubedo (218K) are also Lab316-managed. Top dub videos reach 1.22M views (Kanon's) at 13 to 31 minutes. — [Kanon's](https://www.youtube.com/channel/UCG0bIjs1DXYKvaCO4t6irAQ), [Kawaii](https://www.youtube.com/channel/UC9Qipk3psnRhwP5Spj0QLGw), [RomCom Manga Lab](https://www.youtube.com/channel/UC_-fglawalfTk5ksJCr1ASA), [Sarubedo](https://www.youtube.com/channel/UCidRYNwN-N-16NzqFtJBjzw); own API sample
- In Japan, manga douga voice work is human and cast: Lancers lists jobs recruiting narrators and voice actors for YouTube manga videos (from 700 yen, per the search snippet). Kodansha's Magazine Channel has run "voice comics" with professional seiyuu since 2021. Voice agencies list YouTube voice-comic credits. Studios bundle casting, recording and clean-up. — [Lancers job](https://www.lancers.jp/work/detail/2535920), [PR Times / Kodansha](https://prtimes.jp/main/html/rd/p/000003075.000001719.html), [Al-Share agency](https://al-share.co.jp/), [Digital Shokunin](https://digishoku.co.jp/video/)
- Individuals making manga videos in Japan can use AI voices (CeVIO AI, VOICEROID, CoeFont), combining several AI voices so characters sound distinct. Tool articles describe AI as "complementary rather than a full replacement". — [awaisora article](https://programming.awaisora.com/765ccf5a-1f89-4e0d-8e49-3c4378b97a87/), [search summary of aianimation.jp](https://www.aianimation.jp/ai-voice-actor-tools-2025/)
- Independent English dubs: Diceskiyo (450K subs) "Voice Acting / Comic Dubs" is a solo voice actor. DeadJosey credits "Voice: @DeadJosey". Fan-dub Discord casting calls are unpaid, list many roles (53 in one call), and warn "You will have to yell some lines". — [Diceskiyo](https://www.youtube.com/channel/UCkMwoYRz7FH4akuQEFfb4Rg), [CastingCall.club (2023, older)](https://www.castingcall.club/projects/voice-actors-needed-for-manga-dubs)
- A hybrid exists: 7 recap-search titles are labelled "Manhwa Recap Dub" (e.g. Losweko, 650K views, about 10 minutes). — [Losweko video](https://www.youtube.com/watch?v=Og8kH4_NFIk); own API sample

**Manhwa Fresh**: see section 1. A 2h05m single narrator, no voice credit, and a voice cloned by others, described as "calm… deep, resonant… clear and measured, with a touch of mystery". — [video](https://www.youtube.com/watch?v=9OSXs52aICI), [Fish Audio clone](https://fish.audio/m/7714042439c24509ba4ef61c53671799/)

**Language for describing voices, as used by vendors**
- "Measured, serious" (Dan), "weathered, textured… adds weight to storytelling" (Bill), "upbeat, energetic" (Alex). Stability setting: "lower = more expressive variation, higher = more consistent". Audio tags direct delivery at key moments. — [ElevenLabs blog](https://elevenlabs.io/blog/the-5-best-ai-voices-for-youtube-automation-and-faceless-videos)
- "Sounds like a fan explaining the arc to you", "hits the hook hard and keeps momentum", "raspier tone that matches heavier material". — [YTVoice.app](https://ytvoice.app/use-cases/anime-recap-youtube)
- Human narrators add breaths and hesitations that AI often lacks. — [OverseerOS](https://www.overseeros.com/blog/youtube-script-length-word-count)

### Inferences
**Dub compared with narrator recap**

| | Manga dub (Akatsuki, Kanon's) | Narrator recap (Manhwa Fresh) |
|---|---|---|
| Voices | Several human voice actors playing the characters (2 or more), sometimes with a narrator or host | One narrator for the whole video |
| Point of view | First-person protagonist, plus dialogue | Third person ("He…"), with lines quoted |
| Length | 13 to 31 minutes | 1 to 13+ hours (median about 1.6 hours) |
| What pulls viewers in | Acting, chemistry, comic timing, character voices | Calm, authoritative, binge-able storytelling and fast plot progress |
| Cost | Casting, direction and recording; studio-run (Lab316) | One voice (human or AI) |
| Fits | Original stories you own (romcom, comedy) | Recaps of long serialised manhwa |

**Vocabulary for briefing or judging a recap voice** (my framework, built from the descriptors above)
- **Pitch and register**: low or baritone ("deep, resonant") versus mid or bright. Top recap: low-mid male.
- **Timbre and warmth**: warm, rounded, slightly breathy against thin, nasal or "radio-bright". Texture: smooth versus "raspy" or "weathered".
- **Pace**: words per minute (about 155 to 175 for narration). "Measured" means steady with no rushing; "brisk" means energetic.
- **Pauses**: beat pauses before reveals and after punchlines, and breath sounds. AI voices often have too few.
- **Emphasis and stress**: hitting the key word ("he *refused*"). Pitch rises for questions, falls for finality.
- **Prosody and melody**: varied intonation versus monotone. AI "flatness" comes from repetitive sentence melody.
- **Emotion range**: calm baseline, but able to move to tension (quieter and closer), anger (harder) and comedy (lighter).
- **Character colour**: in dubs, distinct voices per character. In recaps, a light change of tone when quoting characters.
- **Consistency**: the same voice, mic and level in every video. This is the brand.
- **Diction and pronunciation**: clean consonants, correct names, holds up at 1.5x on phone speakers.
- **Mic quality and proximity**: close-mic, intimate presence, no room echo, low noise floor, controlled sibilance.

**Likely gap in our recap** (inference): a TTS read at a uniform rate, with few pauses, little emphasis and flat emotion, sounds "fine but not gripping". Directed delivery with pauses, emphasis and quieter, closer delivery in tense moments, plus character colour on quoted lines, is what both reference styles share.

### Gaps
- The cast size and recording setup per Akatsuki EN video, and whether any English Lab316 channel uses AI voices. The wiki and IMDb pages were blocked (403) and descriptions carry no credits.
- Whether Manhwa Fresh's narration is human or AI. No public evidence.
- Viewer comments praising either voice. The comments API was not available with this token.

## 9. The voice itself: a concrete spec for a winning recap or dub voice

### Takeaway
No public source measures a top recap voice acoustically, and audio analysis was out of scope. So this spec combines three things. First, how the leading recap voice is described ("FRESH MANHWA" clone: calm, deep, resonant, clear, measured, a touch of mystery). Second, voice-acting and audiobook norms. Third, TTS vendor documentation on what makes AI voices sound robotic.

The target:
- **Pitch and timbre:** a low-to-mid male voice (adult male speaking pitch is about 85 to 155 Hz; a "deep" narrator sits in the lower half), warm and resonant, with crisp diction.
- **Pace:** a baseline of about 150 to 170 WPM. Slow down for tension and sad beats, speed up for fights.
- **Pauses and stress:** deliberate pauses of about 0.5 to 1.25 s before reveals, and one stressed word per sentence.
- **Energy:** drop to quieter and closer for suspense.
- **Consistency:** one locked voice in every video.
- **Recording:** close-mic, dry, lightly processed, mastered to about -14 LUFS.

The most-cited AI failures are flat, repeating sentence melody, a single energy level, mechanical or missing pauses, wrong stress, and mangled names and numbers. They are tolerable in a 30-second clip and tiring over a long recap.

### Cited Findings
**Pitch**
- Adult male voiced speech has a fundamental frequency of about 85 to 155 Hz; one figure of 90 to 155 Hz goes back to Fitch and Holbrook (1970), cited in Baken. — [Wikipedia: Voice frequency](https://en.wikipedia.org/wiki/Voice_frequency)
- In a 2012 lab study (Klofstad, Anderson and Peters, *Proc. R. Soc. B*), pitch-shifted recordings were played to listeners. The lower-pitched version won about 60% of votes and was rated more competent, stronger and more trustworthy. The effects were uneven by sex, and the candidates were fictional. — [LiveScience](https://www.livescience.com/19028-voice-pitch-presidential-elections.html), [Duke Chronicle](https://dukechronicle.com/article/2012/04/study-finds-preference-leaders-lower-pitched-voices)
- TTS controls: Azure SSML pitch presets are x-low -45%, low -20%, high +20% and x-high +45%, and pitch changes should stay "within 0.5 to 1.5 times the original". Rate presets are slow 0.64x and fast 1.55x, within 0.5 to 2x. ElevenLabs speed runs 0.7 to 1.2 (default 1.0), and "Extreme values may affect the quality". — [Azure SSML voice](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-voice), [ElevenLabs best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)

**Timbre vocabulary as used in voice-over casting** (VoiceActor.com, May 2023)
- Warm: "Friendly, comforting, and inviting".
- Resonant: "Deep, full, and rich … powerful, memorable impact".
- Dark: "Mysterious, intense, or serious, commonly used in suspenseful or dramatic content".
- Gravelly or raspy: "Rough … maturity, toughness".
- Husky: "Deep and slightly rough".
- Smooth: "Flowing, soothing".
- Conversational: "like chatting with a friend".
- Authoritative: "Commanding and credible".
- Trailer: "Bold, dramatic, and exciting".
— [VoiceActor.com](https://voiceactor.com/articles/voice-over-descriptors)
- Crisp means clear, quick, efficient speech with strong articulation. Breathy means quiet with a lot of breath. (Search-result summaries of wikiHow and Wordnik.) — [wikiHow mirror](https://kiwix.lema.org/wikihow_en_maxi_2023-03/Ways-to-Describe-a-Voice), [Wordnik](https://wordnik.com/lists/voice-descriptions)
- How the leading recap voice is described: "calm and professional male voice with a deep, resonant tone … clear and measured, with a touch of mystery". — [Fish Audio "FRESH MANHWA"](https://fish.audio/m/7714042439c24509ba4ef61c53671799/)
- Vendor equivalents: Sam's "raspier tone that matches heavier material" for seinen; ElevenLabs' Bill, "weathered, textured"; Dan, "measured, serious". — [YTVoice.app](https://ytvoice.app/use-cases/anime-recap-youtube), [ElevenLabs blog](https://elevenlabs.io/blog/the-5-best-ai-voices-for-youtube-automation-and-faceless-videos)

**Speaking rate by scene**
- Narration baseline: 140 to 160 WPM is "a starting test … not a rule" (Recapo, Aug 2026). The measured median for long-form voiceovers is 166.5 WPM (OverseerOS, Oct 2026). — [Recapo AI narration](https://recapo.ai/blog/ai-narration-for-movie-recaps/), [OverseerOS](https://www.overseeros.com/blog/youtube-script-length-word-count)
- Audiobook practice: "a faster pace is often required for action scenes, such as a chase or a fight". For a sad or suspenseful scene, "take your time over the words and the pauses". Other guidance: "slow down for dramatic pauses, and speed up during action-packed sequences", and using the same style for both "weakens impact". — [Audiobook tips (C.C. Hogan)](https://cchogan.dancingbear.co.uk/audiobook-tips-a-short-guide/audiobook-tips-reading/), [Automateed](https://www.automateed.com/how-to-narrate-audiobooks-2), [Narration Box: emotional pacing](https://narrationbox.com/blog/how-emotional-pacing-affects-audiobook-experience) (via search summaries)
- Long-form: "moderate pacing, narrative arc". Shorts: "slightly faster pacing, high energy opening". — [Narration Box (Feb 2026)](https://narrationbox.com/blog/why-ai-voice-sounds-robotic-on-youtube)
- Small speed-ups for AI voices: 1.05x "nearly imperceptible in individual sentences" but it reduces drag over long tracks; FluxNote uses 1.1x. — [dev.to (Julian Brown)](https://dev.to/julianbrown/why-ai-voices-sound-incredible-for-30-seconds-and-unbearable-after-three-minutes-1mfi), [FluxNote](https://fluxnote.io/guides/manhwa-webtoon-recap-channel)

**Pauses**
- Microsoft's standard pause lengths ("break strengths"): x-weak 250 ms, weak 500 ms, medium 750 ms (the default), strong 1,000 ms, x-strong 1,250 ms. The maximum is 20 s. It can also set exact silence at sentence boundaries and commas (examples: 200 ms between sentences, 50 ms at commas). — [Azure SSML structure](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-structure)
- ElevenLabs: `<break time="x.xs" />` "for natural pauses up to 3 seconds" (not Eleven v3 or v4), and "Using too many break tags … can cause instability". On v3 and v4, use ellipses and punctuation; dashes give short pauses, ellipses "hesitant tones". — [ElevenLabs best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- Audiobook craft: when revealing a secret or answering a key question, "pauses are everything", and they should be longer than the rest of the narration. A pause after "a joke, death, reveal, or betrayal" should not feel identical to the others. A scene pause should be "long enough for the listener to feel a reset". No seconds are given. — [Narration Box: scene-break conventions (May 2026)](https://narrationbox.com/blog/scene-break-section-pause-conventions-ai-audiobooks); reveal guidance via [search summary](https://vois-web.pages.dev/blog/audiobook-narration-tips)
- Comedy: "most punch lines want a little room to breathe", but test each line with and without the beat; some punchlines get none. No authoritative duration exists; one comedian's pause measured about 2.2 to 2.6 s, a single case. — [Backstage](https://www.backstage.com/magazine/article/what-is-a-punch-line-76220/), [Wikipedia: Comic timing](https://en.wikipedia.org/wiki/Comic_timing), [Scienceblog](https://scienceblog.com/?p=573658)
- AI narration "often has fewer" breaths and hesitations than a human. — [OverseerOS](https://www.overseeros.com/blog/youtube-script-length-word-count)
- Sync: the spoken reveal should land with the visual reveal. — [Recapo AI narration](https://recapo.ai/blog/ai-narration-for-movie-recaps/)

**Emphasis, volume and energy**
- ElevenLabs v4: "Capitalization increases emphasis"; ellipses add "pauses and weight". Audio tags include `[whispers]`, `[sighs]`, `[laughs]` and `[sarcastic]`; describe the quality clearly ("[low, gravelly voice]"). Emotion through "narrative context or explicit dialogue tags" works, but the model may read the guidance aloud. — [ElevenLabs best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- Azure styles include `narration-professional` ("professional, objective tone"), `narration-relaxed` ("soothing and melodious"), `whispering`, `shouting`, `fearful`, `sad`, `excited` and others, with intensity 0.01 to 2. — [Azure SSML voice](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-voice)
- "Cheap voices read text linearly", without rise and fall or tonal contrast. Fixes are inline cues such as [whisper], [pause], [shocked], [softly] and [intense], short sentences, and pauses after key statements. — [Narration Box](https://narrationbox.com/blog/why-ai-voice-sounds-robotic-on-youtube)
- "Standard TTS flattens everything to a single average energy state", and "A custom voice only solves timbre, not performance." — [dev.to](https://dev.to/julianbrown/why-ai-voices-sound-incredible-for-30-seconds-and-unbearable-after-three-minutes-1mfi)

**Brand consistency**
- Recapo: "voice drift" between episodes makes "the channel feel less like a channel". Generate the same lines on different days to check that they match; keep a pronunciation glossary; record the model and version. — [Recapo AI narration](https://recapo.ai/blog/ai-narration-for-movie-recaps/)
- ACX (audiobooks) requires consistency "in levels, tone, noise level, spacing, and pronunciation". — [ACX requirements](https://help.acx.com/s/article/acx-audio-submission-requirements)
- One voice treated as a brand asset: the Manhwa Fresh-style clone has about 3,400 uses. — [Fish Audio](https://fish.audio/m/7714042439c24509ba4ef61c53671799/)

**Microphone and processing sound**
- ACX narration specification (human narration): RMS -23 to -18 dB, peaks below -3 dB, noise floor below -60 dB RMS, 1 to 5 s of room tone, and no plosives, mic pops, clicks or "excessive mouth noise". — [ACX](https://help.acx.com/s/article/acx-audio-submission-requirements)
- Voice chain norms from tutorials:
  - High-pass filter at 80 to 120 Hz (one engineer warns against applying it blindly).
  - Close miking adds low-end build-up (proximity effect); fix it by mic distance first.
  - De-esser at 5 to 8 kHz, about 3 to 6 dB of reduction.
  - Compression 3:1 to 4:1 (one guide gives 6:1 with a fast attack for speech).
  — [Audient](https://audient.com/tutorial/crafting-a-basic-vocal-chain-a-step-by-step-tutorial/), [Amped Studio](https://ampedstudio.com/blog/vocal-chain/), [Beat Kitchen](https://beatkitchen.io/guides/mixing-masterclass/14-mixing-vocals/) (via search summary)
- A worked TTS mastering example: 80 Hz high-pass, downward expander, two-pass EBU R128 normalisation. Noise floor went from -52 to -68.4 dB and loudness from -24.8 to -20.0 LUFS (an audiobook target, not YouTube). — [dev.to](https://dev.to/julianbrown/why-ai-voices-sound-incredible-for-30-seconds-and-unbearable-after-three-minutes-1mfi)
- Japanese manga-video production guide (PRONI Aimitsu, Jan 2025): narration "クオリティを左右しやすい" (it largely decides quality); viewers may leave partway if the narration is poor; recording environment and equipment noticeably change the sound. — [imitsu](https://imitsu.jp/matome/movie/howtomake-cartoonvideos)

**Most-cited AI voice failures**
- Repeated pitch shapes ("each sentence following the same contour"), one energy level, and evenly weighted pauses that feel "sluggish and heavy" over ten minutes. — [dev.to](https://dev.to/julianbrown/why-ai-voices-sound-incredible-for-30-seconds-and-unbearable-after-three-minutes-1mfi)
- Linear reading with no pause after key claims; mispronounced names and terms "break immersion". Vendor claims, unverified: robotic voice cuts watch time by 15 to 40%, and fatigue sets in after about 90 s of flat narration. — [Narration Box](https://narrationbox.com/blog/why-ai-voice-sounds-robotic-on-youtube)
- Long inputs: TTS reliability "deteriorates as the input text grows" (content accuracy errors). — [arXiv: Taming Long-form TTS](https://arxiv.org/pdf/2609.16989) (via search summary)
- Artifacts "tolerable in short clips but … fatiguing over hours". — [Humanize Audio](https://blog.humanizeaudio.com/why-ai-voice-sounds-robotic/) (via search summary)
- Mangled character names, rushing, voice drift, and narration that misses the on-screen reveal. — [Recapo AI narration](https://recapo.ai/blog/ai-narration-for-movie-recaps/)
- Numbers and abbreviations misread (Flash v2.5 may say "one thousand thousand dollars"). Fixes: phoneme or IPA tags, alias tags, and pronunciation dictionaries, where "only the very first replacement is used". — [ElevenLabs best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- YouTube's automatic AI dubbing cannot give each character a different voice, so it is "hard to tell who is speaking". — [akagami.blog (Japanese, via search summary)](https://akagami.blog/2025youtubeai/)
- Amazon's AI anime dubs were mocked as flat and awkward. — [AOL](https://www.aol.com/articles/amazon-removes-ai-generated-anime-070348147.html)

### Inferences
**Voice spec sheet for our narrator** (a synthesis of the sources above; the numbers are starting points to test, not measured from top channels)

| Parameter | Target |
|---|---|
| Pitch | Male baritone. Speaking pitch roughly 90 to 120 Hz, the lower half of the 85 to 155 Hz male range. Avoid pitching a voice down beyond about -2 to -3 semitones (artefacts). |
| Timbre | Warm, resonant, slightly dark. Crisp consonants. Not nasal, not breathy, no "announcer" sheen. A touch of grain is fine. |
| Baseline rate | 155 to 170 WPM. |
| Rate by scene | Tension, sad and reveal: about 130 to 150 WPM. Comedy: baseline, a light and dry delivery. Fight or montage: about 175 to 190 WPM with very short sentences. Never so fast that names blur. |
| Pauses | Comma about 0.2 to 0.3 s. Sentence about 0.4 to 0.6 s. Story beat about 0.75 to 1 s. Before a reveal or twist about 1 to 1.5 s. After a punchline about 0.5 to 1 s. Scene or chapter change about 1.5 to 2 s, with a music swell. |
| Emphasis | One stressed word per sentence: the twist word, the number, the name, or the contrast pair ("*weakest* … *strongest*"). |
| Dynamics | Mid-energy baseline. Drop to quiet and close for secrets, dread and inner thoughts. Lift for battle climaxes. The narrator never really shouts; shouting belongs to quoted character lines, said with colour. |
| Emotion | Comedy: a smile in the voice, deadpan delivery, timing. Tension: slower, lower, closer. Fight: punchy, rhythmic. Sad: softer, slower, longer pauses. Triumph: brighter, firmer endings on each sentence. |
| Consistency | Lock the voice, model version and settings. Keep a per-series pronunciation glossary (Korean, Chinese and Japanese names; skill names). Use the same processing chain and loudness in every video. |
| Mic and processing | Dry, close sound with a noise floor under -60 dB. High-pass about 80 Hz, de-ess 5 to 8 kHz (3 to 6 dB), compression about 3:1 (3 to 6 dB of gain reduction), limiter at -1 dBTP, about -14 LUFS for YouTube. |

- Practical point for a TTS pipeline: if the TTS cannot follow tags reliably, put the performance into the text (short sentences, ellipses, CAPS on the stress word, paragraph breaks). Then generate sentence by sentence and insert exact silences in the edit, rather than trusting the model's own pauses. This tackles the "evenly weighted pauses" and "single energy state" failures directly.
- The likeliest reason "our voiceover lacks it": an even rate, even pauses and even energy (the documented AI failure pattern). Timbre is rarely the problem. A better voice alone will not fix delivery.

### Gaps
- No acoustic measurements (pitch, WPM, pause lengths, loudness) of Manhwa Fresh, Frieren Manhwa or any top recap. That would need audio analysis, which this brief excluded. It is the single most valuable next step if the owner can run it on his own downloads.
- No authoritative pause durations for reveals or punchlines; the values above are craft guidance plus TTS defaults.
- No viewer-stated preferences (comments or Reddit) on voice traits; access was blocked.

## 10. The script for the voice: how recap scripts are written to be spoken

### Takeaway
Recap scripts are written for the ear:
- short, one-breath sentences;
- a hook in the first 3 to 15 seconds built on a contradiction, a reversal or a high-stakes premise. This is the same formula as the titles: "They kicked him out to die, BUT he's the strongest", "Everyone mocked X… until";
- third person with "He" or "our MC" for English recaps, and first person for Hindi recaps and Japanese-style dubs;
- a fresh "jolt" (a new question, a reversal, a one-line opinion) every 30 to 40 seconds;
- key character lines quoted briefly and attributed, the rest paraphrased;
- a stance or a cliffhanger at the end.

Two things to avoid: stock AI filler ("But then, he discovers a shocking secret") and "Today I'm going to tell you about…" openers.

### Cited Findings
**Hooks in the first 3 to 15 seconds**
- Recapo (July 2026) gives five hook templates with example lines:
  - Suspense: "She confessed to a murder that hadn't happened yet."
  - Contrast: "The town's only firefighter turned out to be its only arsonist."
  - Question: "If turning in your own brother would save a stranger's life, would you do it?"
  - Ending-first: "In the final scene, the detective arrests himself — and he's right to."
  - Second person: "You wake up in your own bed, but every photo in the house shows a stranger's face."
  It recommends opening "with a question or contradiction" and skipping backstory, and contrasts "A man who was never late in his life just missed the last train on purpose" with "Today I'm going to tell you about a thriller." It calls narration that starts where the story starts a mistake "in thousands of recap videos". — [Recapo script guide](https://recapo.ai/blog/how-to-write-a-movie-recap-script/), [Recapo how-to](https://recapo.ai/blog/how-to-make-a-movie-recap-video/)
- Vendor claim: first-minute retention below 60% "may stop a long-form video from scaling". — [Narration Box](https://narrationbox.com/blog/why-ai-voice-sounds-robotic-on-youtube)
- Title formulas, from 146 English recap titles (own API sample):
  - 51% use "!"
  - 36% have "He" as the subject
  - 35% contain an ALL-CAPS word
  - 29% contain a number
  - 17% use reincarnation, regression, rebirth or return
  - 14% contain a "but" reversal
  - 13% use strongest, OP, genius or unlimited
  - 12% use system, rank or level
  — own API sample
- Top examples:
  - "Nobody in the Academy Can Even Lift the Weights He Trains With Every Day!" (1.55M views) — [Manhwa Fresh](https://www.youtube.com/watch?v=kIpABFQJ8qM)
  - "Military Genius Reincarnates as The Worthless Youngest Son Of The King!" (1.39M) — [Mamoru](https://www.youtube.com/watch?v=YGLNNUaMju0)
  - "They Kicked Him To Die In The Apocalypse BUT He's The STRONGEST Regressor!" (1.11M) — [Tobs](https://www.youtube.com/watch?v=0w1FjXmgX0w)
  - "#1 UFC FIGHTER Reincarnates As A SLAVE Into The STRONGEST MAGE FAMILY!" (1.33M) — [Frieren Manhwa](https://www.youtube.com/watch?v=1gcX-jXmJDM)
- Hook copy written in the narrator's voice, from descriptions:
  - Akiel Runes (2.27M views): "In this fictional world, color is EVERYTHING... But our MC is a blank page. That is until he was thrown into a mix of all inks, which turned him into one of the dark creatures that took over the world." — [video](https://www.youtube.com/watch?v=TAPhcHn0rDM)
  - Manhwa Outpost: "Humanity has frozen, and Zhang Yi has traveled back in time to change his past and seek revenge. Now, he possesses the incredible power of space manipulation and has gone completely mad, stockpiling supplies for the frozen apocalypse!" — [video](https://www.youtube.com/watch?v=E4q9RTu5dXs)
  - Manhwa ZoneXi: "A mysterious event changes the world when cards start falling from the sky… but while everyone is confused and panicking, one genius already knows what's coming 😈" — [video](https://www.youtube.com/watch?v=uHBR0aoBqTU)
  - Manhwa Senpai: "After 99 rejections, the ultimate twist hits—on the 100th, he walks away forever. From a hopeless simp to a ruthless man, watch betrayal, revenge, and a regretful girl lose everything as she chases him too late." — [video](https://www.youtube.com/watch?v=aQ0xKM2OCwQ)
  - yuva explainop (Hindi, first person): "Ek dangerous Black Bear society mein ghuskar logon par attack karna shuru kar deta hai, lekin mujhe pehle se pata tha ki ye sab hone wala hai." My translation: "A dangerous black bear breaks into the housing society and starts attacking people, but I already knew this was going to happen." — [video](https://www.youtube.com/watch?v=MbGvwZqwM14)

**Sentence length and structure**
- Split any sentence that leaves the narrator out of breath. Cover only 6 to 8 plot-driving beats, with one transition sentence per beat. Add a "small jolt every 30–40 seconds (a new question, a reversal, or a one-line take)". Write the script word for word, not from an outline. Rewrite the opening and closing by hand. — [Recapo script guide](https://recapo.ai/blog/how-to-write-a-movie-recap-script/)
- "Keep sentences relatively short to match a fast video pace", with vivid language for dramatic moments (a manhwa recap prompt template, via search snippet; the page returned 404). — [DocsBot prompt](https://docsbot.ai/prompts/creative/manhwa-recap-narration)
- Short sentences, built-in pauses after key statements, contrast phrases; one dense statistic sentence split into three lines. — [Narration Box](https://narrationbox.com/blog/why-ai-voice-sounds-robotic-on-youtube)
- For TTS: write "in a natural, narrative style" to steer pacing; expand numbers and abbreviations ("Dr." → "Doctor"). — [ElevenLabs best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- Japanese guidance (via search summary, page not verified): a narration script that is fully understandable without the pictures is not a good one; narration should work with the visuals, not repeat them. — [Lancers article](https://www.lancers.jp/c/article/article-knowhow/13191/)

**Point of view and tense**
- English recap titles favour third person; Hindi and manga-dub titles favour first person (see section 2). Guides suggest drafting, then using ChatGPT to turn it into third-person narration "appropriate for an AI voiceover". — [Toolify (via search summary)](https://www.toolify.ai/ai-news/creating-engaging-manhwa-recaps-a-stepbystep-guide-3528091)
- The description hooks above mix present tense ("changes… knows what's coming"; "Now, he possesses…") with past tense for backstory ("was thrown"). — [Manhwa ZoneXi](https://www.youtube.com/watch?v=uHBR0aoBqTU), [Manhwa Outpost](https://www.youtube.com/watch?v=E4q9RTu5dXs), [Akiel Runes](https://www.youtube.com/watch?v=TAPhcHn0rDM)
- "Our MC" appears in recap copy (Akiel Runes, above).

**"But then", rhetorical questions, foreshadowing**
- Recapo names "But then, he discovers a shocking secret" as a sign of generic AI-written narration. Question hooks should make viewers pick a side. Keep "one or two knots tied until the end". — [Recapo script guide](https://recapo.ai/blog/how-to-write-a-movie-recap-script/)
- Reversal connectors in real copy: "But our MC is a blank page. That is until…" (Akiel Runes); "…but while everyone is confused and panicking, one genius already knows what's coming" (ZoneXi). These lines also foreshadow. — [Akiel Runes](https://www.youtube.com/watch?v=TAPhcHn0rDM), [Manhwa ZoneXi](https://www.youtube.com/watch?v=uHBR0aoBqTU)

**Character dialogue**
- Attribute lines to speakers so the narration doesn't become "a wall of unattributed quotes". Use "a limited selection of panels". — [RecapManga](https://recapmanga.com/blog/manhwa-recap-scripts-ai-guide)
- Two production modes: "Dialogue recap" (the extracted dialogue becomes the audio) and "Narrated recap" (bubbles removed, AI narrates), with "Different voices for narration vs. dialogue". — [dev.to manhwa studio](https://dev.to/aashish124/how-i-built-an-ai-studio-that-turns-manhwa-chapters-into-narrated-recap-videos-5enl)
- Dubs give each character line to a performer (Lab316 "dubbing by local voice actors"). — [Lab316](https://lab316.me/)
- Explicit dialogue tags ("she whispered") make TTS emotion more predictable than context alone. — [ElevenLabs best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- From Japanese script-writing advice (written for stage plays, Dec 2025): avoid 説明セリフ, "unnatural lines an author has an actor say to explain something"; show it through action, expression and sound instead. — [coconala magazine](https://coconala.com/magazine/5145)

**Commentary, opinion and jokes**
- End with "a stance, not a summary"; the take is the main differentiator, and AI tends to produce bland summaries. — [Recapo script guide](https://recapo.ai/blog/how-to-write-a-movie-recap-script/)
- Commentary is "the part only you can do". Lead with analysis or reaction rather than a panel-by-panel read. — [RecapManga](https://recapmanga.com/blog/manhwa-recap-scripts-ai-guide)
- A channel built on opinion and humour: Schikan, "it's really funny, just how bad it truly is" (1.09M views). — [Schikan](https://www.youtube.com/watch?v=b4KL405WjQE)
- Tone: "excited and conversational like a fan talking to a fan". — [FluxNote](https://fluxnote.io/guides/manhwa-webtoon-recap-channel)
- Joke delivery: give punchlines "a little room to breathe", but test with and without the beat. — [Backstage](https://www.backstage.com/magazine/article/what-is-a-punch-line-76220/)
- Monetisation context: added human creative input is what separates OK AI-assisted content from "inauthentic" templated content. — [Medium analysis](https://mateostarcevicfilipovic.medium.com/youtube-quietly-demonetizes-faceless-ai-channels-since-july-2025-30b3d2daaf2e)

**Endings and cliffhangers**
- "End with a cliffhanger teaser for what happens next." — [FluxNote](https://fluxnote.io/guides/manhwa-webtoon-recap-channel)
- Long recaps are packaged as parts: "00:00:00 - Part 1 to 8 … 10:45:49 - New Part 15" (Manhwa Outpost); "【1~2】" (Gido Cuni Mahwa); "(Completed)" and "*Completed*" labels (Manhwa Fresh, Magical Manhwa Recaps). — [Manhwa Outpost](https://www.youtube.com/watch?v=E4q9RTu5dXs), [Gido Cuni Mahwa](https://www.youtube.com/watch?v=6ZFDZzYvdOs), [Magical Manhwa Recaps](https://www.youtube.com/watch?v=VKTAPTRRweo)

**Addressing the viewer**
- Avoid "Today I want to tell you about…" openers. Direct "you" works as a hook device. — [Recapo script guide](https://recapo.ai/blog/how-to-write-a-movie-recap-script/)
- Viewer-address patterns in descriptions:
  - "How would you rate this manhwa from 0 to 10? Drop your rating and why in the comments!" (Magical Manhwa Recaps) — [video](https://www.youtube.com/watch?v=eBhshOY6QY8)
  - "Name in the pinned comment below👇" (Manhwa Fresh) — [video](https://www.youtube.com/watch?v=9OSXs52aICI)
  - "If you love manhwa and like storys you are in the right place" (Tobs) — [video](https://www.youtube.com/watch?v=0w1FjXmgX0w)
- The Japanese Akatsuki channel uses a recurring host character at the start of each manga introduction (a persona, not a creator intro). — [あかつき高校漫画部](https://www.youtube.com/channel/UCGaNTtJCiBroWCXivNrXOfQ)

### Inferences
**A script-for-voice checklist for our recap** (synthesis; the example lines are illustrative and written by me, not quoted)
- **Hook (0 to 15 s):** state the contradiction or stakes in 2 to 3 short lines, then the promise. Pattern: *[status/insult] → [hidden truth] → [consequence].* E.g. "Everyone in the guild calls him F-rank. A tea seller. Useless. What they don't know… is that every cup he pours levels him up." No channel intro before the hook.
- **Sentences:** one idea each, about 8 to 15 words on average. Break long ones at "and" or "which". Put the stressed word last where possible ("…and the one who walked in was *his father*.").
- **POV and tense:** for English, third person with "he" plus the name; present tense for the main action ("He opens the door. The room goes silent."), past tense for backstory. Use first person only for Hindi or dub-style formats.
- **Reversal engine:** a turn every 30 to 40 s. Vary the connectors ("but", "until", "except", "what nobody noticed was…", "there's just one problem"). Avoid the stock "But then, he discovers a shocking secret" by naming the concrete secret.
- **Foreshadowing lines:** "He doesn't know it yet, but this choice will cost him everything." Use about one per act, and pay it off.
- **Rhetorical questions:** at act breaks only ("So why would the strongest man in the city choose to sell tea?"), followed by a pause.
- **Dialogue:** quote at most 1 to 2 decisive lines per scene, attributed ("he says", "she snaps"), with light character colour from the narrator. Paraphrase the rest. Turn sound effects and inner monologue into narration.
- **Jokes:** set up straight, make the punchline the last word, then pause about 0.5 to 1 s. Never explain the joke. Deadpan narrator asides ("Bold strategy.") work well.
- **Commentary:** short opinion beats ("Honestly? That was cold.") about every few minutes, and a stance at the end, to meet the "human creative input" bar.
- **Viewer address:** sparse. An optional "you" in the hook, a question at the midpoint or end, and a call to action for the next part.
- **Ending:** a cliffhanger line about the next arc plus a question for the comments, or "Completed" with a final verdict.
- **Mark-up for TTS:** put performance cues into the text (ellipses, em-dashes, CAPS for stress, paragraph breaks). Keep a pronunciation glossary. Plan pause lengths per beat type (see section 9).

### Gaps
- No full spoken script or transcript from a top manhwa recap could be quoted; captions and audio were out of scope, and Reddit was blocked. The script patterns above come from titles, descriptions and tool guides.
- How often top narrators address the viewer, use jokes, or read dialogue verbatim is unmeasured.
