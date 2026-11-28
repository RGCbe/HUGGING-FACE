# HUGGING-FACE / YouTube / Social Video Project Directive

## ABSOLUTE CORE DIRECTIVE: TRUTH, INTEGRITY & RIGOROUS VERIFICATION

1. **NEVER GIVE FALSE INFORMATION:** Never invent, assume, extrapolate, or hallucinate facts, numbers, dates, statuses, metrics, or capabilities.
2. **NEVER LIE OR FABRICATE SUCCESS:** Never report that a video, Reel, localization, or script uploaded, published, or generated unless verified with hard evidence.
3. **TEST AND CONFIRM EVERY SINGLE DETAIL:**
   - Execute the script and inspect stdout/stderr.
   - Verify HTTP status codes, API payload responses, and video IDs.
   - For Instagram Reels: Always verify audio normalization (Stereo AAC 48kHz, moov faststart) before upload.
   - For YouTube: Verify `localizations` and title length limits (<= 100 characters).
   - Never print or leak API keys or secrets in logs or git.
