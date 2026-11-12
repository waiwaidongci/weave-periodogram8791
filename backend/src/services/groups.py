from sqlalchemy import select
from fastapi import HTTPException
from src.models import TraverseGroup,TraverseGroupMember,TraverseGroupRun
from src.utils.serialize import row
from .source import source_snapshot
from .fingerprint import group_fingerprint
from .audit import record

def member_source(db,study_id,plan_id,ordinal,label):
 try:current=source_snapshot(db,study_id,plan_id)
 except HTTPException as error:raise HTTPException(error.status_code,f'第{ordinal}位：{error.detail}') from error
 return {'ordinal':ordinal,'label':label or current['study']['name'],'study':current['study'],'points':current['points'],'plan':current['plan'],'source_fingerprint':current['source_fingerprint']}

def group_snapshot(db,group):
 members=[]
 for member in sorted(group.members,key=lambda m:m.ordinal):
  current=member_source(db,member.study_id,member.plan_id,member.ordinal,member.label)
  if current['source_fingerprint']!=member.source_fingerprint:raise HTTPException(409,f'第{member.ordinal}位“{member.label}”的源数据或频率计划已更新，登记已失效；请重算并另存为新的测线组')
  members.append(current)
 if len({m['study']['id'] for m in members})!=len(members):raise HTTPException(422,'同一测线不能重复登记为组内成员')
 return {'group':{'id':group.id,'name':group.name,'protocol':group.protocol,'permutations':group.permutations,'seed':group.seed},'members':members}

def member_state(db,member):
 try:
  current=member_source(db,member.study_id,member.plan_id,member.ordinal,member.label)
  fresh=current['source_fingerprint']==member.source_fingerprint
  return current,fresh,None if fresh else '源数据或频率计划自登记后已更新，旧组登记失效'
 except HTTPException as error:
  reason=str(error.detail)
  prefix=f'第{member.ordinal}位：'
  return None,False,reason[len(prefix):] if reason.startswith(prefix) else reason

def group_view(db,group):
 members=[];reasons=[]
 for member in sorted(group.members,key=lambda m:m.ordinal):
  current,fresh,reason=member_state(db,member)
  members.append({'id':member.id,'ordinal':member.ordinal,'label':member.label,'study_id':member.study_id,'plan_id':member.plan_id,'study_name':member.study_snapshot.get('name'),'plan_name':member.plan_snapshot.get('name'),'source_fingerprint':member.source_fingerprint,'stale':not fresh,'invalid_reason':reason})
  if not fresh:reasons.append(reason)
 return {**row(group),'members':members,'stale':bool(reasons),'invalid_reasons':reasons}


def create_group(db,data,actor):
 if db.scalar(select(TraverseGroup).where(TraverseGroup.name==data.name)):raise HTTPException(409,'测线组名已存在')
 members=[member_source(db,member.study_id,member.plan_id,member.ordinal,member.label) for member in data.members]
 if len({m['study']['id'] for m in members})!=len(members):raise HTTPException(422,'同一测线不能重复登记为组内成员')
 group=TraverseGroup(name=data.name,protocol=data.protocol,permutations=data.permutations,seed=data.seed,created_by=actor);db.add(group);db.flush()
 for current in members:db.add(TraverseGroupMember(group_id=group.id,study_id=current['study']['id'],plan_id=current['plan']['id'],ordinal=current['ordinal'],label=current['label'],study_snapshot=current['study'],plan_snapshot=current['plan'],source_fingerprint=current['source_fingerprint']))
 db.commit();record(db,actor,'group.registered',{'group_id':group.id,'members':len(members)});return {'group':row(group),'members':[{k:current[k] for k in ('ordinal','label','study','plan','source_fingerprint')} for current in members]}

def create_group_run(db,data,actor):
 group=db.get(TraverseGroup,data.group_id)
 if not group:raise HTTPException(404,'测线组不存在')
 if db.scalar(select(TraverseGroupRun).where(TraverseGroupRun.name==data.name)):raise HTTPException(409,'组运行名已存在')
 snapshot=group_snapshot(db,group);fingerprint_value=group_fingerprint(group,snapshot['members'])
 run=TraverseGroupRun(group_id=group.id,name=data.name,group_snapshot=snapshot['group'],source_snapshot={'members':snapshot['members']},source_fingerprints=[{'ordinal':m['ordinal'],'study_id':m['study']['id'],'source_fingerprint':m['source_fingerprint']} for m in snapshot['members']],group_fingerprint=fingerprint_value,created_by=actor);db.add(run);db.commit()
 try:
  from src.worker import analyze_group_run
  analyze_group_run.delay(run.id)
 except Exception:
  run.status='failed';run.error='队列不可用，请稍后重建';db.commit();raise HTTPException(503,run.error)
 record(db,actor,'group.run.queued',{'group_run_id':run.id,'members':len(snapshot['members'])});return row(run)
