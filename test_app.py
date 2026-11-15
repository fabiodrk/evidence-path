import http.cookiejar
import io
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
from unittest.mock import patch
import app
import domain

class Client:
    def __init__(self,base):
        self.base=base;self.jar=http.cookiejar.CookieJar();self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
    def request(self,path,data=None,headers=None,raw=None):
        h={'X-Evidence-Path':'1'}
        if headers:h.update(headers)
        if data is not None:body=json.dumps(data).encode();h['Content-Type']='application/json'
        else:body=raw
        req=urllib.request.Request(self.base+path,data=body,headers=h)
        try:
            with self.opener.open(req,timeout=10) as r:
                value=r.read()
                return r.status,json.loads(value) if 'application/json' in r.headers.get('Content-Type','') else value
        except urllib.error.HTTPError as ex:return ex.code,json.loads(ex.read())

class AppTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        previous=os.environ.get('EVIDENCE_PATH_ADMIN_PASSWORD');os.environ['EVIDENCE_PATH_ADMIN_PASSWORD']='test-admin-password'
        self.server=app.make_server(0,self.tmp.name,True)
        if previous is None:os.environ.pop('EVIDENCE_PATH_ADMIN_PASSWORD')
        else:os.environ['EVIDENCE_PATH_ADMIN_PASSWORD']=previous
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base=f'http://127.0.0.1:{self.server.server_port}'
        self.candidate=Client(self.base);self.recruiter=Client(self.base)
        self.assertEqual(self.recruiter.request('/api/login',{'username':'recruiter','password':'test-admin-password'})[0],200)
        self.assertEqual(self.candidate.request('/api/register',{'username':'tester','name':'Test Candidate','password':'candidate-password'})[0],200)
        _,r=self.candidate.request('/api/candidate/start',{'job_id':'operations'});self.a=r['application']
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
    def save_first_stage(self):
        fields={'experience':'I coordinated a volunteer team and checked information for community events.',
            'skills':'coordination, communication','story':'I helped organize a volunteer collection. When a driver cancelled, I checked the schedule and decided to ask the organizer for approval because a revised route could affect another person. Afterward, I learned to agree a backup contact.',
            'micro_task':'I would check the two dates with the supervisor at 10:05 and tell my colleague when I will send the verified answer.','assistance':'I used the facts provided in the local demonstration.'}
        status,r=self.candidate.request('/api/candidate/save',{'id':self.a['id'],'revision':self.a['revision'],'fields':fields,'consent':True})
        self.assertEqual(status,200,r);self.a=r['application']
    def submit_first(self):
        self.save_first_stage();status,r=self.candidate.request('/api/candidate/submit',{'id':self.a['id']});self.assertEqual(status,200,r);self.a=r['application']

    def test_guided_demo_journey_and_isolation(self):
        self.assertEqual(self.candidate.request('/api/candidate/demo',{'action':'start'})[0],403)
        demo_client=Client(self.base)
        demo_client.request('/api/login',{'username':'demo.candidate','password':'candidate-demo'})
        status,r=demo_client.request('/api/candidate/demo',{'action':'start'})
        self.assertEqual(status,200,r);a=r['application'];self.assertTrue(a['guided_demo'])
        self.assertEqual(demo_client.request('/api/candidate/demo',{'action':'advance'})[0],400)
        for step in range(3):
            status,r=demo_client.request('/api/candidate/demo',{'action':'fill','step':step,'revision':a['revision']})
            self.assertEqual(status,200,r);a=r['application']
        self.assertEqual(demo_client.request('/api/candidate/demo',{'action':'fill','step':0,'revision':1})[0],409)
        self.assertEqual(demo_client.request('/api/candidate/submit',{'id':a['id']})[0],200)
        status,r=demo_client.request('/api/candidate/demo',{'action':'advance'});self.assertEqual(status,200,r)
        a=r['application'];self.assertEqual(a['status'],'invited')
        for step in range(3):
            status,r=demo_client.request('/api/candidate/demo',{'action':'fill','step':step,'revision':a['revision']})
            self.assertEqual(status,200,r);a=r['application']
        self.assertEqual(demo_client.request('/api/candidate/assessment-submit',{'id':a['id']})[0],200)
        status,r=demo_client.request('/api/candidate/demo',{'action':'advance'});self.assertEqual(status,200,r)
        self.assertEqual(r['application']['status'],'interview')
        self.assertIn('SIMULATED',r['application']['review']['feedback'])
        with self.server.store.connection() as con:
            stored=con.execute('SELECT data FROM applications WHERE id=?',(a['id'],)).fetchone()
            self.assertEqual(len(json.loads(stored['data'])['snapshots']),2)
        _,normal=self.candidate.request('/api/application/'+self.a['id']);self.assertEqual(normal['application']['status'],'draft')
        _,r=demo_client.request('/api/candidate/demo',{'action':'restart'})
        self.assertEqual(r['application']['fields'],{});self.assertEqual(r['application']['status'],'draft')
        _,resumed=demo_client.request('/api/candidate/demo',{'action':'start'});self.assertEqual(resumed['application']['id'],a['id'])

    def test_full_integrated_journey_and_persistence(self):
        self.submit_first()
        self.assertEqual(self.a['status'],'submitted')
        status,r=self.recruiter.request('/api/recruiter');self.assertEqual(status,200)
        self.assertTrue(any(a['id']==self.a['id'] for a in r['applications']))
        _,r=self.recruiter.request('/api/recruiter/action',{'id':self.a['id'],'action':'invite','reason':'The submitted work supports a closer review.'})
        self.assertEqual(r['application']['status'],'invited')
        _,r=self.candidate.request('/api/application/'+self.a['id']);self.a=r['application']
        self.assertIn('Your story begins',self.a['questions'][0]['prompt'])
        answers={k:'I would check the source record first and explain the trade-off before agreeing the next action with the responsible colleague.' for k in ['ownership','tradeoff','learning','plan','message','contingency']}
        answers['preferences']={'0':4,'1':3}
        _,r=self.candidate.request('/api/candidate/assessment-save',{'id':self.a['id'],'revision':self.a['revision'],'assessment':answers});self.a=r['application']
        status,r=self.candidate.request('/api/candidate/assessment-submit',{'id':self.a['id']});self.assertEqual(status,200,r)
        status,r=self.recruiter.request('/api/recruiter/review',{'id':self.a['id'],'scores':{'reasoning':3,'communication':4,'prioritization':3,'verification':4},'rationale':'The response checks the source before promising a result.','feedback':'You checked the source and explained the next agreed step.','published':True})
        self.assertEqual(status,200,r);self.assertEqual(r['application']['review']['overall'],87.5)
        _,r=self.candidate.request('/api/application/'+self.a['id']);self.assertTrue(r['application']['review']['published']);self.assertNotIn('rationale',r['application']['review'])
        status,r=self.recruiter.request('/api/recruiter/action',{'id':self.a['id'],'action':'interview','reason':'We would like to discuss the submitted work.'});self.assertEqual(status,200,r)
        _,r=self.candidate.request('/api/candidate');self.assertEqual(r['applications'][0]['status'],'interview')
        _,r=self.candidate.request('/api/report?id='+self.a['id']);self.assertIn(b'Test Candidate',r)
        _,export=self.candidate.request('/api/export.json');self.assertEqual(export['applications'][0]['status'],'interview')
        with self.server.store.connection() as con:
            saved=con.execute('SELECT status,data FROM applications WHERE id=?',(self.a['id'],)).fetchone()
            self.assertEqual(saved['status'],'interview');self.assertEqual(len(json.loads(saved['data'])['snapshots']),2)

    def test_cross_account_and_cross_role_guards(self):
        other=Client(self.base);other.request('/api/register',{'username':'other','name':'Other Candidate','password':'another-password'})
        self.assertEqual(other.request('/api/application/'+self.a['id'])[0],403)
        self.assertIn(self.candidate.request('/api/recruiter')[0],[401,403])
        self.assertIn(self.candidate.request('/api/recruiter/action',{'id':self.a['id'],'action':'invite','reason':'Forbidden role action attempt.'})[0],[401,403])
        self.assertEqual(other.request('/api/candidate/save',{'id':self.a['id'],'revision':1,'fields':{}})[0],403)
        self.assertEqual(self.candidate.request('/api/candidate',headers={'Origin':'https://example.com'})[0],403)

    def test_validation_freeze_and_revision(self):
        self.assertEqual(self.candidate.request('/api/candidate/submit',{'id':self.a['id']})[0],400)
        self.save_first_stage()
        self.assertEqual(self.candidate.request('/api/candidate/save',{'id':self.a['id'],'revision':1,'fields':{'story':'stale edit'}})[0],409)
        self.candidate.request('/api/candidate/submit',{'id':self.a['id']})
        self.assertEqual(self.candidate.request('/api/candidate/save',{'id':self.a['id'],'revision':self.a['revision'],'fields':{'story':'edited'}})[0],400)
        self.assertEqual(self.candidate.request('/api/candidate/assessment-save',{'id':self.a['id'],'revision':self.a['revision'],'assessment':{'plan':'Not invited'}})[0],400)
        self.assertEqual(self.candidate.request('/api/candidate/submit',{'id':self.a['id']})[0],400)

    def test_attachments_ownership_extraction_and_report_escaping(self):
        xml=b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Communication and planning experience.</w:t></w:r></w:p></w:body></w:document>'
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:z.writestr('word/document.xml',xml)
        status,r=self.candidate.request('/api/upload',headers={'X-Application-Id':self.a['id'],'X-File-Kind':'resume','X-File-Name':'sample.docx','Content-Type':'application/octet-stream'},raw=buf.getvalue())
        self.assertEqual(status,200,r)
        fid=r['application']['files'][0]['id'];self.a=r['application']
        self.assertEqual(self.candidate.request('/api/files/'+fid)[0],200)
        other=Client(self.base);other.request('/api/register',{'username':'stranger','name':'Stranger','password':'another-password'})
        self.assertEqual(other.request('/api/files/'+fid)[0],403)
        with self.server.store.connection() as con:self.assertIn('planning',con.execute('SELECT extracted FROM files WHERE id=?',(fid,)).fetchone()[0])
        self.assertEqual(self.candidate.request('/api/upload',headers={'X-Application-Id':self.a['id'],'X-File-Kind':'resume','X-File-Name':'bad.html'},raw=b'<script>bad</script>')[0],400)
        fields={'experience':'<script>alert(1)</script> with adequate context for this test.','story':'<img src=x onerror=alert(1)> '+'A specific decision and consequence. '*4,'micro_task':'I would check the source and communicate the verified next step.'}
        self.candidate.request('/api/candidate/save',{'id':self.a['id'],'revision':self.a['revision'],'fields':fields,'consent':True})
        _,report=self.candidate.request('/api/report?id='+self.a['id']);self.assertNotIn(b'<script>alert',report);self.assertIn(b'&lt;script&gt;',report)

    def test_ranking_missing_evidence_and_campaign_lock(self):
        scores,overall=domain.calculate_review({'reasoning':4,'communication':3,'prioritization':2,'verification':None},domain.DEFAULT_ROLE['weights'])
        self.assertIsNone(overall)
        rows=[{'id':str(i),'status':'submitted','review':{'overall':v}} for i,v in enumerate([90,90,75,None])]
        domain.rank_pool(rows);self.assertEqual([a['rank'] for a in rows],[1,1,3,None])
        for bad in [float('nan'),0,5,2.2,True]:
            with self.assertRaises(ValueError):domain.calculate_review({c['id']:bad for c in domain.CRITERIA},domain.DEFAULT_ROLE['weights'])
        self.assertEqual(self.recruiter.request('/api/recruiter/job',{'id':'operations',**domain.DEFAULT_ROLE})[0],400)
        status,r=self.recruiter.request('/api/recruiter/job',{**domain.DEFAULT_ROLE,'title':'New campaign','organization':'Test employer'})
        self.assertEqual(status,200,r)
        _,bootstrap=self.candidate.request('/api/bootstrap');self.assertTrue(any(j['id']==r['job']['id'] for j in bootstrap['jobs']))

    def test_offline_coach_unpublished_review_and_requests(self):
        self.save_first_stage();status,r=self.candidate.request('/api/candidate/coach',{'id':self.a['id']});self.assertEqual(status,200);self.assertEqual(r['mode'],'Offline structured guidance')
        self.candidate.request('/api/candidate/submit',{'id':self.a['id']})
        self.recruiter.request('/api/recruiter/review',{'id':self.a['id'],'scores':{c['id']:3 for c in domain.CRITERIA},'rationale':'Private rationale with a specific evidence reference.','feedback':'Draft feedback must remain private.','published':False})
        _,r=self.candidate.request('/api/application/'+self.a['id']);self.assertEqual(r['application']['review'],{})
        status,r=self.candidate.request('/api/candidate/correction',{'id':self.a['id'],'message':'Please correct the date in my example.'});self.assertEqual(status,200,r)
        _,audit=self.recruiter.request('/api/recruiter/audit');self.assertTrue(any(e['kind']=='candidate_request' for e in audit['events']))
        status,_=self.candidate.request('/api/candidate/withdraw',{'id':self.a['id']});self.assertEqual(status,200)
        self.assertEqual(self.recruiter.request('/api/recruiter/action',{'id':self.a['id'],'action':'invite','reason':'This should not change a withdrawal.'})[0],400)

    def test_two_roles_in_the_same_browser_cookie_jar(self):
        status,_=self.candidate.request('/api/login',{'username':'recruiter','password':'test-admin-password'})
        self.assertEqual(status,200)
        _,r=self.candidate.request('/api/bootstrap',headers={'X-Workspace':'candidate'})
        self.assertEqual(r['user']['role'],'candidate')
        _,r=self.candidate.request('/api/bootstrap',headers={'X-Workspace':'recruiter'})
        self.assertEqual(r['user']['role'],'recruiter')
        self.assertEqual(self.candidate.request('/api/recruiter',headers={'X-Workspace':'recruiter'})[0],200)
        self.assertEqual(self.candidate.request('/api/logout',{},headers={'X-Workspace':'candidate'})[0],200)
        self.assertEqual(self.candidate.request('/api/recruiter',headers={'X-Workspace':'recruiter'})[0],200)
        self.assertEqual(self.candidate.request('/api/candidate',headers={'X-Workspace':'candidate'})[0],401)

    def test_shutdown_requires_recruiter_and_confirmation(self):
        self.assertIn(self.candidate.request('/api/recruiter/shutdown',{'confirmation':'STOP'})[0],[401,403])
        self.assertEqual(self.recruiter.request('/api/recruiter/shutdown',{'confirmation':'missing'})[0],400)
        self.assertEqual(self.recruiter.request('/api/recruiter/shutdown',{'confirmation':'STOP'})[0],200)

    def test_optional_local_model_and_offline_fallback(self):
        self.save_first_stage()
        self.recruiter.request('/api/recruiter/ai',{'enabled':True,'model':'test-local-model'})
        with patch('app.urllib.request.urlopen') as model:
            model.return_value.__enter__.return_value.read.return_value=json.dumps({'response':'Which specific action was yours, and what did you verify?'}).encode()
            status,r=self.candidate.request('/api/candidate/coach',{'id':self.a['id']})
            self.assertEqual(status,200,r);self.assertEqual(r['mode'],'Local model with structured guidance')
            self.assertIn('Which specific action',r['local_ai'])
            request=model.call_args.args[0]
            self.assertEqual(request.full_url,'http://127.0.0.1:11434/api/generate')
            self.assertFalse(json.loads(request.data)['stream'])
        with patch('app.urllib.request.urlopen',side_effect=OSError('Local service unavailable')):
            _,r=self.candidate.request('/api/candidate/coach',{'id':self.a['id']})
            self.assertEqual(r['mode'],'Offline structured guidance');self.assertIn('did not respond',r['notice'])
        _,r=self.candidate.request('/api/application/'+self.a['id']);self.assertEqual(r['application']['review'],{})

if __name__=='__main__':unittest.main(verbosity=2)
