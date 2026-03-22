import datetime
from datetime import timezone
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship
from .database import Base


class LeadStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class LeadPriority(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False)
    stack = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True, default="")
    order = Column(Integer, default=0)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    telegram = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.ADMIN)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc))

    leads = relationship("Lead", back_populates="user")
    projects_created = relationship("Project", back_populates="creator", foreign_keys="Project.created_by_id")
    tasks_assigned = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    tasks_reported = relationship("Task", back_populates="reporter", foreign_keys="Task.reporter_id")


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
    figma_url = Column(String(500), nullable=True)
    external_url = Column(String(500), nullable=True)
    gallery = Column(JSON, nullable=True, default=list)  # List of image URLs
    order = Column(Integer, default=0)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact = Column(String(255), nullable=False)
    chat_history = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW)
    priority = Column(SQLEnum(LeadPriority), default=LeadPriority.WARM)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="leads")
    notes = relationship("LeadNote", back_populates="lead", cascade="all, delete-orphan")


class LeadNote(Base):
    __tablename__ = "lead_notes"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    author = Column(String(100), nullable=False, default="admin")
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    lead = relationship("Lead", back_populates="notes")


class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, nullable=False)
    platform = Column(String(20), nullable=False, default="android")
    admin_username = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE)
    deadline = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    creator = relationship("User", back_populates="projects_created", foreign_keys=[created_by_id])
    members = relationship("User", secondary=project_members, backref="projects_assigned")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc), onupdate=lambda: datetime.datetime.now(timezone.utc))

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks_assigned", foreign_keys=[assignee_id])
    reporter = relationship("User", back_populates="tasks_reported", foreign_keys=[reporter_id])
