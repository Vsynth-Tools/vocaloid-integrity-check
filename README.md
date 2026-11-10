# vocaloid-integrity-check

Verifies the integrity of a Vocaloid voicebank by checking the digest stored in its `.ddi` index.

If a voicebank stops loading after the folder or the `.ddb` was renamed, a digest mismatch is the
usual cause: the `.ddi` embeds a digest of the bank name, and the engine checks it on load.

Standard library only. Python 3.10+.

## Install

```console
$ pip install vocaloid-integrity-check
```

## Usage

```console
$ vocaloid-integrity-check Yuki.ddi --ddb Yuki.ddb
hash verified
  name   : Yuki  (root ARR4)
  stored : 92942a5a960cdf938b3d742d8a75f5df
  expect : 92942a5a960cdf938b3d742d8a75f5df
```

`--json` for machine-readable output. If `--ddb` is omitted the `.ddi` filename is used.

## Output

| Result | Meaning |
|---|---|
| `hash verified` | The stored digest matches the `.ddb` name. |
| `hash fail` | The stored digest does not match the `.ddb` name. |
| `hash present, not checkable` | A digest was found but cannot be derived from the file (Vocaloid 3/4). |
| `hash not present` | No digest store in this file. |
| `hash not verifiable` | The name is non-ASCII, so the expected digest depends on the engine's locale. |

Exit status: `0` verified, `1` fail, `2` anything inconclusive or bad input.

## Coverage

Vocaloid 2 banks (`ARR2`, `ARR3`, `ARR4`) are fully checked. Vocaloid 3 and 4 banks (`DBSe`) carry
the same 260-byte store, but the value depends on the installed licence volume as well as the bank,
so it cannot be recomputed from the files alone. For those the tool reports the stored value and
does not judge it.

For V3 the store layout is confirmed on a retail bank, but the mechanism is inferred from V4 — the
V3 retail package ships only the library and no engine binary to compare against.

## Notes

* This is not an authenticity check. The constants involved are public, so a digest can be
  recomputed for any name. It detects accidental renames, not deliberate forgery.
* `unity-chan_for_Unity` does not follow the same rule as other `ARR4` banks. A mismatch there
  should be treated as unknown, not as tampering.

## License

MIT.
