from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .models import LeadStatus


# ── Team ──────────────────────────────────────────────

class TeamMemberBase(BaseModel):
    name: str
    position: str
    stack: str
    description: str = ""
    photo_url: str = ""
    order: int = 0


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    stack: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None
    order: Optional[int] = None


class TeamMemberResponse(TeamMemberBase):
    id: int

    class Config:
        from_attributes = True


# ── Services ──────────────────────────────────────────

class ServiceBase(BaseModel):
    title: str
    description: str = ""
    icon: str = "💻"
    order: int = 0


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    order: Optional[int] = None


class ServiceResponse(ServiceBase):
    id: int

    class Config:
        from_attributes = True


# ── Portfolio ─────────────────────────────────────────

class PortfolioBase(BaseModel):
    title: str
    short_description: str = ""
    full_description: str = ""
    image_url: str = ""
    slug: str
    tags: str = ""
    order: int = 0


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    image_url: Optional[str] = None
    slug: Optional[str] = None
    tags: Optional[str] = None
    order: Optional[int] = None


class PortfolioResponse(PortfolioBase):
    id: int

    class Config:
        from_attributes = True


# ── Auth ──────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Chat ──────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    text: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    has_submitted_lead: bool = False
    quiz_context: Optional[dict] = None


class ChatResponse(BaseModel):
    reply: str


# ── Leads ─────────────────────────────────────────────

class LeadBase(BaseModel):
    name: str
    contact: str
    chat_history: Optional[str] = ""
    ai_summary: Optional[str] = ""
    status: LeadStatus = LeadStatus.NEW


class LeadCreate(LeadBase):
    is_supplement: bool = False


class LeadUpdate(BaseModel):
    status: Optional[LeadStatus] = None


class LeadResponse(LeadBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
