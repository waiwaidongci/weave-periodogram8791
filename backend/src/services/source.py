from sqlalchemy import select
from fastapi import HTTPException
from src.models import TraverseStudy,TraversePoint,FrequencyPlan
from src.utils.serialize import row
from .validation import validate_points,validate_plan
from .audit import record
from .fingerprint import fingerprint

def source_snapshot(db,study_id,plan_id=None):
 study=db.get(TraverseStudy,study_id)
 if not study:raise HTTPException(404,'测线研究不存在')
 points=[row(p) for p in db.scalars(select(TraversePoint).where(TraversePoint.study_id==study_id).order_by(TraversePoint.position))]
 plan=db.get(FrequencyPlan,plan_id) if plan_id is not None else None
 if plan_id is not None and not plan:raise HTTPException(422,'频率计划不存在')
 if plan is not None and plan.study_id!=study.id:raise HTTPException(422,'频率计划不属于该测线')
 study_row=row(study);plan_row=row(plan) if plan is not None else None
 if plan is not None:validate_points(points);validate_plan(plan_row)
 return {'study':study_row,'points':points,'plan':plan_row,'source_fingerprint':fingerprint(study_row,points,plan_row)}

def create_study(db,data,actor):
 if db.scalar(select(TraverseStudy).where(TraverseStudy.name==data.name)):raise HTTPException(409,'测线研究名已存在')
 try:points=validate_points([p.model_dump() for p in data.points])
 except ValueError as error:raise HTTPException(422,str(error))
 study=TraverseStudy(**data.model_dump(exclude={'points'}));db.add(study);db.flush()
 for point in points:db.add(TraversePoint(study_id=study.id,**point))
 db.commit();record(db,actor,'study.imported',{'study_id':study.id,'points':len(points)});return row(study)

def source_data(db,id):
 study=db.get(TraverseStudy,id)
 if not study:raise HTTPException(404,'测线研究不存在')
 return row(study),[row(p) for p in db.scalars(select(TraversePoint).where(TraversePoint.study_id==id).order_by(TraversePoint.position))]

def edit_point(db,id,data,actor):
 point=db.get(TraversePoint,id)
 if not point:raise HTTPException(404,'测点不存在')
 _,points=source_data(db,point.study_id);candidate=[dict(p,position=data.position,thickness=data.thickness) if p['id']==id else p for p in points]
 try:validate_points(candidate)
 except ValueError as error:raise HTTPException(422,str(error))
 point.position=data.position;point.thickness=data.thickness;db.commit();record(db,actor,'point.revised',{'point_id':id});return row(point)
