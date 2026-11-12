import json
from pathlib import Path
from celery import Celery
from src.config.database import SessionLocal
from src.config.settings import REDIS_URL,ARTIFACT_DIR
from src.models import SpectrumRun,TraverseGroupRun
from src.services.analysis import analyze
from src.services.group_analysis import analyze_group
from src.services.audit import record
app=Celery('weave_periodogram',broker=REDIS_URL,backend=REDIS_URL)
app.conf.update(task_track_started=True,worker_prefetch_multiplier=1,task_acks_late=True)
@app.task(name='weave.analyze',soft_time_limit=120,time_limit=150)
def analyze_run(id):
 with SessionLocal() as db:
  run=db.get(SpectrumRun,id)
  if not run or run.status=='completed':return
  run.status='running';db.commit()
  try:
   snapshot=run.source_snapshot;result=analyze(snapshot['study'],snapshot['points'],run.plan_snapshot)
   Path(ARTIFACT_DIR).mkdir(parents=True,exist_ok=True);Path(ARTIFACT_DIR,f'weave-{id}.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False));run.result=result;run.peak_frequency=result['best']['frequency'];run.max_power=result['observed_max_power'];run.global_p=result['global_test']['global_p'];run.status='completed';run.error=None;db.commit();record(db,'worker','run.completed',{'run_id':id,'global_p':run.global_p})
  except Exception as error:
   db.rollback();run=db.get(SpectrumRun,id);run.status='failed';run.error=str(error)[:1000];db.commit();record(db,'worker','run.failed',{'run_id':id,'error':run.error})
@app.task(name='weave.analyze_group',soft_time_limit=240,time_limit=300)
def analyze_group_run(id):
 with SessionLocal() as db:
  run=db.get(TraverseGroupRun,id)
  if not run or run.status=='completed':return
  run.status='running';db.commit()
  try:
   snapshot=run.source_snapshot;result=analyze_group(run.group_snapshot,snapshot['members'],run.group_fingerprint)
   Path(ARTIFACT_DIR).mkdir(parents=True,exist_ok=True);Path(ARTIFACT_DIR,f'weave-group-{id}.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False));run.result=result;winner=result['winning_member'];run.observed_max_power=result['observed_max_power'];run.global_p=result['global_test']['global_p'];run.winning_member_ordinal=winner['ordinal'];run.winning_study_id=winner['study_id'];run.winning_frequency=winner['frequency'];run.status='completed';run.error=None;db.commit();record(db,'worker','group.run.completed',{'group_run_id':id,'global_p':run.global_p})
  except Exception as error:
   db.rollback();run=db.get(TraverseGroupRun,id);run.status='failed';run.error=str(error)[:2000];db.commit();record(db,'worker','group.run.failed',{'group_run_id':id,'error':run.error})
