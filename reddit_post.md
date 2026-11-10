**Title:** I made a tool to verify the integrity of Vocaloid voicebanks

**Body:**

I made a small tool to verify the integrity of Vocaloid voicebanks, mostly because there are a lot
of posts here from people wondering whether theirs are corrupted or broken.

You point it at a `.ddi` and it tells you whether the voicebank's stored digest still matches its
name. That's usually the reason a bank stops loading after the folder or `.ddb` got renamed.

```console
$ vocaloid-integrity-check Yuki.ddi --ddb Yuki.ddb
hash verified
```

It reports `hash verified`, `hash fail`, `hash not present` or `hash present, not checkable`.
Standard library only, Python 3.10+, and it only reads the file — nothing is modified.

- PyPI: `pip install vocaloid-integrity-check`
- Source (MIT): [GITHUB LINK]
