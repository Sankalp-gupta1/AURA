from typing import Optional, List
from pydantic import BaseModel, model_validator
from datetime import datetime


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    picture: str
    last_synced_at: str

    class Config:
        from_attributes = True


class EmailOut(BaseModel):
    id: int
    sender: str
    subject: str
    snippet: str
    email_date: str
    category: str
    priority: str
    is_important: bool
    ai_summary: str

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "Medium"
    deadline: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[str] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    status: str
    deadline: str
    source: str

    class Config:
        from_attributes = True


class EventOut(BaseModel):
    id: int
    title: str
    description: str
    location: str
    start_time: str
    end_time: str
    meet_link: str

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    title: str
    start_time: str
    end_time: str
    description: str = ""
    location: str = ""

    @model_validator(mode="after")
    def validate_event_times(self):
        start = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
        end = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("Event times must include a timezone offset")
        if end <= start:
            raise ValueError("Event end must be after its start")
        if not self.title.strip():
            raise ValueError("Event title is required")
        return self


class NoteCreate(BaseModel):
    content: str


class NoteOut(BaseModel):
    id: int
    content: str

    class Config:
        from_attributes = True


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


class DashboardStats(BaseModel):
    emails: int
    tasks_pending: int
    events_upcoming: int
    important_emails: int


class BriefingOut(BaseModel):
    daily_briefing: str
    top_focus: List[str]
    risks: List[str]
    suggested_actions: List[str]
    motivational_note: str
    generated_at: str


class MemoryOut(BaseModel):
    id: int
    content: str
    category: str
    importance: int
    source: str

    class Config:
        from_attributes = True


class MemoryCreate(BaseModel):
    content: str
    category: str = "fact"


class ActionOut(BaseModel):
    id: int
    task_id: Optional[int]
    action_type: str
    title: str
    description: str
    payload: dict
    status: str
    result_note: str

    class Config:
        from_attributes = True
