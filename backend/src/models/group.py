from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey,String,Double,JSON,Text,DateTime,UniqueConstraint
from datetime import datetime,timezone
from src.config.database import Base
class TraverseGroup(Base):
 __tablename__='traverse_groups'
 id:Mapped[int]=mapped_column(primary_key=True)
 name:Mapped[str]=mapped_column(String(180),unique=True)
 protocol:Mapped[str]=mapped_column(Text)
 permutations:Mapped[int]=mapped_column()
 seed:Mapped[int]=mapped_column()
 created_by:Mapped[str]=mapped_column(String(120))
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
 members:Mapped[list['TraverseGroupMember']]=relationship(back_populates='group',order_by='TraverseGroupMember.ordinal',cascade='all, delete-orphan')
class TraverseGroupMember(Base):
 __tablename__='traverse_group_members'
 __table_args__=(UniqueConstraint('group_id','ordinal'),UniqueConstraint('group_id','study_id'))
 id:Mapped[int]=mapped_column(primary_key=True)
 group_id:Mapped[int]=mapped_column(ForeignKey('traverse_groups.id'))
 study_id:Mapped[int]=mapped_column(ForeignKey('traverse_studies.id'))
 plan_id:Mapped[int]=mapped_column(ForeignKey('frequency_plans.id'))
 ordinal:Mapped[int]=mapped_column()
 label:Mapped[str]=mapped_column(String(150))
 study_snapshot:Mapped[dict]=mapped_column(JSON)
 plan_snapshot:Mapped[dict]=mapped_column(JSON)
 source_fingerprint:Mapped[str]=mapped_column(String(64))
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
 group:Mapped[TraverseGroup]=relationship(back_populates='members')
class TraverseGroupRun(Base):
 __tablename__='traverse_group_runs'
 id:Mapped[int]=mapped_column(primary_key=True)
 group_id:Mapped[int]=mapped_column(ForeignKey('traverse_groups.id'))
 name:Mapped[str]=mapped_column(String(180),unique=True)
 group_snapshot:Mapped[dict]=mapped_column(JSON)
 source_snapshot:Mapped[dict]=mapped_column(JSON)
 source_fingerprints:Mapped[list]=mapped_column(JSON)
 group_fingerprint:Mapped[str]=mapped_column(String(64))
 status:Mapped[str]=mapped_column(String(24),default='queued')
 result:Mapped[dict|None]=mapped_column(JSON,nullable=True)
 error:Mapped[str|None]=mapped_column(Text,nullable=True)
 observed_max_power:Mapped[float|None]=mapped_column(Double(asdecimal=False),nullable=True)
 global_p:Mapped[float|None]=mapped_column(Double(asdecimal=False),nullable=True)
 winning_member_ordinal:Mapped[int|None]=mapped_column(nullable=True)
 winning_study_id:Mapped[int|None]=mapped_column(nullable=True)
 winning_frequency:Mapped[float|None]=mapped_column(Double(asdecimal=False),nullable=True)
 created_by:Mapped[str]=mapped_column(String(120))
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
