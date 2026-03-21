from locust import HttpUser, between, task

class MyUser(HttpUser):
    wait_time = between(1, 5)  # Wait time between tasks in seconds

    @task(priority=1)
    def create_zone(self):
        data = {"name": "example-zone"}
        self.client.post("/zones", json=data)  # Выполнение POST-запроса для создания зоны

    @task(priority=2)
    def get_zones(self):
        self.client.get("/zones")  # Выполнение GET-запроса для получения списка зон

    @task(priority=3)
    def delete_zone(self):
        zone_name = "example-zone"  # Замените на фактическое имя зоны
        self.client.delete(f"/zones/{zone_name}")  # Выполнение DELETE-запроса для удаления зоны

    @task(priority=1)
    def create_record(self):
        data = {"zone": "example.com", "type": "A", "name": "test", "data": "192.168.1.1"}
        self.client.post("/records", json=data)  # Выполнение POST-запроса для создания записи

    @task(priority=2)
    def get_records(self):
        self.client.get("/records")  # Выполнение GET-запроса для получения списка записей

    @task(priority=3)
    def delete_record(self):
        record_id = "123456"  # Замените на фактический ID записи, которую нужно удалить
        self.client.delete(f"/records/{record_id}")  # Выполнение DELETE-запроса для удаления записи

    @task(priority=1)
    def create_user(self):
        data = {"username": "example_user", "password": "password", "role": "user", "email": "example@example.com"}
        self.client.post("/users", json=data)  # Выполнение POST-запроса для создания пользователя

    @task(priority=2)
    def get_users(self):
        self.client.get("/users")  # Выполнение GET-запроса для получения списка пользователей

    @task(priority=3)
    def delete_user(self):
        username = "example_user"  # Замените на фактическое имя пользователя
        self.client.delete(f"/users/{username}")  # Выполнение DELETE-запроса для удаления пользователя