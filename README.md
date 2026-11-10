# Vocaloid integrity checker

Checks the integrity of a Vocaloid voicebank by locating and verifying the name digest stored in a
`.ddi`.

A Vocaloid voicebank is a folder containing a `.ddb` (the voice data) and a `.ddi` (the index).
The index embeds a digest of the bank name, and the engine checks it on load. If someone renames the
`.ddb`, the digest no longer matches and the voice will not load. This tool reports whether that
digest matches the name you have on disk.

Standard library only. Python 3.10+.

## Install

```console
$ pip install vocaloid-integrity-check
```

Or run it straight from a checkout without installing:

```console
$ python -m vocaloid_integrity_check path/to/Yuki.ddi --ddb Yuki.ddb
```

## Output

| Result | Meaning |
|---|---|
| `hash verified` | The stored digest matches the `.ddb` name. |
| `hash fail` | The stored digest does not match the `.ddb` name. |
| `hash present, not checkable` | A hash store was found but cannot be derived from the file (Vocaloid 3/4). |
| `hash not present` | No hash store in this file (legacy V2 root, or a development tree). |
| `hash not verifiable` | The name is non-ASCII, so the expected digest depends on the engine's locale. |

## Usage

```console
$ vocaloid-integrity-check Yuki.ddi --ddb Yuki.ddb
hash verified
  name   : Yuki  (root ARR4)
  stored : 92942a5a960cdf938b3d742d8a75f5df
  expect : 92942a5a960cdf938b3d742d8a75f5df

$ vocaloid-integrity-check Matcha.ddi --ddb Matcha.ddb
hash present, not checkable
  name   : Matcha  (root DBSe)
  stored : cdd787ab1039a67267dcb3d4a9e57cb9
  note   : Vocaloid 3/4 store is licence-derived; value reported, not judged
```

`--json` for machine-readable output. If `--ddb` is omitted the `.ddi` filename is used.

Exit status: `0` verified, `1` fail, `2` anything inconclusive or bad input.

## Format coverage

**Vocaloid 2 — fully checked.** For `ARR2`, `ARR3` and `ARR4` roots the 32 bytes after `PHDC` are

```
MD5(prefix + UPPERCASE(ddb_name) + suffix)
```

with `K2ho`/`nF` for `ARR2` and `ARR3`, and `1m5Pj`/`qFE` for `ARR4`. Legacy `ARR ` banks have no
digest. The engine takes the name from the `.ddb` on disk, so the digest binds a `.ddi` to that
filename. Uppercasing means case is not significant.

**Vocaloid 3/4 — located, not verified.** Retail libraries (`DBSe`) carry a 260-byte hash store
directly after `PHDC`, laid out like V2's: 32 ASCII hex characters in the first 32 bytes, the
remaining 228 zero. That is confirmed on three shipped libraries, one of them Vocaloid 3:
**Gachapoid V3** (`acfb2575…`), **Matcha** (`cdd787ab…`) and **Yukari Onn** (`086b8475…`). The V3
file differs only in the version word at `0x18`, which reads `3` instead of `4`.

What the V3/V4 value is computed from is known in outline for V4. The macOS V4 engine library
contains the check: it zeroes a 260-byte buffer, lowercases the voice name into it, prepends and
appends the same four salts used in V2 (`1m5Pj`/`qFE`, else `K2ho`/`nF`), MD5s the result and
compares all 260 bytes. The voice name it hashes is not the folder name, though — it is produced by
a licence routine that validates a 14-character base-28 serial, and the same library binds that
path to the platform UUID and MAC address. The same was not confirmed against a V3 engine binary:
the V3 retail package analysed installs only the library, not the engine. The V3 value is likewise
not name-derived, but that part of the account is inferred from V4 rather than proven on V3.

So the stored value is a function of the installed licence volume, not of the bank alone. Two
copies of one library can legitimately differ, and no `.ddi`-only rule reproduces it. The tool
therefore reports the value without judging it. `hash present, not checkable` is the intended final
state for V3/V4, not a placeholder for unfinished work.

The V3/V4 header places `PHDC` at `0x1c` rather than `0x18`, because a `u32` version follows the
flags. Development trees (`DBS `) are not supported.

## Limitations

* Not an authenticity check. The V2 constants are public, so a digest can be recomputed for any
  name. This detects accidental renames, not deliberate forgery.
* The `ARR3` salt pair is a static prediction; no `ARR3` sample was tested.
* **`ARR4` is not uniform.** Every AHS, Crypton and Internet Co. bank checked matches
  `1m5Pj`/`qFE`, but `unity-chan_for_Unity` (shipped for the Unity SDK) stores a value that the
  formula does not produce. Treat a mismatch on that bank as unknown, not as tampering.
* `hash present, not checkable` on a V3/V4 bank is expected on every file, not a defect: the stored
  value derives from the licence volume as well as the name.

## License

MIT.
