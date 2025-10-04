from typing import List, Optional
from pydantic import BaseModel

class FeedbackInput(BaseModel):
    meeting_id: str
    rating: int
    comments: str = None

class MeetingInput(BaseModel):
    file_path: Optional[str] = None  # Explicitly allow None
    language: str = "en"
    notify_slack: bool = False
    channel: Optional[str] = None
    industry: Optional[str] = None
    user_id: Optional[str] = None
    meeting_title: Optional[str] = None  
    custom_prompt_description: Optional[str] = None

    class Config:
        extra = "forbid"

    @classmethod
    def from_dict(cls, data: dict):
        # Handle null or missing fields; file_path is optional
        input_data = {
            "file_path": data.get("file_path", None),  # Allow None
            "language": data.get("language", "en"),
            "notify_slack": data.get("notify_slack", False),
            "channel": data.get("channel", "") if data.get("notify_slack", False) else "",
            "industry": data.get("industry", "General"),
            "user_id": data.get("user_id", "anonymous"),
            "meeting_title": data.get("meeting_title", "Untitled Meeting"),
            "custom_prompt_description": data.get("custom_prompt_description", None)
        }
        return cls(**input_data)
    

class ActionItem(BaseModel):
    description: str
    assignee: str
    deadline: str
    priority: str
    meeting_id: str
    industry: Optional[str] = None

class MeetingRecord(BaseModel):
    meeting_id: str
    title: str
    industry: str
    summary: str
    sentiment: Optional[str]
    action_items: List[ActionItem]
    date: str