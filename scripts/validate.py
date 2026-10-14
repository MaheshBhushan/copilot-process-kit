#!/usr/bin/env python3
"""Static/fixture checks only; never executes tenant actions, M, DAX or flow simulation."""
import csv
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
RESULTS = []


def check(condition, message):
    if not condition:
        raise ValueError(message)


def group(name, detail):
    RESULTS.append((name, detail))
    print(f'PASS {name}: {detail}')


def read_csv(relative):
    with (ROOT / relative).open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        check(reader.fieldnames and len(set(reader.fieldnames)) == len(reader.fieldnames), f'{relative}: duplicate/missing headers')
        check(rows and all(None not in r and all(v is not None for v in r.values()) for r in rows), f'{relative}: malformed/empty CSV')
        return rows, reader.fieldnames


def dt(value):
    check(value.endswith('Z'), 'Timestamp must use UTC Z')
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def unique(rows, field):
    values = [r[field] for r in rows]
    check(all(values) and len(values) == len(set(values)), f'Duplicate/blank {field}')


def validate():
    parsed = {str(p.relative_to(ROOT)): json.loads(p.read_text(encoding='utf-8'))
              for p in ROOT.rglob('*.json') if '.scratch' not in p.relative_to(ROOT).parts}
    contract = parsed['contracts/process.json']
    schema = parsed['contracts/sharepoint-schema.json']
    env = parsed['config/environment.example.json']
    group('JSON', f'{len(parsed)} files parse')
    fields = {name: {f['internalName']: f for f in table['fields']} for name, table in schema['lists'].items()}
    for name, table in schema['lists'].items():
        check(len(fields[name]) == len(table['fields']), f'{name}: duplicate fields')
        for f in table['fields']:
            check(all(k in f for k in ['type', 'required', 'default', 'writers', 'choices', 'indexed', 'unique']), f'{name}: field metadata')
            check(f['writers'] and isinstance(f['required'], bool), f'{name}: access/required metadata')
    check(fields['Orders']['Status']['choices'] == contract['states'], 'State choices differ')
    check(fields['Orders']['ProductType']['choices'] == contract['productTypes'], 'Product choices differ')
    check(fields['OrderCommands']['CommandType']['choices'] == contract['commands'], 'Command choices differ')
    check(fields['OrderCommands']['RequestKey']['required'] and fields['OrderCommands']['RequestKey']['unique'], 'RequestKey must be required/unique')
    check('ApprovalSnapshotPath' in fields['Orders'] and fields['ApprovalJobs']['ApprovalSnapshotPath']['required'], 'Snapshot contract missing')
    transitions = {(t['fromStatus'] or '', t['command']): t for t in contract['transitions']}
    check(len(transitions) == len(contract['transitions']) == 16, 'Transition table duplicate/incomplete')
    check({t['command'] for t in transitions.values()} == set(contract['commands']), 'Command transition coverage')
    for (source, command), t in transitions.items():
        check((not source or source in contract['states']) and t['toStatus'] in contract['states'], 'Transition enum')
        check(set(t['roles']) <= set(contract['roles']), 'Transition role')
        check(set(t['requiredInputs']) <= set(fields['OrderCommands']) | {'QCReference', 'WasteQuantity'}, 'Unknown command input')
    check(fields['Orders'] and schema['lists']['Orders']['staffAccess'] == 'Read', 'Orders staff access')
    check(schema['lists']['OrderEvents']['staffAccess'] == 'None', 'Events staff access')
    check(env['EnableAutomation'] is False and env['EnableNotifications'] is False, 'Configuration not disabled first')
    check(env['ApprovalTimeoutHours'] == contract['sla']['ApprovalTimeoutHours'] == 72 and env['ReminderHours'] == 24, 'SLA mismatch')
    group('Contracts', '16 transitions; enums, field metadata, RequestKey, snapshots, permissions and disabled config agree')

    tree = ET.parse(ROOT / 'process/print-order.bpmn')
    nodes = list(tree.iter())
    ids = {e.attrib['id']: e for e in nodes if 'id' in e.attrib}
    check(len(ids) == sum('id' in e.attrib for e in nodes), 'Duplicate BPMN IDs')
    local = lambda e: e.tag.split('}')[-1]
    for e in nodes:
        for attr in ['sourceRef', 'targetRef', 'attachedToRef', 'bpmnElement']:
            if attr in e.attrib:
                check(e.attrib[attr] in ids, f'BPMN unresolved {attr}')
        if local(e) in ['incoming', 'outgoing', 'flowNodeRef']:
            check(e.text.strip() in ids, 'BPMN unresolved text reference')
    shape_targets = {e.attrib['bpmnElement'] for e in nodes if local(e) == 'BPMNShape'}
    edge_targets = {e.attrib['bpmnElement'] for e in nodes if local(e) == 'BPMNEdge'}
    diagram_nodes = {'startEvent', 'endEvent', 'task', 'userTask', 'serviceTask', 'manualTask', 'exclusiveGateway', 'boundaryEvent', 'subProcess', 'lane'}
    for e in nodes:
        if local(e) in diagram_nodes:
            check(e.attrib['id'] in shape_targets, 'Missing BPMN DI shape')
        if local(e) == 'sequenceFlow':
            check(e.attrib['id'] in edge_targets, 'Missing BPMN DI edge')
        if local(e) == 'BPMNShape':
            bounds = next((b for b in e if local(b) == 'Bounds'), None)
            check(bounds is not None and float(bounds.attrib['width']) > 0 and float(bounds.attrib['height']) > 0, 'Invalid DI bounds')
        if local(e) == 'BPMNEdge':
            waypoints = [w for w in e if local(w) == 'waypoint']
            check(len(waypoints) >= 2 and all('x' in w.attrib and 'y' in w.attrib for w in waypoints), 'Invalid DI edge')
    required = ['Task_RecordOrder', 'Task_Preflight', 'Task_RequestApproval', 'Task_InternalApproval', 'Boundary_ApprovalTimeout',
                'Task_RecordExpiry', 'Task_ReleaseArtwork', 'Task_PrintFinish', 'Task_QualityCheck', 'Task_Rework', 'Task_CloseOrder', 'SubProcess_Cancel']
    check(set(required) <= set(ids), 'Required process node missing')
    ET.parse(ROOT / 'process/print-order.svg')
    group('BPMN/XML', f'{len(ids)} unique IDs; references and DI resolve; SVG parses (no XSD/runtime claim)')

    orders, oh = read_csv('data/Orders.csv')
    events, eh = read_csv('data/OrderEvents.csv')
    users, uh = read_csv('data/Users.csv')
    usage, ah = read_csv('data/Usage.csv')
    scenarios, sh = read_csv('data/scenarios.csv')
    check(oh == list(fields['Orders']) and eh == list(fields['OrderEvents']), 'Sample headers differ from schema')
    check(uh == ['UserKey','UPN','Role','EligiblePilot'], 'User headers')
    check(ah == ['EventID','EventAt','UserKey','Role','ActivityType','Outcome'], 'Usage headers')
    check(sh == ['ScenarioID','OrderKey','Scenario','ExpectedStatus','Note','EvidenceClass'], 'Scenario headers')
    check(len(orders) == 60 and len(users) == 12 and len({r['Scenario'] for r in scenarios}) >= 10, 'Fixture counts')
    for rows, key in [(orders,'OrderKey'), (events,'EventKey'), (events,'CommandID'), (users,'UserKey'), (users,'UPN'), (usage,'EventID'), (scenarios,'ScenarioID')]:
        unique(rows,key)
    for name, rows in [('Orders', orders), ('OrderEvents', events)]:
        for r in rows:
            for field, spec in fields[name].items():
                v = r[field]
                check(v or not spec['required'], f'{name}: required {field}')
                if not v:
                    continue
                if spec['choices']:
                    check(v in spec['choices'], f'{name}: invalid choice {field}')
                if spec['type'] == 'DateTime':
                    dt(v)
                if spec['type'] in ['Number', 'Currency']:
                    n = float(v)
                    check(n >= 0, f'{name}: negative {field}')
                    if spec.get('integer'):
                        check(n == int(n), f'{name}: noninteger {field}')
                    if 'minimum' in spec:
                        check(n >= spec['minimum'], f'{name}: below minimum')
                    if isinstance(spec.get('maximum'), (int,float)):
                        check(n <= spec['maximum'], f'{name}: above maximum')
                if 'maxLength' in spec:
                    check(len(v) <= spec['maxLength'], f'{name}: text length')
            if name == 'Orders':
                check(re.fullmatch(contract['identifiers']['OrderKey'], r['OrderKey']), 'Invalid OrderKey')
                check(dt(r['DueAt']) > dt(r['SubmittedAt']), 'Due date before submit')
                check(not r['WasteQuantity'] or int(r['WasteQuantity']) <= int(r['Quantity']), 'Waste exceeds quantity')
                check(not r['QuoteEUR'] or (float(r['QuoteEUR']) > 0 and re.fullmatch(r'\d+\.\d{2}',r['QuoteEUR'])), 'Currency format')
    check({r['Status'] for r in orders} == set(contract['states']), 'State coverage missing')
    check({r['ProductType'] for r in orders} == set(contract['productTypes']), 'Product coverage missing')
    check((max(dt(r['EventAt']) for r in events)-min(dt(r['EventAt']) for r in events)).days >= 56, 'Less than 8 weeks')
    group('CSV/schema', '60 orders, 12 users; exact typed headers, unique keys, ranges, all states/products, 8+ weeks')

    usermap = {r['UserKey']:r for r in users}
    upns = {r['UPN'] for r in users} | {'automation@example.invalid'}
    ordermap = {r['OrderKey']: r for r in orders}
    histories = defaultdict(list)
    for e in events:
        check(e['OrderKey'] in ordermap and e['ActorUPN'] in upns, 'Orphan event/user')
        histories[e['OrderKey']].append(e)
    asof = dt(contract['reportingRules']['sampleAsOfUtc'])
    approval_pairs = {}
    for key, order in ordermap.items():
        history = histories[key]
        check(history, 'Missing order history')
        previous, previous_time = '', None
        current_approval, requested, released = '', None, ''
        timestamp_fields = {k:'' for k in ['ApprovedAt','ProductionStartedAt','CompletedAt','CancelledAt']}
        for revision,e in enumerate(history,1):
            check(int(e['Revision']) == revision and e['EventKey'] == f'{key}-r{revision}', 'Event revision/key')
            check(e['FromStatus'] == previous, 'Event source does not follow history')
            t = transitions.get((previous,e['EventType']))
            check(t and t['toStatus'] == e['ToStatus'] and e['Role'] in t['roles'], 'Illegal event transition/role')
            at = dt(e['EventAt'])
            check(at <= asof and (previous_time is None or at > previous_time), 'Event chronology')
            if revision == 1:
                check(e['EventType'] == 'Submit' and order['SubmittedAt'] == e['EventAt'], 'Submit missing/immutable time')
                check(key == f"PO-{int(e['CommandID']):06}", 'OrderKey not from Submit ID')
                check(e['ActorUPN'] == order['SalesUPN'], 'Sales identity differs from submit Author')
            if e['EventType'] == 'Validate':
                current_approval, requested = f'{key}-r{revision}', at
                check(current_approval not in approval_pairs, 'Duplicate approval key')
                approval_pairs[current_approval] = at
            check(e['ApprovalKey'] == current_approval, 'Event ApprovalKey does not preserve requested revision')
            if e['EventType'] in ['ApprovalApproved','ApprovalRejected','ApprovalExpired']:
                elapsed = (at-requested).total_seconds()/3600
                check(elapsed >= 72 if e['EventType']=='ApprovalExpired' else 0 <= elapsed <= 72, 'Approval deadline')
                check(not e['DurationHours'] or float(e['DurationHours']) == elapsed, 'Wrong event duration')
            for cmd,field in [('ApprovalApproved','ApprovedAt'),('StartProduction','ProductionStartedAt'),('Complete','CompletedAt'),('Cancel','CancelledAt')]:
                if e['EventType'] == cmd:
                    timestamp_fields[field] = e['EventAt']
            if e['EventType'] == 'Release':
                released = f'ProductionFiles/{current_approval}-approved.pdf'
            previous, previous_time = e['ToStatus'], at
        check(order['Status'] == previous and int(order['Revision']) == len(history), 'Current status/revision differs from final event')
        check(order['LastCommandKey'] == f"CMD-{history[-1]['CommandID']}", 'Current LastCommandKey differs')
        check(all(order[k] == v for k,v in timestamp_fields.items()), 'Current timestamps differ from history')
        check(order['ApprovalKey'] == current_approval and order['ReleasedFilePath'] == released, 'Current approval/release snapshot differs')
        if current_approval:
            check(order['ApprovalSnapshotPath'] == f'ProductionFiles/ApprovalSnapshots/{current_approval}.pdf', 'Snapshot identity')
            check(dt(order['ApprovalRequestedAt']) == requested and dt(order['ApprovalDueAt']) == requested+timedelta(hours=72), 'Current approval times')
        else:
            check(not any(order[k] for k in ['ApprovalSnapshotPath','ApprovalRequestedAt','ApprovalDueAt','ApprovedAt']), 'Fabricated approval data')
    check({e['EventType'] for e in events} == set(contract['commands']), 'Missing command sample coverage')
    for s in scenarios:
        check(s['OrderKey'] in ordermap and s['ExpectedStatus'] == ordermap[s['OrderKey']]['Status'] and s['EvidenceClass']=='Synthetic fixture', 'Scenario mismatch')
    group('History/current snapshot', f'{len(events)} legal chronological transitions; approval request keys/deadlines and final fields reconcile')

    for u in users:
        check(u['Role'] in contract['roles'] and u['Role']!='Automation' and u['EligiblePilot']=='true', 'Invalid pilot cohort')
        check(u['UPN'].endswith('@example.invalid'), 'Non-synthetic user')
    for a in usage:
        check(a['UserKey'] in usermap and a['Role']==usermap[a['UserKey']]['Role'], 'Usage user/role mismatch')
        check(a['ActivityType'] in ['AgentSession','GuideViewed','TrainingCompleted','OrderCommand'], 'Usage activity')
        check(a['Outcome'] in ['Success','Escalated','Failed'] and dt(a['EventAt'])<=asof, 'Usage outcome/time')
    group('Synthetic usage', f'{len(usage)} separate activity rows; user joins, roles, outcomes and UTC times valid')

    # Independent aggregation: do not import the generator or its metric logic.
    status_counts = Counter(r['Status'] for r in orders)
    completed = [r for r in orders if r['Status']=='Completed']
    eligible = [r for r in completed if r['CompletedAt'] and r['DueAt']]
    ontime = sum(dt(r['CompletedAt']) <= dt(r['DueAt']) for r in eligible)
    active = [r for r in orders if r['Status'] not in ['Completed','Cancelled']]
    rework = {e['OrderKey'] for e in events if e['ToStatus']=='ChangesRequested'}
    cycles = [(dt(r['CompletedAt'])-dt(r['SubmittedAt'])).total_seconds()/3600 for r in completed]
    decisions = [e for e in events if e['EventType']=='ApprovalApproved']
    turnaround = [(dt(e['EventAt'])-approval_pairs[e['ApprovalKey']]).total_seconds()/3600 for e in decisions]
    sessions = [a for a in usage if a['ActivityType']=='AgentSession']
    weekly = defaultdict(set)
    for a in sessions:
        day = dt(a['EventAt']).date()
        weekly[(day-timedelta(days=day.weekday())).isoformat()].add(a['UserKey'])
    trained = {a['UserKey'] for a in usage if a['ActivityType']=='TrainingCompleted' and a['Outcome']=='Success' and usermap[a['UserKey']]['EligiblePilot']=='true'}
    mean = lambda values: round(sum(values)/len(values),6) if values else None
    ratio = lambda n,d: round(n/d,6) if d else None
    actual = dict(AsOfUtc=contract['reportingRules']['sampleAsOfUtc'], TotalOrders=len(orders), CompletedOrders=len(completed), ActiveOrders=len(active),
                  CompletionRate=ratio(len(completed),len(orders)), OnTimeCompletedOrders=ontime, OnTimeEligibleOrders=len(eligible),
                  OnTimeCompletionPct=ratio(ontime,len(eligible)), AverageCycleHours=mean(cycles), ApprovalTurnaroundHours=mean(turnaround),
                  SuccessfulApprovalEvents=len(decisions), AdministrativeReworkOrders=len(rework), ReworkRate=ratio(len(rework),len(orders)),
                  ActiveOverdue=sum(dt(r['DueAt']) < asof for r in active), AgentSessions=len(sessions), TrainingCompletedUsers=len(trained),
                  EligiblePilotUsers=len(users), TrainingCompletionPct=ratio(len(trained),len(users)),
                  WeeklyAgentUsers={k:len(v) for k,v in sorted(weekly.items())}, StatusCounts=dict(sorted(status_counts.items())),
                  EventCount=len(events), UsageEventCount=len(usage))
    check(actual == parsed['data/expected-metrics.json'], 'Expected metrics differ from independent CSV aggregation')
    golden = {'TotalOrders':60,'CompletedOrders':20,'ActiveOrders':35,'ActiveOverdue':30,'OnTimeCompletedOrders':15,
              'AverageCycleHours':81.0,'ApprovalTurnaroundHours':12.0,'ReworkRate':0.25,'AgentSessions':114,'TrainingCompletionPct':0.75}
    check(all(actual[k]==v for k,v in golden.items()), 'Fixed fixture expectation changed')
    group('Metrics', f'{len(actual)} exact metrics including all weekly/status buckets reconcile; fixed reference values agree')

    actions, headers = read_csv('flows/action-map.csv')
    check(headers == ['Flow','ActionId','ActionName','NativeAction','ContractRefs','BPMNRefs','Spec'], 'Action headers')
    check(len(actions)==96 and {r['Flow'] for r in actions}=={'F01','F02','F03','F04'}, 'Action counts/flows')
    unique(actions,'ActionId')
    builtins = {'ID','Created','Modified','Author','Editor'}
    for r in actions:
        check(all(r[k] for k in ['Flow','ActionId','ActionName','NativeAction','Spec']), 'Empty action metadata')
        check((ROOT/r['Spec']).is_file() and r['ActionName'] in (ROOT/r['Spec']).read_text(), 'Missing action guide/name')
        for ref in filter(None,r['ContractRefs'].split(';')):
            table,field = ref.split('.')
            check(table in fields and field in set(fields[table]) | builtins, f'Unknown action contract ref {ref}')
        check(set(filter(None,r['BPMNRefs'].split(';'))) <= set(ids), 'Unknown action BPMN ref')
    group('Action map', '96 unique actions across four native flow guides; schema/system-field and BPMN references resolve')
    acceptance, ac = read_csv('deployment/acceptance-cases.csv')
    evaluation, ec = read_csv('copilot/evaluation-cases.csv')
    unique(acceptance,'CaseID')
    unique(evaluation,'CaseId')
    check(len(acceptance)==35 and len(evaluation)==28, 'Acceptance/evaluation counts')
    for r in acceptance:
        check(all(r[k] for k in ['Name','Preconditions','Steps','Expected','EvidenceRequired']) and r['Status']=='Pending', 'Acceptance missing criteria/not Pending')
        check(not r['Tester'] and not r['TestedAt'], 'Invented acceptance test attribution')
    for r in evaluation:
        check(all(r[k] for k in ['Category','Identity','Steps','Prompt','Expected','Critical']), 'Evaluation missing criteria')
        check(all(r[k]=='Pending' for k in ['LiveResult','ObservedAnswer','CitationEvidence','SourceVersion','TestedAtUtc','Reviewer']), 'Invented live evaluation')
    group('Tenant/agent cases', '35 acceptance and 28 evaluation cases populated; every live result remains Pending')

    link_count = 0
    for p in ROOT.rglob('*.md'):
        if '.scratch' in p.relative_to(ROOT).parts:
            continue
        content = p.read_text(encoding='utf-8')
        for target in re.findall(r'!?\[[^\]]*\]\(([^\n]+?)\)',content):
            target = target.strip().split(' "')[0].strip('<>')
            if re.match(r'^(https?://|mailto:|app:)',target):
                continue
            filename, _, fragment = target.partition('#')
            destination = (p.parent/unquote(filename)).resolve() if filename else p
            check(destination.is_file(), f'Broken Markdown link {p.relative_to(ROOT)} -> {target}')
            check(destination.is_relative_to(ROOT), 'Markdown link escapes kit')
            if fragment and destination.suffix=='.md':
                anchors = []
                seen = Counter()
                for h in re.findall(r'^#{1,6}\s+(.+)$',destination.read_text(),re.M):
                    slug = re.sub(r'[^\w\- ]','',h.lower()).replace(' ','-')
                    anchors.append(slug if seen[slug]==0 else f'{slug}-{seen[slug]}')
                    seen[slug]+=1
                check(unquote(fragment) in anchors, f'Broken Markdown anchor {target}')
            link_count += 1
    group('Markdown links', f'{link_count} relative links/anchors resolve within kit')
    manifest = parsed['manifest.json']
    inventory = {r['path']:r for r in manifest['artifacts']}
    check(len(inventory)==len(manifest['artifacts']), 'Duplicate manifest paths')
    actual_files = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()
                    and not any(part in {'.scratch','__pycache__','.git'} for part in p.relative_to(ROOT).parts)}
    check(actual_files == set(inventory), f'Manifest missing/extra: {actual_files ^ set(inventory)}')
    check(all(r.get('class') and r.get('status') and r.get('purpose') for r in inventory.values()), 'Manifest metadata')
    check(manifest['tenantStatus']=='Pending' and manifest['powerBIRuntimeStatus']=='Pending', 'Manifest runtime claim')
    check(not any(Path(p).suffix.lower() in {'.pbix','.zip','.msapp'} for p in actual_files), 'Fake export candidate')
    group('Manifest/artifact classes', f'{len(inventory)} files inventoried; no PBIX/solution export claim; tenant and Desktop Pending')
    proof = parsed['validation/determinism.json']
    hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted((ROOT/'data').iterdir()) if p.suffix in {'.csv','.json'}}
    check(proof['first'] == proof['second'] == hashes and proof['outsideWorkingDirectory']=='/', 'Determinism proof/current hashes differ')
    group('Determinism', f'{len(hashes)} CSV/JSON SHA256 hashes identical across two runs, including a run from /')
    now = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
    lines = ['# Local verification report','',f'Observed at {now}. Python {sys.version.split()[0]}.',
             '', 'Commands actually run:', '', '```sh', 'python3 scripts/generate_samples.py',
             'cd / && python3 "'+str(ROOT/'scripts/generate_samples.py')+'"',
             'python3 scripts/validate.py', '```', '',
             'The two generator invocations and their recorded hashes are in [determinism.json](determinism.json).', '',
             '| Validation group | Actual result |','|---|---|']
    lines += [f'| {name} | PASS: {detail} |' for name,detail in RESULTS]
    lines += ['',f'Validator exit: 0. {len(RESULTS)} validation groups passed.', '',
              '## Generated SHA256 values', '', '| File | SHA256 |','|---|---|']
    lines += [f'| {p} | `{h}` |' for p,h in hashes.items()]
    lines += ['', '## Scope of evidence', '',
              'Local checks parse JSON/XML/CSV, inspect cross-references, enforce fixture invariants and independently aggregate metrics. No Microsoft service was contacted. No BPMN XSD validator, Power BI Desktop, M/DAX runtime, connector action, flow run, permission boundary or notification delivery was executed. All tenant acceptance, live agent evaluation, Power BI runtime and live usage refresh remain Pending.', '',
              'Deployment remains HOLD if the required deprecated Copy file action cannot provide the documented explicit destination filename and no-overwrite behavior. A replacement requires approval and tenant proof before enabling flows.', '']
    (ROOT/'validation/local-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(f'PASS {len(RESULTS)} validation groups; exit 0; wrote validation/local-report.md')


if __name__ == '__main__':
    try:
        validate()
    except (ValueError, KeyError, TypeError, OSError, ET.ParseError, json.JSONDecodeError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
