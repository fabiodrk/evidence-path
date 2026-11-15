"""Fictional, explicitly simulated candidate journey. No hiring automation."""
import domain

FIELDS = {
    'experience': 'I am Alex Morgan, a fictional student applicant. I coordinated a campus food collection with six volunteers, balanced my classes with a part-time service role, and checked collection records before updating the organizer.',
    'skills': 'coordination, communication, prioritization, verification',
    'resume_text': 'Alex Morgan — fictional demonstration résumé\nStudent volunteer coordinator: planned collection routes, confirmed availability and reconciled collection records.\nPart-time service assistant: answered customer questions and communicated changes to colleagues.',
    'cover_text': 'I am interested in the coordinator role because I enjoy organizing practical work and helping people get reliable information. My volunteer collection experience taught me to check dependencies before promising a delivery time.',
    'story': 'During our campus food collection, a volunteer driver cancelled on the morning of a delivery. I checked the collection windows and asked another volunteer about availability. I considered moving the entire route, but that would have delayed two other stops. I proposed moving only the affected stop and asked the organizer to approve the change before contacting the receiving team. The revised collection was completed that afternoon. I learned to confirm a backup driver in advance; I did not make the final approval decision myself.',
    'micro_task': 'I would check the original delivery record with the supervisor at 10:05 rather than guess which date is correct. I would tell my colleague that the dates conflict and agree to send a verified update before 10:10. If verification is delayed, I would explain that uncertainty before the promised update time.',
    'assistance': 'All names and answers are fictional examples supplied by the guided demo. They are not evidence about a real candidate.'
}
ANSWERS = {
    'ownership': 'I checked the collection windows, contacted the available volunteer and proposed the revised stop. The organizer approved it; the replacement driver carried out the delivery. I distinguish my coordination from their decisions and work.',
    'tradeoff': 'Moving the whole route would have been simpler for us but would have delayed two receiving teams. I chose to propose changing just one stop, accepting extra coordination to protect the other commitments.',
    'learning': 'The collection finished that afternoon, but this is only my account, not independent verification. Next time I would confirm a backup driver and record an agreed escalation contact before the event.',
    'plan': 'At 11:20 I would inspect the registration IDs and the original booking log to find the two repeated IDs. I would not assume there are 40 unique people until that check is complete. I would ask the operations lead to resolve any remaining discrepancy at 11:25. In parallel I would ask my colleague to agree a revised internal deadline and send a qualified status update at 11:30, aiming for a verified client update by 11:40.',
    'message': 'The sheet shows 42 registrations, but two rows repeat an ID. I am checking the booking log and will consult the lead at 11:25 if needed. Can we move the internal figures deadline to 11:35? I can send a clearly qualified status update at 11:30, then confirm the verified count for the client by 11:40 if resolved.',
    'contingency': 'If the lead cannot resolve the discrepancy, I would tell both recipients what remains uncertain before their deadlines, explain the source checks already completed, and agree the next update time. I would not change the booking log or present an unverified count as final.',
    'reflection': 'I would check that the revised internal deadline was explicitly accepted and that the source record supports the final count. My proposed timing depends on access to the log and the lead.',
    'motivation': 'I enjoy turning unclear information into a practical next step and keeping colleagues informed. I would like to develop this skill in a coordination role. This text demonstrates the alternative to an optional video.',
    'assistance': 'These are editable, authored demonstration answers, not a real assessment submission or AI evaluation.'
}

def fill(a, step):
    if a['status']=='draft':
        keys = [('experience','skills','resume_text','cover_text'),('story','assistance'),('micro_task',),()][step]
        for key in keys: a['fields'][key]=FIELDS[key]
        if step==0: a['consent']=True
    elif a['status']=='invited':
        keys = [('ownership','tradeoff','learning'),('plan','message','contingency'),('reflection','motivation','assistance'),()][step]
        for key in keys: a['assessment'][key]=ANSWERS[key]
    else: raise ValueError('Sample answers are available only in an open demo step.')

def advance(a):
    if a['status']=='submitted':
        a['status']='invited';a['questions']=domain.followups(a);a['scenario']=domain.SCENARIO
        text='SIMULATED recruiter invitation: explore the follow-up questions and work sample. In a normal application, a recruiter must invite you.'
    elif a['status']=='assessment_submitted':
        scores={'reasoning':3.5,'communication':3,'prioritization':3.5,'verification':4}
        _,overall=domain.calculate_review(scores, {c['id']:25 for c in domain.CRITERIA})
        a['review']={'scores':scores,'overall':overall,'rationale':'SIMULATED review: sample answers identify source checks, deadlines and the need for agreement. Authored example, not AI scoring.','feedback':'SIMULATED feedback: you separated uncertain figures from verified facts and proposed source checks. Make the colleague’s acceptance of a revised deadline explicit, and confirm who owns the next update. These illustrative ratings are not validated findings.','published':True,'reviewer':'Demo simulation','updated':domain.now()}
        a['status']='interview'
        text='SIMULATED outcome: selected for interview. This completes the walkthrough; no interview is booked and no external message is sent.'
    else: raise ValueError('Submit the current stage before simulating its recruiter response.')
    a['notifications'].append({'date':domain.now(),'text':text,'reason':'Explicit guided demonstration; not a real recruiter decision.'})
