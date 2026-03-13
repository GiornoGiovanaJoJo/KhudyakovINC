import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from .database import Base


class LeadStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False)
    stack = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="")
    photo_url = Column(String(500), nullable=True, default="")
    order = Column(Integer, default=0)


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False, default="")
    icon = Column(String(50), nullable=True, default="💻")
    order = Column(Integer, default=0)


class PortfolioProject(Base):
    __tablename__ = "portfolio_projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    short_description = Column(String(500), nullable=False, default="")
    full_description = Column(Text, nullable=False, default="")
    image_url = Column(String(500), nullable=True, default="")
    slug = Column(String(200), unique=True, nullable=False)
    tags = Column(String(500), nullable=True, default="")
    order = Column(Integer, default=0)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact = Column(String(255), nullable=False)
    chat_history = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
