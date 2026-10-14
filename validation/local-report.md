# Local verification report

Observed at 2026-10-14T17:15:05Z. Python 3.14.6.

Commands actually run:

```sh
python3 scripts/generate_samples.py
cd / && python3 "/run/media/maheshk/New Volume/MK-solutions/copilot-process-kit/scripts/generate_samples.py"
python3 scripts/validate.py
```

The two generator invocations and their recorded hashes are in [determinism.json](determinism.json).

| Validation group | Actual result |
|---|---|
| JSON | PASS: 6 files parse |
| Contracts | PASS: 16 transitions; enums, field metadata, RequestKey, snapshots, permissions and disabled config agree |
| BPMN/XML | PASS: 114 unique IDs; references and DI resolve; SVG parses (no XSD/runtime claim) |
| CSV/schema | PASS: 60 orders, 12 users; exact typed headers, unique keys, ranges, all states/products, 8+ weeks |
| History/current snapshot | PASS: 255 legal chronological transitions; approval request keys/deadlines and final fields reconcile |
| Synthetic usage | PASS: 147 separate activity rows; user joins, roles, outcomes and UTC times valid |
| Metrics | PASS: 22 exact metrics including all weekly/status buckets reconcile; fixed reference values agree |
| Action map | PASS: 96 unique actions across four native flow guides; schema/system-field and BPMN references resolve |
| Tenant/agent cases | PASS: 35 acceptance and 28 evaluation cases populated; every live result remains Pending |
| Markdown links | PASS: 108 relative links/anchors resolve within kit |
| Manifest/artifact classes | PASS: 54 files inventoried; no PBIX/solution export claim; tenant and Desktop Pending |
| Determinism | PASS: 6 CSV/JSON SHA256 hashes identical across two runs, including a run from / |

Validator exit: 0. 12 validation groups passed.

## Generated SHA256 values

| File | SHA256 |
|---|---|
| data/OrderEvents.csv | `21a0d2108f94c8a59bc5b2ade38e77ccd25d692890f264db8d8f0b23584595d5` |
| data/Orders.csv | `f7b01a293ef3a50945c37edbeda26ee7fd051ef9d7ee001c84254b593ac5d88f` |
| data/Usage.csv | `c439da9ceb7172bb0c07650a6d7ed13082ecc0147d9cf71668b9c1f2eccc285f` |
| data/Users.csv | `4610dbceac092e145b2d90e8850609cfc2957266d417714c593b1a3c1e22e2f0` |
| data/expected-metrics.json | `171ab6c2c24b16d3b342142239cebebf3a9188785c40cc76770209d8e4cbb20b` |
| data/scenarios.csv | `0989ac190ae41ba5931898e985cc050713e3444a7655b016b4ff9067287c0d35` |

## Scope of evidence

Local checks parse JSON/XML/CSV, inspect cross-references, enforce fixture invariants and independently aggregate metrics. No Microsoft service was contacted. No BPMN XSD validator, Power BI Desktop, M/DAX runtime, connector action, flow run, permission boundary or notification delivery was executed. All tenant acceptance, live agent evaluation, Power BI runtime and live usage refresh remain Pending.

Deployment remains HOLD if the required deprecated Copy file action cannot provide the documented explicit destination filename and no-overwrite behavior. A replacement requires approval and tenant proof before enabling flows.
