"""Reviewed demo content and transparent, non-predictive prototype calculations."""
import json
import re
from datetime import datetime, timezone

PRODUCT = 'evidence-path-local'
VERSION = '1.0.0'
CRITERIA = [
    {'id': 'reasoning', 'name': 'Reasoning', 'description': 'Identifies the problem and explains a feasible decision.'},
    {'id': 'communication', 'name': 'Communication', 'description': 'Explains the change, audience and requested agreement.'},
    {'id': 'prioritization', 'name': 'Prioritization', 'description': 'Handles deadlines, dependencies and competing commitments.'},
    {'id': 'verification', 'name': 'Information checking', 'description': 'Checks uncertainty before making a consequential claim.'},
]
STATUS_LABELS = {'draft':'In progress','submitted':'Awaiting review','invited':'Assessment invited',
    'assessment_submitted':'Assessment received','interview':'Interview selected',
    'not_proceeding':'Not proceeding','withdrawn':'Withdrawn'}
ANCHORS = [
    '1 · A material requirement is missing',
    '2 · Partial response with a consequential gap',
    '3 · Meets the task requirement',
    '4 · Meets it and anticipates a relevant contingency',
]
QUESTIONS = [
    {'id':'ownership','label':'Your contribution','prompt':'Which part of the decision was yours, and what did another person contribute?'},
    {'id':'tradeoff','label':'A trade-off','prompt':'What alternative did you consider, and what information changed your choice?'},
    {'id':'learning','label':'What you learned','prompt':'What would you do differently now? Explain a concrete change.'},
]
PREFERENCES = [
    'I prefer to clarify an unclear request before starting.',
    'I like to compare alternatives before choosing an approach.',
    'I find it useful to write down commitments and deadlines.',
    'I ask for feedback when I am uncertain about my work.',
    'I prefer to explain a trade-off when priorities conflict.',
    'I am comfortable saying that I do not yet know an answer.',
    'I like to check how my work affects the next person.',
    'I prefer explicit instructions when learning a new task.',
    'I am comfortable revising a plan when new facts emerge.',
    'I find examples helpful when learning a new process.',
]
MICRO_TASK = {
    'title':'A promise and a missing fact',
    'context':'It is 10:00. A colleague wants you to confirm a delivery date to a customer by 10:10. The shared record lists two different dates. Your supervisor can check the source record at 10:05.',
    'prompt':'Write the next action you would take and a short update to your colleague. You can describe more than one reasonable approach.',
}
SCENARIO = {
    'version':'coordination-v1', 'title':'The update before lunch',
    'context':'You coordinate a small customer service team. It is 11:20. A client needs a verified attendance update by 11:40. A colleague asks for the same figures for an internal meeting at 11:30. The spreadsheet lists 42 registrations, but two rows have the same registration ID.',
    'facts':[
        'You can inspect the registration IDs and the original booking log.',
        'The operations lead is available at 11:25 to resolve any remaining discrepancy.',
        'The client can accept a short status update at 11:30 while verification continues.',
        'You can propose a changed internal deadline, but your colleague must agree.',
        'You cannot change a booking or promise a verified count without checking the source.',
    ],
    'fields':[
        {'id':'plan','label':'Your action plan','prompt':'Explain the order of your actions, what you would verify, and who needs to agree.'},
        {'id':'message','label':'Your message to the colleague','prompt':'Write the update you would send about the 11:30 request.'},
        {'id':'contingency','label':'If the discrepancy remains','prompt':'Explain what you would communicate or escalate before 11:40.'},
    ],
}
DEFAULT_ROLE = {
    'title':'Service & operations coordinator', 'organization':'Local demonstration employer',
    'description':'Help a small team coordinate requests, check information and communicate changes. Demonstrate relevant experience from paid work, volunteering, caregiving or personal projects.',
    'requirements':'Explain your decisions clearly. Work through competing requests. Check facts before making commitments. No particular school, employer or formal internship is required.',
    'skills':['coordination','communication','planning','customer','team','verification'],
    'weights':{'reasoning':25,'communication':25,'prioritization':25,'verification':25},
    'open':True,
}

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def clean_text(value, limit=12000):
    if not isinstance(value,str):
        raise ValueError('A text value was expected.')
    if len(value)>limit:
        raise ValueError(f'Text exceeds the {limit:,}-character limit.')
    return value.replace('\x00','').strip()

