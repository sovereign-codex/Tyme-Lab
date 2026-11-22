# Synthetic Forge return compatibility

Run from the Tyme-Lab root with Python 3.12, PyYAML and jsonschema available locally.

```sh
python -B compatibility/forge_return/verify.py --forge-root ../AVOT-forge
```

Append `--report` to emit the local classification. Both modes check the input file bytes against sources.json before importing repository modules. Supply trusted local source roots. Each lock entry identifies the reviewed commit and relevant Git blobs. The check also works with an extracted snapshot and does not verify Git history or authenticate anyone.

The fixture resolves the registered Archivist identity, formats a Forge invocation and joins an explicitly simulated result to the retained Lab inputs. The proposed adapter is test-only. The normal monitor workflow does not discover these cases automatically. The review clock and tool snapshots come from the pinned PR #63 synthetic fixture. Readiness and activation fields describe that scenario. Provider authentication, real authorization and runtime completion remain unestablished.

The regression test compares the entire generated report, including retained file hashes, to expected-report.json from the original review. Inspect any differences before changing the fixture, report or pins together. The offline run uses temporary directories and a Python audit guard for socket, subprocess and AVOT entrypoint imports. Use a trusted Python environment.
