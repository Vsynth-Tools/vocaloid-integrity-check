# Reddit post draft — r/vocaloid

**Title:** I made a tool that tells you why a renamed voicebank won't load (VOCALOID 2/3/4 .ddi integrity checker)

**Body:**

If you've ever renamed a voicebank folder or a `.ddb` and had the voice suddenly refuse to load,
this is why: a `.ddi` index embeds a digest of the bank name, and the engine checks it on load.
Rename the `.ddb` without updating that digest and load is rejected. Rename only the `.ddi` and it
still loads.

I wrote a small tool that checks that digest and tells you which case you're in. Sorry if this is
obvious to some of you — it took me a while to work out, and I couldn't find it written down
anywhere, so I'm leaving it here in case it saves someone else the same trouble.

**What it reports**

- `hash verified` — the digest matches the name on disk
- `hash fail` — it doesn't, so the engine will reject this bank
- `hash not present` — no digest in this file
- `hash present, not checkable` — V3/V4, see below

**How it works (VOCALOID 2)**

For `ARR2`/`ARR3`/`ARR4` roots, the 32 bytes after `PHDC` are `MD5(prefix + UPPERCASE(name) +
suffix)`, with `K2ho`/`nF` for ARR2/ARR3 and `1m5Pj`/`qFE` for ARR4. Legacy `ARR ` banks have no
digest at all.

**The honest limitation**

VOCALOID 3 and 4 (`DBSe`) do have the same 260-byte store — 32 hex characters then 228 zeros, same
as V2 — but the value isn't a function of the name alone. I took apart the V4 engine library and the
check is the same shape as V2's, except the string it hashes comes out of a licence routine that
validates a 14-character base-28 serial and ties into the machine's platform UUID and MAC address.
So the stored value depends on the licence volume, two copies of the same library can legitimately
differ, and nothing in the `.ddi` can reproduce it. The tool reports the value and refuses to judge
it, which is the honest answer rather than a guessed one.

For V3 specifically I confirmed the *file format* on a retail Gachapoid V3 bank, but the V3 package
ships only the library and no engine binary, so I couldn't confirm the mechanism the way I did for
V4. It's inferred from V4, not proven on V3, and I've said so in the README.

**One thing that surprised me**

`unity-chan_for_Unity` doesn't match the ARR4 formula — every AHS, Crypton and Internet Co. bank I
checked does. If anyone knows why that one is different, or has a V3 editor/`DSE3` binary to check
the V3 half against, I'd like to hear it.

**Where it is**

- PyPI: `pip install vocaloid-integrity-check`
- Source (MIT): [GitHub link]

Standard library only, Python 3.10+. It only reads the `.ddi` — it doesn't modify anything, doesn't
touch audio, and doesn't need the editor installed.

Happy to be told I've got something wrong.
