from pydantic import BaseModel,Field,ConfigDict,field_validator,model_validator
class GroupMemberInput(BaseModel):
 model_config=ConfigDict(allow_inf_nan=False,str_strip_whitespace=True)
 ordinal:int=Field(ge=1,le=64,strict=True)
 study_id:int=Field(gt=0,strict=True)
 plan_id:int=Field(gt=0,strict=True)
 label:str=Field(default='',max_length=150)
class GroupInput(BaseModel):
 model_config=ConfigDict(allow_inf_nan=False,str_strip_whitespace=True)
 name:str=Field(min_length=2,max_length=180)
 protocol:str=Field(min_length=5,max_length=3000)
 permutations:int=Field(ge=199,le=499,strict=True)
 seed:int=Field(ge=0,le=1000000000,strict=True)
 members:list[GroupMemberInput]=Field(min_length=1,max_length=64)
 @field_validator('members')
 @classmethod
 def unique_members(cls,members):
  ordinals=[m.ordinal for m in members];studies=[m.study_id for m in members]
  if len(set(ordinals))!=len(ordinals):raise ValueError('组内序号必须唯一')
  if len(set(studies))!=len(studies):raise ValueError('同一测线不能在组内重复登记')
  return members
class GroupRunInput(BaseModel):
 model_config=ConfigDict(str_strip_whitespace=True)
 group_id:int=Field(gt=0,strict=True)
 name:str=Field(min_length=2,max_length=180)
