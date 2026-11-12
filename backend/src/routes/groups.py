from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.controllers.dependencies import current_user,writers
from src.models import TraverseGroup,TraverseGroupRun
from src.schemas.group import GroupInput,GroupRunInput
from src.services.groups import create_group,create_group_run,group_view
from src.utils.serialize import row
router=APIRouter(prefix='/groups',tags=['groups'])
@router.get('')
def groups(db:Session=Depends(get_db),user=Depends(current_user)):return [group_view(db,g) for g in db.scalars(select(TraverseGroup).order_by(TraverseGroup.id.desc()))]
@router.post('')
def create(data:GroupInput,db:Session=Depends(get_db),user=Depends(writers)):return create_group(db,data,user.email)
@router.get('/runs')
def runs(db:Session=Depends(get_db),user=Depends(current_user)):return [row(r) for r in db.scalars(select(TraverseGroupRun).order_by(TraverseGroupRun.id.desc()))]
@router.get('/runs/{id}')
def one(id:int,db:Session=Depends(get_db),user=Depends(current_user)):
 run=db.get(TraverseGroupRun,id)
 if not run:raise HTTPException(404,'组运行不存在')
 return row(run)
@router.post('/runs')
def run(data:GroupRunInput,db:Session=Depends(get_db),user=Depends(writers)):return create_group_run(db,data,user.email)
