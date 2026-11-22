# Working in this repository

## Security comes first (owner's rule, 22 Nov 2026: "Always check for security")

Every run, scheduled or not, follows these rules.

**Before using or recommending any outside tool, library, model or Space**, check:

- **Install scripts.** Does it pipe a download into a shell, or run hooks on install? Does the installer verify what it downloads?
- **Where your data goes.** Which servers receive our keys, prompts, voice and pictures? Is telemetry on by default, and how is it turned off?
- **Default settings.** Look for default passwords and secrets, ports open to the network, servers with no login, and CORS set to `*`.
- **Model loading.** Look for pickle files loaded with `torch.load` without `weights_only=True`, `trust_remote_code=True`, and model versions that are not pinned.
- **Known vulnerabilities.**
  - Run the OSV scanner on the tool's lockfiles.
  - Search the NVD for published CVEs, and compare the affected versions with the current one.
- **Security policy.** Does the project have a security policy?

Report what was verified in the code apart from what was not run.

**This repository is public**:

- **Never commit secrets.** No keys, tokens, passwords or `env.sh`. Keys live in `~/.cache/<project>/env.sh` and the environment settings.
- **Never commit private media.** No voice audio, video clips, or the owner's real photo. Doodle host pictures are fine.
- **Search before every push.** Run a key-pattern search over the diff before pushing.

**Keys go only where they belong**:

- `HF_TOKEN` is sent only to the owner's own Spaces and datasets, never to third-party Spaces.
- YouTube and ElevenLabs keys are sent only to their own APIs.
- Never print a key's value.

**Our own libraries**: when a pinned version gets a known vulnerability, say so, and update it after testing.
- Example: the picture Space `videos/manga/spaces/flux2` runs Gradio 5.50.0, which has 14 known issues.
