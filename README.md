# Evidence Path local application

An integrated candidate workspace and recruiter workspace, inspired by the runnable HRPG pilot and based on **Consolidated Workflow_Nov 5.docx**. Both workspaces share one local SQLite database. The original HRPG application is unchanged.

## Start

Double-click **Start_Evidence_Path.bat**. Install Python 3.10 or newer first. The launcher uses the Windows Python launcher or Python on PATH. No dependency installation, cloud account, API key or internet connection is required for the default application.

- Candidate: **http://127.0.0.1:8780/candidate**
- Recruiter: **http://127.0.0.1:8780/recruiter**

The launcher reopens an existing instance. If that port is occupied by a different application, it chooses the next available port through 8789 and prints the address. Keep its terminal running. Ctrl+C stops a terminal-launched instance.

To stop an instance running in the background, sign in as recruiter and use **Local AI & access → Stop local server**. Type `STOP` in its confirmation. The launcher starts it again with the same saved records.

The recruiter username is **recruiter**. The generated password is in **data/.local-access.txt** after the first launch. Keep this file private. Candidates create their own accounts. **Try a sample candidate** opens the separate demonstration account. Its public demonstration password is `candidate-demo` and its username is `demo.candidate`; do not use it for private work.

Candidate and recruiter cookies are separate. You can keep both workspaces signed in in two tabs of the same browser. Each workspace authorizes its own requests. One candidate account per browser session is supported; use another browser profile to simulate two different candidates simultaneously.

Command-line alternative:

```powershell
python app.py --port 8780
```

For a fresh workspace without synthetic records:

```powershell
python app.py --port 8781 --data-dir clean-data --no-demo
```

Do not run multiple server processes against the same data folder. To open an existing process, use the launcher.

## Guided candidate demonstration

On the candidate sign-in page, choose **Start guided candidate demo**. No registration or recruiter password is needed. It opens the fictional Alex Morgan application in a separate demonstration campaign.

1. Choose **Use sample answers for this step**, read or edit the answers, and choose **Save & continue**. The first step includes résumé and cover-letter text, so no upload is required. Repeat for the story and short demonstration. You can also try the story coach.
2. Review and **Submit application**, then choose **Simulate recruiter invitation**.
3. Explore the three follow-ups, practical work sample and optional reflection. Load the editable sample answers on each step. Written motivation demonstrates the alternative to recording a video; camera access is unnecessary.
4. Review and **Submit assessment**, then choose **Simulate review & interview outcome** to see illustrative ratings, published feedback, the outcome and a printable report.
5. Choose **Restart guided demo** and type `RESTART` to reset the fictional answers and outcome. Existing attachments and the audit trail remain. Other applications are preserved. Leaving and reopening the demo resumes its saved state.

The demo usually takes about three minutes. All sample answers, reviewer ratings and recruiter responses are authored fiction, clearly marked as simulations. Only the public `demo.candidate` account and its dedicated guided-demo record support these controls. Normal applications still require recruiter decisions. The recruiter can inspect the guided-demo campaign to see the shared record. Independent copies of the app have independent data.

## Candidate experience

1. Create an account and select the open operations-coordination opportunity or a campaign the recruiter creates.
2. Describe relevant experience and optionally link skills or upload a résumé and existing cover letter. PDF, DOCX and TXT are supported up to 10 MB. Pasted text is an accessible alternative. PDF extraction uses `pypdf` when it is already available; the original attachment remains reviewable if extraction fails.
3. Explain one specific decision. The story coach requests context and personal contribution. Offline mode uses disclosed authored guidance. Optional local AI mode can add generated clarification questions.
4. Complete a common short demonstration. Review the evidence and acknowledge the local assessment information before submitting. Drafts save automatically and can be resumed after a refresh.
5. Read the recruiter’s invitation or outcome in the same workspace. No external email is sent.
6. If invited, answer three follow-up questions connected to your original story, complete the work sample, and optionally add reflection, declared assistance, unscored work-preference self-report and motivation text or video.
7. Upload an optional MP4/WEBM/MOV video up to 50 MB, or record locally with browser camera and microphone permission. Recording stops after 90 seconds. No media is uploaded to a cloud service.
8. Submit the assessment, inspect published feedback, open a printable evidence report, or record a correction/accommodation/deletion request for the recruiter.

Target burden is 10 minutes for the first stage and about 20 more minutes if invited. These are suggested timings, not a countdown or a validated time limit. This consolidates the original workflow’s separate 30-minute assessment and 15-minute test. Accommodations and actual task burden need study.

## Recruiter experience

- Overview with pipeline counts, an interactive 3D reviewed-evidence map, and five relative rank groups.
- A separate **100-candidate synthetic campaign** for exploration. Eighty profiles have synthetic complete reviewer ratings; twenty remain unranked. They are fictional and clearly marked. New submissions use a separate campaign.
- Search, status filtering, score/name/date sorting, CSV export and evidence JSON export.
- A linked application review with original documents, decision story, short demonstration, second-stage answers, optional video and an activity trail.
- Human-entered criterion ratings, supporting rationale, candidate feedback and an explicit publication control.
- Human invitation, interview-selection and not-proceeding actions with a recorded reason. A withdrawal blocks further invitations. No score automatically rejects a candidate.
- New campaigns with approved descriptions, requirements, keywords and criterion weights. Weights total 100%. A campaign’s criteria freeze when the first application starts; create another campaign for changed criteria.
- Local AI configuration and a reviewable activity/request log.

