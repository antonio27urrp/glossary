import grpc
from concurrent import futures
from sqlmodel import Session, select, SQLModel

# Импортируем ваши существующие настройки и модели
from .database import engine
from .models import Term

# Импортируем сгенерированные gRPC файлы
import app.glossary_pb2 as pb2
import app.glossary_pb2_grpc as pb2_grpc

class GlossaryService(pb2_grpc.GlossaryServiceServicer):
    """Реализация методов, описанных в glossary.proto"""

    def GetTerms(self, request, context):
        with Session(engine) as session:
            terms = session.exec(select(Term)).all()
            # Формируем список сообщений Term для Protobuf
            return pb2.TermList(terms=[
                pb2.Term(keyword=t.keyword, description=t.description) 
                for t in terms
            ])

    def GetTerm(self, request, context):
        with Session(engine) as session:
            term = session.exec(select(Term).where(Term.keyword == request.keyword)).first()
            if not term:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Термин не найден")
                return pb2.Term()
            return pb2.Term(keyword=term.keyword, description=term.description)

    def AddTerm(self, request, context):
        with Session(engine) as session:
            # Проверка на дубликат (так как keyword уникален)
            existing = session.exec(select(Term).where(Term.keyword == request.keyword)).first()
            if existing:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Термин уже существует")
                return pb2.Term()
                
            db_term = Term(keyword=request.keyword, description=request.description)
            session.add(db_term)
            session.commit()
            session.refresh(db_term)
            return pb2.Term(keyword=db_term.keyword, description=db_term.description)

    def UpdateTerm(self, request, context):
        with Session(engine) as session:
            db_term = session.exec(select(Term).where(Term.keyword == request.keyword)).first()
            if not db_term:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return pb2.Term()
            
            db_term.description = request.description
            session.add(db_term)
            session.commit()
            session.refresh(db_term)
            return pb2.Term(keyword=db_term.keyword, description=db_term.description)

    def DeleteTerm(self, request, context):
        with Session(engine) as session:
            db_term = session.exec(select(Term).where(Term.keyword == request.keyword)).first()
            if not db_term:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return pb2.DeleteResponse(success=False)
            
            session.delete(db_term)
            session.commit()
            return pb2.DeleteResponse(success=True)

def serve():
    # Инициализация таблиц в SQLite (database.db)
    SQLModel.metadata.create_all(engine)
    
    # Создание gRPC сервера
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_GlossaryServiceServicer_to_server(GlossaryService(), server)
    
    # Слушаем порт 50051
    server.add_insecure_port('[::]:50051')
    print("-----------------------------------------")
    print("gRPC Сервер запущен на порту 50051")
    print("Используйте Postman или Evans для тестов")
    print("-----------------------------------------")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()