# временное хранилище для прототипа вместо бд
_users_db = {}

class UserService:

    def list_users(self):
        return [
            {"username": u, "role": data["role"], "email": data.get("email")}
            for u, data in _users_db.items()
        ]

    def create_user(self, username, password, role="user", email=None):
        if username in _users_db:
            raise ValueError("User already exists")

        _users_db[username] = {
            "password": password,
            "role": role,
            "email": email
        }

    def update_user(self, username, password=None, role=None, email=None):
        if username not in _users_db:
            raise ValueError("User not found")

        if password:
            _users_db[username]["password"] = password
        if role:
            _users_db[username]["role"] = role
        if email:
            _users_db[username]["email"] = email

    def delete_user(self, username):
        if username not in _users_db:
            raise ValueError("User not found")

        del _users_db[username]

    def get_user(self, username):
        return _users_db.get(username)