# Office Tea Talks (Tamil office life lessons, on the Tea Break channel): plan

The owner's idea (22 Nov 2026): a fully automated channel of Tamil office / IT life lessons, as doodle Shorts.

- **Why this genre:** a search of Tamil work videos from the last 90 days (`trends.py`) found the biggest topics are job
  fear (layoffs, "no more freshers", 1.1-1.6M views), office humour (manager, notice period, work-life balance, 1.8-5.6M)
  and short stories with a lesson ("தோற்றம் vs திறமை - சிறுகதை", 2.26M). Almost no Tamil channel tells office stories with
  a lesson; Chennai has lakhs of IT and office workers.
- **What is ours:** every story is our own: invented characters (never presented as the owner's real life), the owner's
  AI voice (or his real voice when he sends a voice note), our own doodles (`doodle/imagegen.py`, own Space), our own beat
  (`doodle/score.py`), built with `movies-explained/lore_video.py`, checked with `doodle/clarity.py`.
- **What is never done:** downloading or clipping other people's podcasts or videos (their audio and words are theirs,
  and YouTube refuses downloads from the cloud machine). `trends.py` reads only titles and view counts.
- **The format:** 40-60 seconds. Line 1, the moment ("காலை 6 மணி. ஒரு மெயில்…"); the story in 3-4 short lines; the lesson in
  one line; a question for the comments. Office words stay English (mail, manager, appraisal, layoff, skill).

**How a story is made (the owner's rule, 22 Nov 2026):** "we only analyse their videos, take what is important and the
main things, and from that create our own story". Each run: `trends.py` picks the hottest theme and its top videos; the
spoken text of the top 3-5 is read (the video-transcript connector; YouTube refuses direct downloads from the cloud
machine); the run writes down the main POINTS viewers care about (never sentences, never anyone's personal story, never
their course or sponsor pitches); then writes a NEW story with invented characters that carries one of those points as
its lesson. First analysis (layoffs / freshers): loyal seniors quietly sidelined; "company is not family"; companies ask
"what can you do?" not "what degree?"; "AI" often an excuse for lost projects; people over 35 accepting pay cuts.

Status (22 Nov 2026): the trend finder works; sample 1 ("காலை 6 மணி layoff mail", 43 s) made end to end and passes the
clarity check. The owner watched it and chose the Tea Break channel (below).

22 Nov 2026 (later): the owner chose to post these on the **Tea Break with Manoj** channel instead of a new one, "a little funny", in their own playlist "Office Tea Talks | ஆபீஸ் கதைகள்" (PLPWFuIoAlFcs), at 8:30 am India time. First Short: "6 மணிக்கு Layoff Mail 😅" (https://youtu.be/FPmuHDordXY), public 23 Nov 8:30 am. Daily run: trig_018qgSscwyimgCxBLkMt6xLU, 11:17 am; the points bank is refreshed every Sunday in the main session.