def alignment(application, role):
    """Keyword coverage, explicitly not a capability or success prediction."""
    fields=application.get('fields',{})
    evidence=' '.join(str(fields.get(k,'')) for k in ['experience','skills','story','resume_text','cover_text'])
    evidence+=' '+' '.join(f.get('extracted_text','') for f in application.get('files',[]) if f.get('kind')!='video')
    tokens=set(re.findall(r'[a-z]+',evidence.lower()))
    skills=role.get('skills',[])
    matched=[s for s in skills if any(t.startswith(s.lower()) or s.lower().startswith(t) for t in tokens if len(t)>3)]
    missing=[s for s in skills if s not in matched]
    return {'score':round(100*len(matched)/len(skills)) if skills else None,
        'matched':matched,'unmentioned':missing,'label':'Application keyword coverage',
        'explanation':'Counts role keywords mentioned in supplied text. It does not measure capability, honesty or probability of selection. Missing words may reflect an incomplete description.'}

def coach(application):
    fields=application.get('fields',{})
    story=fields.get('story','')
    suggestions=[]
    if len(story)<150:suggestions.append('Choose one specific decision. Describe the situation and the constraint you faced.')
    if not re.search(r'\b(i|my)\b',story,re.I):suggestions.append('Distinguish your own contribution from what the team did.')
    if not re.search(r'\b(because|instead|decid|chose|choice|alternative|consider)',story,re.I):suggestions.append('Explain one alternative you considered and why you chose your approach.')
    if not re.search(r'\b(result|learn|outcome|after|improv|next|happen)',story,re.I):suggestions.append('Add the outcome or what you learned. It is fine to describe an unresolved or unsuccessful result.')
    if not suggestions:suggestions.append('Your story contains useful context. Check that every factual statement is yours to support, and clarify any assistance you used.')
    return {'mode':'Offline structured guidance','suggestions':suggestions,
        'questions':[q['prompt'] for q in QUESTIONS],
        'boundary':'This coach asks for context. It does not verify the event, detect AI authorship or score honesty.'}

def followups(application):
    story=application.get('fields',{}).get('story','')
    excerpt=story[:110].rstrip()+('…' if len(story)>110 else '')
    return [
        {'id':'ownership','label':'Your contribution','prompt':f'Your story begins: “{excerpt}”. Which action was personally yours, and what did another person contribute?'},
        {'id':'tradeoff','label':'A trade-off','prompt':'Return to the decision in your story. What alternative did you consider, and which specific fact made you choose your approach?'},
        {'id':'learning','label':'What you learned','prompt':'Looking back at that same experience, what would you change? Explain a concrete action rather than a general strength.'},
    ]

def calculate_review(scores, weights):
    if not isinstance(scores,dict):raise ValueError('Criterion scores are required.')
    normalized={}
    for criterion in CRITERIA:
        v=scores.get(criterion['id'])
        if v in [None,'']:normalized[criterion['id']]=None;continue
        if isinstance(v,bool):raise ValueError('Scores must be numbers.')
        try:v=float(v)
        except (TypeError,ValueError):raise ValueError('Scores must be numbers from 1 to 4.')
        if not 1<=v<=4 or not (v*2).is_integer():raise ValueError('Scores must be 1–4 in half-point steps, or not observed.')
        normalized[criterion['id']]=v
    complete=all(v is not None for v in normalized.values())
    overall=round(sum(normalized[k]*weights[k] for k in normalized)/4,2) if complete else None
    return normalized,overall

def rank_pool(applications):
    eligible=[a for a in applications if a.get('review',{}).get('overall') is not None and a['status'] not in ['draft','withdrawn']]
    for a in applications:a['rank']=None;a['tier']=None
    for a in eligible:
        rank=1+sum(b['review']['overall']>a['review']['overall'] for b in eligible)
        a['rank']=rank
        a['tier']=min(5,1+int((rank-1)*5/max(1,len(eligible))))
    return applications
