from fastapi import FastAPI
from sqlmodel import create_engine,String,SQLModel,Field,Session,select
from typing import List, Optional,Dict, Annotated
# from pydantic import BaseModel,Field 
from datetime import datetime


class TodoBase(SQLModel):
    title: str
    description: str
    completed: bool = False

class Todo(TodoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default=datetime.now())
    updated_at: Optional[datetime] = Field(default=datetime.now())

class TodoCreate(TodoBase):
    pass

class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    updated_at: datetime = Field(default=datetime.now())

# class TodoRead(TodoBase):
#     id: int
#     created_at: datetime
#     updated_at: datetime

