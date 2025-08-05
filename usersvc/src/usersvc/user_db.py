from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str
    name: str

_DB = {
    "u1": User(id="u1", email="alice@example.com", name="Alice"),
    "u2": User(id="u2", email="bob@example.com",   name="Bob"),
}

def get_user(user_id: str) -> User | None:
    return _DB.get(user_id)
