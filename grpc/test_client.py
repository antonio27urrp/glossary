import grpc
import app.glossary_pb2 as pb2
import app.glossary_pb2_grpc as pb2_grpc

def run():
    # Подключаемся к серверу
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = pb2_grpc.GlossaryServiceStub(channel)
        
        # 1. Тест: Добавление термина
        print("--- Добавление термина ---")
        try:
            new_term = stub.AddTerm(pb2.Term(keyword="gRPC", description="Высокопроизводительный фреймворк от Google"))
            print(f"Добавлено: {new_term.keyword}")
        except grpc.RpcError as e:
            print(f"Ошибка или уже существует: {e.details()}")

        # 2. Тест: Получение списка
        print("\n--- Список всех терминов ---")
        response = stub.GetTerms(pb2.Empty())
        for term in response.terms:
            print(f"[*] {term.keyword}: {term.description}")

if __name__ == "__main__":
    run()