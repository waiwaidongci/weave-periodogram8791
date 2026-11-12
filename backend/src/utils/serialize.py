from datetime import datetime,date,timezone
from sqlalchemy import inspect
def _timestamp(value):
 if isinstance(value,datetime):
  if value.tzinfo is None:value=value.replace(tzinfo=timezone.utc)
  return value.astimezone(timezone.utc).isoformat()
 return value.isoformat() if isinstance(value,date) else value
def row(obj):
 return {c.key:_timestamp(getattr(obj,c.key)) for c in inspect(obj).mapper.column_attrs if c.key!='password_hash'}
