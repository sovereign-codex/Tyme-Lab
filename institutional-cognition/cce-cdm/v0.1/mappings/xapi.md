# CCE → xAPI Projection v0.1

## Purpose

Export a minimum-purpose learning-experience statement without treating an LRS as the canonical developmental record.

| CCE | xAPI | Rule |
|---|---|---|
| `participant.id` | `actor.account.name` or pseudonymous identifier | Do not expose a broader identity than required |
| `action.verb` | `verb.id` and `verb.display` | Map through a governed verb registry |
| `action.object` | `object.id` and `definition.name` | Mint a stable activity identifier |
| `context` | `context.contextActivities` / extensions | Export only authorized context |
| `action.result` | `result` | Remove private narrative unless essential |
| `occurred_at` | `timestamp` | For intervals, export end time and a duration when appropriate |
| `evidence` | `attachments` or extensions | Prefer integrity-safe references; never leak private locations |
| `event_id` | statement extension | Preserve reversible source linkage |

## Excluded by default

- raw reflection;
- consent receipt contents;
- full developmental signals;
- guardian information;
- undisclosed lineage;
- private evidence locations.

## Projection receipt

Every projection should record source event ID, target purpose, fields released, transformations, semantic losses, timestamp, recipient, and derived artifact digest.

## Known semantic loss

xAPI expresses an experience statement well but does not natively carry the complete sovereignty, contestation, progressive guardianship, or temporal interpretation model. Those remain canonical in CCE/CDM.
