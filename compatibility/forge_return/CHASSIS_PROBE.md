# Bounded deterministic Archivist probe

Status: opt-in local test adapter. This extends the PR #64 compatibility work
with one actual invocation of existing deterministic code and a separate
readback command. It changes no production Forge registration, runtime hook,
institutional schema, workflow, or incoming event.

## What runs

Forge still declares `avot_agents.archivist:run` in
`sovereign-intel/avot-archivist`. Its runtime remains a simulator. This probe
retains the original formatted invocation and records an explicit **local test
mapping** to:

- Repository: `sovereign-codex/AVOT-ARCHIVIST`
- Revision: `4a6ab60069e4d5adea8e29a98670bd90f1536353`
- Callable: `avot_chassis.examples.archivist.Archivist.summarize(text)`

The existing method checks a chassis permission and returns the first 120
trimmed characters with a fixed prefix. It is not a model call. Only the two
pinned source files are verified and compiled in memory; their module bodies
execute after the worker restrictions are installed. The example
`run_archivist.main()` is not invoked; its ledger append
is outside this test.

The implementation uses a fixed public synthetic text, an M0/S3 test registry,
and a synthetic header. Its retained mapping is not an activated alias or a
claim that the production Forge entrypoint executed.

## Execution and readback

From the Tyme-Lab root, use Python 3.12 on unprivileged Linux with
`libseccomp.so.2`, PyYAML, and jsonschema available. Supply trusted source
snapshots for Forge and Archivist. The existing `sources.json` and the new
worker's fixed source hashes reject changed dependency bytes. The source roots
can be extracted snapshots; the check does not authenticate their Git history.

Run the baseline and new tests:

```sh
python -B compatibility/forge_return/verify.py --forge-root ../AVOT-forge
python -B compatibility/forge_return/chassis_cases.py --forge-root ../AVOT-forge --archivist-root ../AVOT-ARCHIVIST
```

The new suite contains 12 test methods. It creates disposable local runs for
positive and refusal cases, exercises the boundary, and tests timeout/output
exhaustion. These are separate synthetic test cases, not automatic retries of
an institutional assignment.

Execute one retained demonstration into a new directory:

```sh
python -B compatibility/forge_return/chassis_probe.py run --forge-root ../AVOT-forge --archivist-root ../AVOT-ARCHIVIST --output /path/to/new-probe-bundle
```

Save its printed `expected_manifest_sha256`, `expected_assignment_id`, and
`expected_request_id` outside that bundle. Then start a new interpreter and
pass those retained values to the separate command:

```text
python -B compatibility/forge_return/chassis_probe.py readback
  --bundle /path/to/new-probe-bundle
  --manifest-sha256 <separately retained manifest digest>
  --assignment-id <separately retained assignment ID>
  --request-id <separately retained request ID>
```

The multiline example shows the required arguments; pass them as one shell
command. Do not derive the expected digest or identities anew from potentially
changed bundle contents. The anchor is an integrity expectation held by the
caller, not a signature or authenticated institutional custody record.

The run refuses an existing output directory. Each run gets fresh request,
assignment, and activation identities. This prevents accidental reuse of the
same local destination; it is not a durable institution-wide deduplication
service. The readback command writes only its report to stdout and does not
modify the bundle. Keep that report separately to avoid a circular manifest.

## Enforced worker controls

Before any pinned source module executes, `chassis_boundary.py` installs
`no_new_privs` and a Linux seccomp syscall allowlist. After preparation it denies
filesystem opens, reads, metadata and mutation syscalls, socket/network calls,
and process creation or exec. It allows writes only to the stdout/stderr pipes,
limited memory-management calls, and necessary timing/signal/exit calls. It does
not create a filesystem or user namespace.

The worker exercises socket creation, file read-open, file write-open, and fork
denial before invoking the callable. Missing or weaker controls block execution.
Its control report states the exact rules and their limits; readback rejects
substituted rules, omitted denials, and unsupported namespace claims.

| Bound | Enforced by |
| --- | --- |
| 30-second wall ceiling | Parent monotonic deadline and process-group termination |
| 1 MiB combined stdout/stderr ceiling | Parent nonblocking pipe reader |
| 25-second worker alarm | Worker default-action SIGALRM |
| 5 seconds CPU | Worker resource limit |
| 256 MiB address space | Worker resource limit |
| Zero file/core output; zero child-process allowance | Worker resource limits plus syscall restrictions |
| 16 descriptors | Worker resource limit; parent closes extra descriptors |
| Fresh working directory and sanitized environment | Parent process setup |

Inherited stricter resource limits are accepted and reported. Unsupported Linux
controls, missing libseccomp, source drift, or an execution error do not trigger
an unrestricted fallback. The parent attempts to terminate the whole process
group on cleanup, including when its leader has already exited. Failures,
refusals, partial output, timeouts, and output exhaustion are retained.

This boundary is for the reviewed, pinned callable. The controller, verifier,
Python environment, imported dependencies, and operating system remain trusted.
It is not a general service for executing arbitrary hostile repositories. The
workload cannot open the retained bundle or evaluator after its restrictions
are installed; the controlling operator still owns those files. Byte hashes
and permissions do not make that operator institutionally independent.

## Evidence meanings

The parent retains the assignment, fixed input, explicit mapping, original
Forge-formatted invocation, source pins, raw worker output, observer record,
and a manifest of exact bytes. The worker's output is observed local process
output, not a provider attestation.

Successful computation projects to the existing `EVIDENCE_RETURN_v0.1` value
`no_material_change`: synthetic input produces no research signal. The actual
deterministic output is retained separately. Refusal/failure projects to
`failed`, with the original worker status and reason preserved. `returned` and
`dormancy_entered` describe only this local child and retained result; they do
not describe an Office agent or institutional delivery.

Readback checks the externally supplied anchor, exact assignment/version/request
and activation bindings, source and controller identities, implementation and
permission mapping, timestamps, expected output, and local phase projections.
It reuses the existing monitor byte/schema/identity functions. It does not call
the task method to manufacture its expected output.

The complete monitor checker receives `authorization_verified: false` and an
assignment with `status: local_test_only`. It therefore returns:

```json
{
  "disposition": "blocked_authorization",
  "packet_consistency": "not_checked"
}
```

That early return is intentional. The wrapper performs its own strict local
phase, tracker, context, permission, timestamp, and return checks. Do not report
the full institutional checker as having passed the packet.

A successful separate readback reports:

```json
{
  "classification": "deterministic_chassis_local_readback",
  "local_callable_execution": "observed_by_local_controller",
  "retained_bytes": "match_separately_supplied_anchor",
  "semantic_output": "pass",
  "existing_return_schema_and_identity": "pass",
  "forge_production_runtime_executed": false,
  "model_inference_executed": false,
  "authenticated_custody": "not_established",
  "institutional_independence": "not_established",
  "institutional_effect": "none"
}
```

Fresh-process readback demonstrates a separate retrieval path under the same
operator. It does not establish independent institutional review. The historical
PR #64 fixture, its clock, and its expected report remain unchanged; its
`synthetic_readback_only` result is distinct from this actual local computation.

## Remaining integration

This completes a local deterministic implementation and readback exercise. The
production Forge binding, authenticated custody, durable cross-process duplicate
handling, and actual monitor/Office return remain separate work. Reuse the
existing Archivist real-inference handoff and AVOT-engine probe when model
inference is the objective. No file belongs in an `incoming/` directory as part
of this probe: that would trigger a different, live ingestion path.
