"""
Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class CategoryEnum(str, Enum):
    work = "work"
    school = "school"
    personal = "personal"


class PriorityEnum(int, Enum):
    high = 1
    medium = 2
    low = 3


class SourceEnum(str, Enum):
    self_ = "self"
    lisa = "lisa"
    calendar = "calendar"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: CategoryEnum = CategoryEnum.personal
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[str] = None  # ISO date: "2026-03-30"
    due_time: Optional[str] = None  # "14:30"
    source: SourceEnum = SourceEnum.self_
    notes: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[CategoryEnum] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    notes: Optional[str] = None


class BulkCreateRequest(BaseModel):
    tasks: list[TaskCreate] = Field(..., min_length=1)


class ReorderRequest(BaseModel):
    task_ids: list[int] = Field(..., min_length=1)


class PrintRequest(BaseModel):
    task_ids: list[int] = Field(default=None)
    category: Optional[CategoryEnum] = None
    all_open: bool = False


class TaskResponse(BaseModel):
    id: int
    title: str
    category: str
    priority: int
    due_date: Optional[str]
    due_time: Optional[str]
    sort_order: int
    status: str
    source: str
    notes: Optional[str]
    created_at: str
    archived_at: Optional[str]
    printed_at: Optional[str]

    class Config:
        from_attributes = True
