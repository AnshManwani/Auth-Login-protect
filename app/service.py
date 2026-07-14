class ItemService:
    """Business logic layer. Doesn't care if repository is in-memory or Postgres."""

    def __init__(self, repository):
        self.repository = repository

    def create_item(self, name, description, user_id=None):
        if not name:
            raise ValueError("Name is required")
        return self.repository.create(name, description, user_id=user_id)

    def list_items(self):
        return self.repository.get_all()

    def get_item(self, item_id):
        return self.repository.get_by_id(item_id)

    def delete_item(self, item_id):
        return self.repository.delete(item_id)