# vocaloid-integrity-check

Check a Vocaloid voicebank when you’re concerned that it may be corrupted or was renamed.

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

`--json` prints machine-readable output. If `--ddb` is omitted, the `.ddi` filename is used.

## Results

- `hash verified` — the check succeeded.
- `hash fail` — the check found a mismatch.
- `hash present, not checkable` — a value is present, but cannot be judged from the files alone (Vocaloid 3/4).
- `hash not present` — no value was found.
- `hash not verifiable` — the name cannot be checked in the current environment.

Exit status: `0` verified, `1` fail, `2` inconclusive or invalid input.

Vocaloid 2 banks are checked. Vocaloid 3/4 banks are recognized, but reported as not checkable rather than verified or failed.

## Notes

This is an integrity check, not an authenticity check. `unity-chan_for_Unity` is a known exception; treat a mismatch for it as unknown.

## License

MIT.
