from sqlmodel import create_engine

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Именно эту переменную 'engine' ищет ваш main.py
engine = create_engine(sqlite_url, echo=True)