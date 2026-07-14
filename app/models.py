class Item:
    def __init__(self, id, name, description, user_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.user_id = user_id

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }


class User:
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

    def to_dict(self):
        """Never includes password_hash."""
        return {
            "id": self.id,
            "email": self.email
        }