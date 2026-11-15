"""Local SQLite persistence. All mutable records share the same transaction store."""
import hashlib
import json
import os
from pathlib import Path
import random
import secrets
import sqlite3
from contextlib import contextmanager
import domain

ROOT=Path(__file__).resolve().parent

def password_hash(password,salt=None):
    salt=salt or secrets.token_hex(16)
    return salt+':'+hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),210000).hex()

def password_matches(password,stored):
    return secrets.compare_digest(password_hash(password,stored.split(':')[0]),stored)

class Store:
    def __init__(self,data_dir=None,seed_demo=True):
        self.directory=Path(data_dir or ROOT/'data').resolve()
        self.directory.mkdir(parents=True,exist_ok=True)
        self.uploads=self.directory/'uploads';self.uploads.mkdir(exist_ok=True)
        self.path=self.directory/'evidence-path.sqlite3'
        self.initialize(seed_demo)

    @contextmanager
    def connection(self):
        con=sqlite3.connect(self.path,timeout=15)
        con.row_factory=sqlite3.Row
        con.execute('PRAGMA foreign_keys=ON')
        try:yield con;con.commit()
        except Exception:con.rollback();raise
        finally:con.close()

    def initialize(self,seed_demo):
        with self.connection() as con:
            con.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,username TEXT UNIQUE NOT NULL,name TEXT NOT NULL,password TEXT NOT NULL,role TEXT NOT NULL,created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id),expires REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,title TEXT NOT NULL,demo INTEGER NOT NULL DEFAULT 0,config TEXT NOT NULL,created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS applications(id TEXT PRIMARY KEY,user_id TEXT REFERENCES users(id),job_id TEXT NOT NULL REFERENCES jobs(id),name TEXT NOT NULL,status TEXT NOT NULL,data TEXT NOT NULL,revision INTEGER NOT NULL DEFAULT 1,created TEXT NOT NULL,updated TEXT NOT NULL,UNIQUE(user_id,job_id));
            CREATE TABLE IF NOT EXISTS files(id TEXT PRIMARY KEY,application_id TEXT NOT NULL REFERENCES applications(id),kind TEXT NOT NULL,name TEXT NOT NULL,mime TEXT NOT NULL,path TEXT NOT NULL,size INTEGER NOT NULL,extracted TEXT NOT NULL DEFAULT '',created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,application_id TEXT,actor TEXT NOT NULL,kind TEXT NOT NULL,detail TEXT NOT NULL,created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            ''')
            if not con.execute("SELECT 1 FROM users WHERE role='recruiter'").fetchone():
                password=os.environ.get('EVIDENCE_PATH_ADMIN_PASSWORD') or secrets.token_urlsafe(16)
                con.execute('INSERT INTO users VALUES(?,?,?,?,?,?)',(secrets.token_hex(16),'recruiter','Local recruiter',password_hash(password),'recruiter',domain.now()))
                (self.directory/'.local-access.txt').write_text('Evidence Path local recruiter access\nUsername: recruiter\nPassword: '+password+'\n\nKeep this file private. The service listens on localhost only.\n',encoding='utf-8')
            if not con.execute('SELECT 1 FROM jobs').fetchone():
                role=dict(domain.DEFAULT_ROLE)
                con.execute('INSERT INTO jobs VALUES(?,?,?,?,?)',('operations',role['title'],0,json.dumps(role),domain.now()))
                if seed_demo:self.seed(con)
            con.execute("INSERT OR IGNORE INTO settings VALUES('ai',?)",(json.dumps({'enabled':False,'model':''}),))

    def seed(self,con):
        role=dict(domain.DEFAULT_ROLE);role['title']='Operations coordinator · sample campaign';role['organization']='Fictional employer';role['description']='A fictional pool for exploring the recruiter workspace. Every sample profile and score is synthetic.'
        con.execute('INSERT INTO jobs VALUES(?,?,?,?,?)',('demo-campaign',role['title'],1,json.dumps(role),domain.now()))
        demo_id=secrets.token_hex(16)
        con.execute('INSERT INTO users VALUES(?,?,?,?,?,?)',(demo_id,'demo.candidate','Demo applicant',password_hash('candidate-demo'),'candidate',domain.now()))
        rng=random.Random(20261105)
        stories=[
            'I helped coordinate a community food collection. When a driver cancelled, I checked the delivery windows, asked another volunteer about availability and proposed a revised route. I confirmed the change with the organizer before telling the team. We completed the collection, and I learned to agree a backup contact in advance.',
            'In my part-time shop role, I handled a customer request while a delivery arrived. I checked what could wait, asked my colleague to cover the desk and explained the change to the customer. I learned that a short, specific update helped the next person continue the work.',
            'While organizing a student project, I found conflicting figures in two files. I checked the original record before sharing the result and told the team which number remained uncertain. We corrected the final slide, and I learned to retain the source reference.'
        ]
        for i in range(100):
            sid=secrets.token_hex(16)
            fields={'experience':'Fictional community and part-time work experience. Coordination, planning and customer communication.','skills':'coordination, communication, planning','story':stories[i%3],
                'micro_task':'I would check the original record with the supervisor at 10:05. I would tell my colleague that the date is being verified and confirm the next update before 10:10.','assistance':'Sample content authored for the local demonstration.'}
            status=['submitted','invited','assessment_submitted','interview','not_proceeding'][i%5]
            scores={c['id']:rng.choice([1,1.5,2,2.5,3,3.5,4]) for c in domain.CRITERIA}
            _,overall=domain.calculate_review(scores,role['weights'])
            review={'scores':scores,'overall':overall,'rationale':'Synthetic reviewer example. Inspect the linked responses and apply your own criterion anchors.','feedback':'This is a fictional feedback example, not an actual candidate judgment.','published':True,'reviewer':'Demo reviewer','updated':domain.now()}
            assessment={'ownership':'I checked the source and asked the organizer to approve the change.','tradeoff':'I considered sending a provisional number, but decided to separate the confirmed facts from the unresolved ones.','learning':'I would agree the update time and backup contact earlier.',
                'plan':'I would check duplicate IDs against the booking log first. I would ask the operations lead to resolve uncertainty at 11:25 and agree a revised internal deadline. I would give the client a status update while verification continues.',
                'message':'I am checking two duplicate records before sharing the attendance count. Can we agree an update after 11:25? I will send the confirmed count or identify the remaining uncertainty.',
                'contingency':'If verification is incomplete, I would tell the client what is known and ask the operations lead for the next decision. I would not call the count verified.',
                'reflection':'I used the facts in the scenario to check my proposed plan.','preferences':{}}
            record={'fields':fields,'assessment':assessment if status not in ['submitted','invited'] else {},'review':review if i<80 else {},'notifications':[], 'demo':True,'task_version':domain.SCENARIO['version'],'snapshots':[]}
            con.execute('INSERT INTO applications VALUES(?,?,?,?,?,?,?,?,?)',(sid,None,'demo-campaign',f'Sample candidate {i+1:03}',status,json.dumps(record),1,domain.now(),domain.now()))

    @staticmethod
    def event(con,application_id,actor,kind,detail):
        con.execute('INSERT INTO events(application_id,actor,kind,detail,created) VALUES(?,?,?,?,?)',(application_id,actor,kind,json.dumps(detail),domain.now()))

    @staticmethod
    def job(row):
        return {'id':row['id'],'demo':bool(row['demo']),**json.loads(row['config'])}

    @staticmethod
    def application(con,row):
        if row is None:raise LookupError('Application not found.')
        a={'id':row['id'],'user_id':row['user_id'],'job_id':row['job_id'],'name':row['name'],'status':row['status'],'revision':row['revision'],'created':row['created'],'updated':row['updated'],**json.loads(row['data'])}
        a['files']=[{'id':f['id'],'kind':f['kind'],'name':f['name'],'mime':f['mime'],'size':f['size'],'extracted_text':f['extracted'],'created':f['created']} for f in con.execute('SELECT * FROM files WHERE application_id=? ORDER BY created,id',(a['id'],))]
        return a

    @staticmethod
    def save(con,a,expected_revision=None):
        fields={k:v for k,v in a.items() if k not in ['id','user_id','job_id','name','status','revision','created','updated','files','alignment','rank','tier','job_title']}
        revision=a['revision'] if expected_revision is None else expected_revision
        updated=domain.now()
        cur=con.execute('UPDATE applications SET name=?,status=?,data=?,revision=revision+1,updated=? WHERE id=? AND revision=?',(a['name'],a['status'],json.dumps(fields),updated,a['id'],revision))
        if cur.rowcount!=1:raise RuntimeError('This record changed in another window. Reload it before saving again.')
        a['revision']=revision+1;a['updated']=updated
