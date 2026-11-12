import json,hashlib
from datetime import datetime,timezone,date
from src.constants.numerics import ALGORITHM_VERSION,GROUP_ALGORITHM_VERSION

def canonical(value):
 if isinstance(value,datetime):
  if value.tzinfo is None:value=value.replace(tzinfo=timezone.utc)
  return value.astimezone(timezone.utc).isoformat()
 if isinstance(value,(date,)):return value.isoformat()
 if isinstance(value,dict):return {k:canonical(v) for k,v in value.items()}
 if isinstance(value,(list,tuple)):return [canonical(v) for v in value]
 return value

def fingerprint(study,points,plan):
 payload=canonical({'version':ALGORITHM_VERSION,'study':study,'points':sorted(points,key=lambda p:p['position']),'plan':plan})
 return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def group_fingerprint(group,members):
 payload=canonical({'version':GROUP_ALGORITHM_VERSION,'group':{'name':group.name,'protocol':group.protocol,'permutations':group.permutations,'seed':group.seed},'members':[{'ordinal':m['ordinal'],'label':m['label'],'source_fingerprint':m['source_fingerprint']} for m in members]})
 return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
