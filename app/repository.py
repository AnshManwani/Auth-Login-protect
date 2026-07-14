from app.models import Item


class InMemoryItemRepository:
    """Stores items in a Python list. Data is lost on restart."""

    def __init__(self):
        self._items = {}
        self._next_id = 1

    def create(self, name, description):
        item = Item(self._next_id, name, description)
        self._items[item.id] = item
        self._next_id += 1
        return item

    def get_all(self):
        return list(self._items.values())

    def get_by_id(self, item_id):
        return self._items.get(item_id)

    def delete(self, item_id):
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False