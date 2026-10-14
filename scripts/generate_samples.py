#!/usr/bin/env python3
"""Create synthetic CSV fixtures only. Uses no Microsoft connection or real identities."""
import csv
import json
import random
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
ASOF = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)


def stamp(value):
    return value.isoformat(timespec='seconds').replace('+00:00', 'Z')


def write_csv(name, rows, fields=None):
    with (DATA / name).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fields or list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def generate():
    DATA.mkdir(exist_ok=True)
    rng = random.Random(42)
    contract = json.loads((ROOT / 'contracts/process.json').read_text())
    schema = json.loads((ROOT / 'contracts/sharepoint-schema.json').read_text())
    roles = ['Sales'] * 3 + ['Prepress'] * 2 + ['Approver'] * 2 + ['Production'] * 3 + ['Owner'] * 2
    users = [dict(UserKey=f'U{i:02}', UPN=f'u{i:02}@example.invalid', Role=role, EligiblePilot='true')
             for i, role in enumerate(roles, 1)]
    actor = {role: next(u['UPN'] for u in users if u['Role'] == role) for role in set(roles)}
    actor['Automation'] = 'automation@example.invalid'
    full = ['Submit', 'Validate', 'ApprovalApproved', 'Release', 'StartProduction', 'Complete']
    scenarios = [
        ('Completed on time', full, 'Normal approved snapshot and passed QC.'),
        ('Completed late', full, 'Completion one day after due time.'),
        ('Administrative correction', ['Submit', 'RequestChanges', 'Resubmit'] + full[1:], 'Correction before approval; administrative rework.'),
        ('Rejected then resubmitted', full[:2] + ['ApprovalRejected', 'Resubmit'] + full[1:], 'New ApprovalKey after rejection; successful decision matches new key.'),
        ('Approval expired', full[:2] + ['ApprovalExpired'], '72 hours elapsed; late response cannot revive this order.'),
        ('Cancelled before approval', ['Submit', 'Cancel'], 'Sales cancellation with reason; no production.'),
        ('Submitted backlog', ['Submit'], 'Active overdue order awaits preflight.'),
        ('Awaiting approval', full[:2], 'Recent request within 72-hour window; no response yet.'),
        ('Approved awaiting release', full[:3], 'Synthetic file-copy uncertainty drill; hold release until operator verifies snapshot and destination.'),
        ('Ready for production', full[:4], 'Synthetic notification uncertainty drill; outbox NeedsReview does not reverse release.'),
        ('In production', full[:5], 'Manual QC rework may occur without extra business transition.'),
        ('Changes requested', ['Submit', 'RequestChanges'], 'Missing consent/artwork drill; no approval request created.'),
    ]
    orders, events, scenario_rows = [], [], []
    command_id = 0
    for i in range(60):
        kind = i % len(scenarios)
        label, path, note = scenarios[kind]
        key = f'PO-{command_id + 1:06}'
        submitted = ASOF - timedelta(days=63 - (i // 12) * 7, hours=i % 3)
        if kind == 7:
            submitted = ASOF - timedelta(hours=24 + i // 12)
        due = submitted + timedelta(days=5)
        if kind == 1:
            due = submitted + timedelta(hours=54)
        row = {f['internalName']: '' for f in schema['lists']['Orders']['fields']}
        row.update(Title=f'Synthetic {label}, batch {i + 1}', OrderKey=key, CustomerCode=f'C{i % 15 + 1:03}',
                   ProductType=contract['productTypes'][i % 4], Quantity=rng.choice([100, 250, 500, 1000]),
                   DueAt=stamp(due), SubmittedAt=stamp(submitted), SalesUPN=users[i % 3]['UPN'])
        previous = None
        at = submitted
        requested = None
        for revision, command in enumerate(path, 1):
            command_id += 1
            if revision > 1:
                at += timedelta(hours=72 if command == 'ApprovalExpired' else 18 if command == 'Complete' else 12)
            transition = next(t for t in contract['transitions'] if t['fromStatus'] == previous and t['command'] == command)
            role = transition['roles'][0]
            duration = ''
            if command == 'Validate':
                requested = at
                row.update(QuoteEUR=f'{rng.randrange(50, 1500)}.00', ApproverUPN=actor['Approver'],
                           ApprovalRequestedAt=stamp(at), ApprovalDueAt=stamp(at + timedelta(hours=72)),
                           ApprovalKey=f'{key}-r{revision}', DraftFilePath=f'DraftArtwork/{key}.pdf',
                           ApprovalSnapshotPath=f'ProductionFiles/ApprovalSnapshots/{key}-r{revision}.pdf',
                           CustomerConsentRef=f'CONSENT-{key}')
            if command in ['ApprovalApproved', 'ApprovalRejected']:
                duration = (at - requested).total_seconds() / 3600
            if command == 'ApprovalApproved':
                row['ApprovedAt'] = stamp(at)
            if command == 'Release':
                row['ReleasedFilePath'] = f"ProductionFiles/{row['ApprovalKey']}-approved.pdf"
            if command == 'StartProduction':
                row.update(ProductionStartedAt=stamp(at), ProductionUPN=actor['Production'])
            if command == 'Complete':
                row.update(CompletedAt=stamp(at), QCReference=f'QC-{key}', WasteQuantity=rng.randrange(0, 10))
            if command == 'Cancel':
                row['CancelledAt'] = stamp(at)
            row.update(Status=transition['toStatus'], Revision=revision, LastCommandKey=f'CMD-{command_id}')
            events.append(dict(Title=f'{key} {command}', EventKey=f'{key}-r{revision}', OrderKey=key,
                               CommandID=command_id, FromStatus=previous or '', ToStatus=row['Status'], Revision=revision,
                               EventAt=stamp(at), ActorUPN=row['SalesUPN'] if role == 'Sales' else actor[role], Role=role, EventType=command,
                               ApprovalKey=row['ApprovalKey'], DurationHours=duration))
            previous = row['Status']
        orders.append(row)
        scenario_rows.append(dict(ScenarioID=f'SC-{i + 1:02}', OrderKey=key, Scenario=label,
                                  ExpectedStatus=row['Status'], Note=note, EvidenceClass='Synthetic fixture'))
    usage = []
    for week in range(9):
        for u in users[:4 + week % 7]:
            for session in range(1 + rng.randrange(3)):
                usage.append(dict(EventID=f'US-{len(usage)+1:04}', EventAt=stamp(ASOF - timedelta(days=62-week*7, hours=session)),
                                  UserKey=u['UserKey'], Role=u['Role'], ActivityType='AgentSession',
                                  Outcome=rng.choice(['Success', 'Success', 'Escalated', 'Failed'])))
        usage.append(dict(EventID=f'US-{len(usage)+1:04}', EventAt=stamp(ASOF-timedelta(days=62-week*7)),
                          UserKey=users[week]['UserKey'], Role=users[week]['Role'], ActivityType='TrainingCompleted', Outcome='Success'))
    for i, u in enumerate(users):
        for activity in ['GuideViewed', 'OrderCommand']:
            usage.append(dict(EventID=f'US-{len(usage)+1:04}', EventAt=stamp(ASOF-timedelta(days=i+1)),
                              UserKey=u['UserKey'], Role=u['Role'], ActivityType=activity, Outcome='Success'))
    write_csv('Orders.csv', orders)
    write_csv('OrderEvents.csv', events)
    write_csv('Users.csv', users)
    write_csv('Usage.csv', usage)
    write_csv('scenarios.csv', scenario_rows)
    # Aggregate the serialized facts; fixture construction counters are not metric inputs.
    with (DATA / 'Orders.csv').open(newline='') as f:
        facts = list(csv.DictReader(f))
    with (DATA / 'OrderEvents.csv').open(newline='') as f:
        history = list(csv.DictReader(f))
    with (DATA / 'Usage.csv').open(newline='') as f:
        activity = list(csv.DictReader(f))
    dt = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))
    completed = [r for r in facts if r['Status'] == 'Completed']
    active = [r for r in facts if r['Status'] not in contract['terminalStates']]
    ontime = sum(dt(r['CompletedAt']) <= dt(r['DueAt']) for r in completed)
    rework = len({e['OrderKey'] for e in history if e['ToStatus'] == 'ChangesRequested'})
    approval_requests = {e['ApprovalKey']: dt(e['EventAt']) for e in history if e['EventType'] == 'Validate'}
    approval_hours = [(dt(e['EventAt']) - approval_requests[e['ApprovalKey']]).total_seconds()/3600
                      for e in history if e['EventType'] == 'ApprovalApproved']
    weekly = {}
    for e in activity:
        if e['ActivityType'] == 'AgentSession':
            day = dt(e['EventAt']).date()
            monday = (day - timedelta(days=day.weekday())).isoformat()
            weekly.setdefault(monday, set()).add(e['UserKey'])
    metrics = dict(AsOfUtc=stamp(ASOF), TotalOrders=len(facts), CompletedOrders=len(completed), ActiveOrders=len(active),
                   CompletionRate=round(len(completed)/len(facts), 6), OnTimeCompletedOrders=ontime,
                   OnTimeEligibleOrders=len(completed), OnTimeCompletionPct=round(ontime/len(completed), 6),
                   AverageCycleHours=round(sum((dt(r['CompletedAt'])-dt(r['SubmittedAt'])).total_seconds()/3600 for r in completed)/len(completed), 6),
                   ApprovalTurnaroundHours=round(sum(approval_hours)/len(approval_hours), 6), SuccessfulApprovalEvents=len(approval_hours),
                   AdministrativeReworkOrders=rework, ReworkRate=round(rework/len(facts), 6),
                   ActiveOverdue=sum(dt(r['DueAt']) < ASOF for r in active),
                   AgentSessions=sum(e['ActivityType']=='AgentSession' for e in activity),
                   TrainingCompletedUsers=len({e['UserKey'] for e in activity if e['ActivityType']=='TrainingCompleted' and e['Outcome']=='Success'}),
                   EligiblePilotUsers=12, TrainingCompletionPct=0.75,
                   WeeklyAgentUsers={k:len(v) for k,v in sorted(weekly.items())}, StatusCounts=dict(sorted(Counter(r['Status'] for r in facts).items())),
                   EventCount=len(history), UsageEventCount=len(activity))
    (DATA/'expected-metrics.json').write_text(json.dumps(metrics, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == '__main__':
    generate()
