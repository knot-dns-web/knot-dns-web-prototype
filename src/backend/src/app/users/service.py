from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

        hashed_password = pwd_context.hash(password)
        
        _users_db[username] = {
            "password": hashed_password,
            "role": role,
            "email": email
        }

    def update_user(self, username, password=None, role=None, email=None):
        if username not in _users_db:
            raise ValueError("User not found")

        if password:
            _users_db[username]["password"] = pwd_context.hash(password)
        if role:
            _users_db[username]["role"] = role
        if email is not None:
            _users_db[username]["email"] = email

    def delete_user(self, username):
        if username not in _users_db:
            raise ValueError("User not found")

        del _users_db[username]

    def get_user(self, username):
        user_data = _users_db.get(username)
        if user_data:
            # Возвращаем копию с добавленным username
            return {**user_data, "username": username}
        return None