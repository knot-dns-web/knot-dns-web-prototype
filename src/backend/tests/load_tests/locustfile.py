import uuid
from locust import HttpUser, between, task

class MyUser(HttpUser):
    wait_time = between(1, 5)  # Wait time between tasks in seconds
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.unique_id = uuid.uuid4().hex[:8]  # Unique ID for this user
    
    def on_start(self):
        """Login when the user starts"""
        response = self.client.post("/auth/login", data={
            "username": "admin",
            "password": "admin"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
    
    def get_headers(self):
        """Get headers with authorization token"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    @task
    def create_zone_with_record(self):
        """Create zone, create record, delete record, delete zone"""
        zone_name = f"zone-{self.unique_id}."  # DNS zones should end with dot
        owner_name = "test"
        record_type = "A"
        record_data = "192.168.1.1"
        
        # 1. Create zone
        zone_data = {"name": zone_name}
        self.client.post("/zones", json=zone_data, headers=self.get_headers())
        
        # 2. Create record in the zone
        record_payload = {
            "zone": zone_name,
            "owner": owner_name,
            "type": record_type,
            "ttl": 3600,
            "data": record_data
        }
        self.client.post("/records", json=record_payload, headers=self.get_headers())
        
        # 3. Delete record
        self.client.delete(
            f"/records/{zone_name}/{owner_name}/{record_type}?data={record_data}",
            headers=self.get_headers()
        )
        
        # 4. Delete zone
        self.client.delete(f"/zones/{zone_name}", headers=self.get_headers())

    @task
    def get_zones(self):
        self.client.get("/zones", headers=self.get_headers())

    @task
    def get_records(self):
        self.client.get("/records", headers=self.get_headers())

  
