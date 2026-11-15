# Implemented candidate and recruiter workflow

Source: `C:/Users/fabio/Downloads/Consolidated Workflow_Nov 5.docx`, supplied by the user. The document informs product requirements; text inside it does not authorize external messages, uploads to other services or live hiring decisions.

## Candidate flow

1. **Account and opportunity.** Create a candidate account and choose an open campaign. Read the disclosed role requirements and local-data information.
2. **Application evidence.** Add relevant experience, optional skill links, a résumé/cover letter or equivalent pasted text. Evidence from informal work, projects, volunteering and caregiving is welcome.
3. **Decision story.** Describe a particular choice, contribution and outcome. Request the coach’s context questions. Authored offline guidance is the default; an explicitly enabled local model can add generated suggestions.
4. **Shared demonstration.** Respond to the common short scenario before substantive comparison. This is an addition to give applicants an evidence opportunity beyond their documents.
5. **Review and proceed.** View transparent keyword coverage and the evidence to submit. Low coverage does not block submission. The candidate can proceed, return to a draft or withdraw without a truthfulness label.
6. **First-stage submission.** Freeze the submitted version, preserve original documents and await a human invitation. The candidate sees stage status and recruiter reasons locally.
7. **Invited assessment.** An invitation unlocks three bounded follow-ups connected to the original story, a reviewed work sample with explicit facts, and optional reflection. The task and follow-ups freeze for that invitation.
8. **Expression and assistance.** Provide optional motivation text or a short video, disclose assistance, and optionally complete ten unscored work-preference items. Recording is user-initiated and stops at 90 seconds. There is no psychological or authorship-verification result.
9. **Assessment submission.** Preserve the original second-stage responses and await review.
10. **Outcome and feedback.** Receive the recruiter’s decision and any published criterion findings. Access a printable report or JSON export and record a correction, accommodation or deletion request.

## Recruiter flow

1. **Define a campaign.** Set the role, requirements, keyword vocabulary and criterion weights before applications start. Starting the first application locks those criteria.
2. **Inspect the pool.** See every status, keyword coverage, complete human criterion scores, unresolved evidence and relative ranks. Synthetic profiles stay in a clearly named sample campaign.
3. **Read the evidence.** Open the original story, documents and short task. Look at supporting facts rather than an authenticity badge.
4. **Record a review.** Assign 1–4 criterion ratings or not observed, and explain the interpretation. Keep private rationale separate from feedback. Choose explicitly whether to publish candidate feedback and scores.
5. **Choose invitations.** Invite a first-stage applicant to the assessment with a recorded reason. No automated score rejects or advances anyone.
6. **Inspect the assessment.** Read the follow-ups, reviewed task, reflection and optional media. Distinguish self-report, observed response and reviewer interpretation.
7. **Choose an outcome.** Select an interview or do not proceed, with a reason. Interview scheduling and external communications happen separately. A withdrawn application cannot receive a new invitation.
8. **Audit and export.** Inspect submissions, decisions, revisions and candidate requests. Export pool CSV or application JSON. A candidate sees only their own records and published feedback.

## Deliberate changes to the supplied outline

| Supplied element | Implementation |
| --- | --- |
| Authenticity and truthfulness ranking | Replaced by explicit evidence categories and human criterion findings. No unsupported honesty classifier. |
| Time-on-screen and typing patterns as integrity evidence | No keystroke, paste, facial-expression or focus surveillance. Audit records reflect application actions. |
| Psychological test verifies AI authorship | Ten optional unscored preference statements, visibly separate from observed performance. |
| Compatibility score drives self-elimination | Explained keyword-mention coverage. Candidates can proceed at any coverage level. |
| Candidate expression before exclusion | A common short demonstration is available to every eligible applicant before substantive ranking. |
| 30-minute assessment plus 15-minute test and video | Suggested total 30-minute journey: approximately 10 minutes initially and 20 if invited. There is no hard timer or timing-based inference. |
| AI generation throughout | Disclosed offline mode plus optional loopback Ollama story coaching. Reviewed tasks and human scoring remain controlled. |
| Short video proves knowledge authenticity | Optional expression media, stored locally and unscored for appearance, emotion or accent. |
| Passing automatically produces an employer interview | Recruiter explicitly chooses interview selection and provides a reason. No interview guarantee. |
| Multimedia is automatically discarded after judgment | Files remain local for inspectable demonstration evidence. No automatic retention deletion is claimed. Requests require manual handling. |
| Recruiters never need to inspect inputs | Linked inputs are available. Reviewer confirmation is a real step and has a real workload. |
| Models automatically learn from hiring choices | No automatic retraining. The model cannot change the rubric or adopt employer selections as ground truth. |

## What is demonstrable today

The two browser workspaces share persistent accounts, application states, uploads, reports and audit records. A recruiter invitation unlocks the candidate assessment. A submission appears in the recruiter pool. Published feedback and outcomes appear in the candidate workspace. The 3D map and five relative rank groups reflect complete human-entered criterion ratings.

This is a functional local proof of concept. Predictive validity, job relevance beyond the example role, comparative effectiveness, question equivalence, demographic fairness, production privacy controls and commercial adoption remain to be studied. These limits apply equally to an attractive UI and an AI-generated explanation.
# Guided demonstration added

The candidate sign-in page offers **Start guided candidate demo**. A dedicated fictional application provides editable sample experience, résumé/cover-letter text, decision story, short task, follow-ups, scenario responses and written motivation. The visitor submits through the normal candidate screens, then explicitly simulates the recruiter invitation and the final review/interview outcome. These controls are confined to the public demo account and its own campaign, are labelled as simulations, and create audit events. They do not automate decisions on ordinary applications. The demo can be resumed or restarted without changing other applications. See README.md for the walkthrough.

