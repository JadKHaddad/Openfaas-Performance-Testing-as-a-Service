from locust import HttpUser, task, between

print("started")
class User(HttpUser):
    wait_time = between(1, 5)
    host = "https://google.com"
    

    @task
    def my_task(self):
        self.client.get("/")

    @task
    def task_404(self):
        self.client.get("/non-existing-path")

