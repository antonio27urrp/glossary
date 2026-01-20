import grpc
import time
from locust import User, HttpUser, task, between, events
import app.glossary_pb2 as pb2
import app.glossary_pb2_grpc as pb2_grpc

# Кастомный клиент для gRPC с подсчетом размера данных
class GrpcClient:
    def __init__(self, host):
        self.channel = grpc.insecure_channel(host)
        self.stub = pb2_grpc.GlossaryServiceStub(self.channel)

    def __getattr__(self, name):
        func = getattr(self.stub, name)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                # Вычисляем размер бинарного сообщения
                response_length = result.ByteSize() if hasattr(result, "ByteSize") else 0
                
                events.request.fire(
                    request_type="grpc",
                    name=name,
                    response_time=(time.perf_counter() - start_time) * 1000,
                    # Теперь передаем реальный размер в байтах
                    response_length=response_length,
                    exception=None,
                )
                return result
            except Exception as e:
                events.request.fire(
                    request_type="grpc",
                    name=name,
                    response_time=(time.perf_counter() - start_time) * 1000,
                    response_length=0,
                    exception=e,
                )
                raise e
        return wrapper

# Класс для тестирования gRPC
class GlossaryGrpcUser(User):
    # Устанавливаем вес, чтобы Locust запускал оба класса
    weight = 1
    wait_time = between(1, 2)
    host = "localhost:50051"

    def on_start(self):
        self.client = GrpcClient(self.host)

    @task(3)
    def GetTerms(self):
        self.client.GetTerms(pb2.Empty())

    @task(1)
    def AddTerm(self):
        # Генерируем уникальный ключ, чтобы не было ошибок в БД
        unique_key = f"term_{int(time.time() * 1000)}"
        self.client.AddTerm(pb2.Term(keyword=unique_key, description="Test description"))

# Класс для тестирования REST (FastAPI)
class GlossaryRestUser(HttpUser):
    weight = 1
    wait_time = between(1, 2)
    # Host укажем в интерфейсе Locust (http://localhost:8000)
    host = "http://localhost:8000"
    @task(3)
    def GetTermsRest(self):
        self.client.get("/terms", name="/terms (REST)")

    @task(1)
    def AddTermRest(self):
        unique_key = f"rest_{int(time.time() * 1000)}"
        self.client.post("/terms", 
                         json={"keyword": unique_key, "description": "Test REST"},
                         name="/terms (REST POST)")