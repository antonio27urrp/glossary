from typing import Optional
from sqlmodel import Field, SQLModel

# Эта модель и таблица в БД, и схема для вывода данных
class Term(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True, unique=True)
    description: str

# Эта модель — только схема для получения данных от пользователя (POST)
class TermCreate(SQLModel):
    keyword: str
    description: str

# Эта модель — только схема для частичного обновления (PATCH)
class TermUpdate(SQLModel):
    description: Optional[str] = None