New submissions and recruiter updates appear on refresh. Overview and waiting-candidate screens also check for updates every 12 seconds. Active drafts and reviewer forms are not silently replaced by polling.

## Scoring and evidence boundaries

**Application keyword coverage** is a transparent count of role words mentioned in supplied application text. It is not a compatibility prediction, measure of capability or reason to withdraw. The candidate may proceed at any coverage level.

**Criterion scores** are reviewer-entered values from 1 to 4 in half-point steps, or **not observed**. The four criteria are reasoning, communication, prioritization and information checking. The initial campaign weights each at 25%. Overall display score = sum of criterion score × weight / 4, giving a 0–100 scale. An overall score requires all four observations. Missing evidence is not a zero.

The 3D map displays reasoning, communication and prioritization, each converted to 0–100. Color groups reflect the overall four-criterion score. Rank is one plus the number of higher-scoring candidates in the same campaign. Tied scores share a rank and group. Group = min(5, 1 + floor((rank - 1) × 5 / reviewed count)). Ties can make group sizes unequal or leave a group empty. The map is a human-review summary, not a hiring recommendation.

The prototype does not label candidates honest, authentic or deceptive. It does not track keystrokes, detect AI authorship, diagnose psychology, score emotions, or infer capability from appearance or accent. The ten optional reflection statements are unscored self-description. A video supplies expression, not verification of historical claims. Assistance is permitted when disclosed.

## Optional local generative AI

The default app works without a model. It does not pretend authored responses come from AI.

If **Ollama is already installed and serving a downloaded model** at `http://127.0.0.1:11434`, open **Recruiter → Local AI & access**, select an installed model, and enable it. The application does not install Ollama or download model weights. It uses the local `/api/tags` endpoint to list models and `/api/generate` with `stream: false` to request story clarification. A timeout returns the offline guidance.

Only the candidate’s story and experience needed for the request go to the configured loopback service. Model output has no tool access and cannot change scores, submissions, the rubric or recruiter actions. Generated questions remain suggestions. The assessment bank and criterion scoring remain controlled; broad generative interviewing and automated semantic assessment are not implemented.

API references:

- https://docs.ollama.com/api/tags
- https://docs.ollama.com/api/generate

## Persistence and local privacy

`data/` contains the SQLite database, original attachments and recruiter-access file. Records survive refreshes, sign-outs and server restarts. Submissions retain frozen snapshots; later corrections append an activity record. Browser session tokens are random, hashed in the database, and kept in HttpOnly, SameSite=Strict role-specific cookies. Passwords use salted PBKDF2. Access checks apply to applications, files, reports and exports. The server binds only to `127.0.0.1`, rejects foreign Host/Origin values and uses a custom header for mutations.

This is a **local prototype**, not a hardened production hiring system. Candidate evidence and files are not encrypted at rest. All recruiter accounts on this machine can inspect the campaigns. There is no automatic retention deletion, production identity verification, regulatory certification, assessment validation or anti-fraud guarantee. Requests for corrections, accommodations or deletion are recorded for manual handling. Reports disclose their interpretation limits. Do not use the synthetic scores as validation data.

CSV exports neutralize formula-like user values. HTML reports escape submitted text. Uploaded files receive generated storage names, and authorization is checked before retrieval. Original document filenames are preserved for display without executing their contents.

## A five-minute demonstration

1. Sign in as recruiter and explore the synthetic campaign’s dashboard, pool, map and reports.
2. In another tab, create a candidate account and submit a short application to **Service & operations coordinator**.
3. Return to the recruiter tab, select that campaign and refresh. Open the new candidate, save ratings and invite them to the assessment with a reason.
4. Return to the candidate tab and choose **My applications**. Open the invitation, complete the questions and work sample, then submit.
5. Return to the recruiter tab, refresh, inspect the assessment and publish feedback. Select an interview with a reason. The candidate sees that outcome and the published feedback.

Notifications stay in the app. No external messages or interview bookings are sent.

## Tests

```powershell
python -m unittest -v
```

The tests use isolated temporary databases and cover the complete two-role journey, cross-account and cross-role authorization, role-specific browser sessions, upload extraction, attachment access, report escaping, frozen submissions, stale revisions, incomplete evidence, ranking ties, campaign locking, unpublished feedback, requests and withdrawals.

The original development environment also used a machine-specific browser check. That helper is not included in this portable repository. The application has no Node.js or Playwright dependency.

## Files

- `app.py`: localhost service, authorization, uploads, reports and API.
- `store.py`: SQLite schema, password hashing, persistence and synthetic pool.
- `domain.py`: reviewed scenario, follow-ups, offline coach and transparent calculations.
- `static/`: candidate and recruiter browser interfaces.
- `launch.py` and `Start_Evidence_Path.bat`: local startup and instance reuse.
- `WORKFLOW.md`: implemented flow and changes from the supplied outline.
- `test_app.py`: portable integration verification.

No source file or data in `hrpg_pilot/` is changed by this application.


## Portfolio publication

See [PORTFOLIO.md](PORTFOLIO.md) for project context and publication scope.
