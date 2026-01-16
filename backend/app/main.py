from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from .database import engine, SQLModel
from .models import Term, TermCreate, TermUpdate

app = FastAPI(title="Glossary API")

# Создаем таблицы при запуске
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# 1. Получение списка всех терминов (уже работает)
@app.get("/terms", response_model=list[Term])
def read_terms(session: Session = Depends(get_session)):
    return session.exec(select(Term)).all()

# 2. Получение одного термина по слову (ТЗ пункт 2)
@app.get("/terms/{keyword}", response_model=Term)
def read_term(keyword: str, session: Session = Depends(get_session)):
    term = session.exec(select(Term).where(Term.keyword == keyword)).first()
    if not term:
        raise HTTPException(status_code=404, detail="Термин не найден")
    return term

# 3. Добавление термина (уже работает)
@app.post("/terms", response_model=Term)
def create_term(term_data: TermCreate, session: Session = Depends(get_session)):
    db_term = Term.from_orm(term_data)
    session.add(db_term)
    session.commit()
    session.refresh(db_term)
    return db_term

# 4. Обновление термина (ТЗ пункт 4)
@app.patch("/terms/{keyword}", response_model=Term)
def update_term(keyword: str, term_data: TermUpdate, session: Session = Depends(get_session)):
    db_term = session.exec(select(Term).where(Term.keyword == keyword)).first()
    if not db_term:
        raise HTTPException(status_code=404, detail="Термин не найден")
    if term_data.description:
        db_term.description = term_data.description
    session.add(db_term)
    session.commit()
    session.refresh(db_term)
    return db_term

# 5. Удаление термина (ТЗ пункт 5)
@app.delete("/terms/{keyword}")
def delete_term(keyword: str, session: Session = Depends(get_session)):
    db_term = session.exec(select(Term).where(Term.keyword == keyword)).first()
    if not db_term:
        raise HTTPException(status_code=404, detail="Термин не найден")
    session.delete(db_term)
    session.commit()
    return {"ok": True, "message": f"Термин {keyword} удален"}

from fastapi.middleware.cors import CORSMiddleware

# Добавьте это сразу после создания app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Разрешает запросы с любых адресов
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)