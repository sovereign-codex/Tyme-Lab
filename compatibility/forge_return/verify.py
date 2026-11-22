"""Opt-in, local Forge return compatibility review."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]


def offline(event, args):
    if event.startswith(("socket.", "subprocess.")) or event in {"os.system", "os.posix_spawn"}:
        raise RuntimeError("Offline review forbids " + event)
    if event == "import" and args[0].split(".")[0] == "avot_agents":
        raise RuntimeError("AVOT entrypoint imports forbidden")


def check_sources(roots):
    lock = json.loads((HERE / "sources.json").read_text())
    for repo, root in roots.items():
        for name, expected in lock[repo]["files"].items():
            path = root / name
            if not path.is_file():
                raise SystemExit(f"Required source missing: {repo}/{name}")
            raw = path.read_bytes()
            header = b"blob " + str(len(raw)).encode() + b"\0"
            if hashlib.sha1(header + raw).hexdigest() != expected:
                raise SystemExit(f"Source differs from reviewed revision: {repo}/{name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forge-root", type=Path, required=True)
    parser.add_argument("--report", action="store_true", help="Print the fixture classification")
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    sys.addaudithook(offline)
    forge = args.forge_root.resolve()
    check_sources({"forge": forge, "lab": LAB})
    sys.path[:0] = [str(HERE), str(forge / "python"), str(LAB), str(LAB / "tests")]
    if args.report:
        from adapter import assess, build
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            build(base)
            print(json.dumps(assess(base), indent=2))
        return 0
    suite = unittest.defaultTestLoader.loadTestsFromNames(["test_monitor_circuit_readback_v0", "cases"])
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
