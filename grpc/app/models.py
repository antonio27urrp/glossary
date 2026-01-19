from typing import Optional
from sqlmodel import Field, SQLModel

class Term(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True, unique=True)
    description: str