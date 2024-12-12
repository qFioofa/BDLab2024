from BTree import BTree
from HashTable import HashTable
from dbInfo import (
    IMPLEMENTATIONS,
    DATA_TEMPLATES
)

class DataBaseHandler:
    implementations: list[str] = IMPLEMENTATIONS
    templates: dict[str, dict[str, str]] = DATA_TEMPLATES
    current_implementation: str
    current_template: dict[str, str]
    handler: BTree | HashTable

    def __init__(self) ->None:
        self.handler = None
        self.current_implementation = None
        self.current_template = None

    def set_implementation(self, implementation: str, db_path: str) ->None:
        if implementation not in self.implementations:
            raise SyntaxError("Wrong implementation")

        self.current_implementation = implementation
        match implementation:
            case "B-Tree":
                if not self.current_template:
                    raise ValueError("Template must be set before creating a B-Tree handler.")
                self.handler = BTree(self.current_template)
            case "Hash-table":
                if not self.current_template:
                    raise ValueError("Template must be set before creating a HashTable handler.")
                self.handler = HashTable(self.current_template, db_path)

    def set_data_template(self, template: str) -> None:
        if template not in self.templates.keys():
            raise SyntaxError("Wrong template")
        self.current_template = self.templates[template]

    def get_template(self) -> dict[str, str]:
        return self.current_template

    def insert_data(self, data) -> None:
        if not self.handler:
            raise ValueError("Handler is not set. Use `set_implementation` to initialize the handler.")
        self.handler.insert(data)

    def find_by_key(self, keys) -> list:
        if not self.handler:
            raise ValueError("Handler is not set. Use `set_implementation` to initialize the handler.")
        return self.handler.find(keys)

    def find_by_value(self, value)-> list:
        if not self.handler:
            raise ValueError("Handler is not set. Use `set_implementation` to initialize the handler.")
        return self.handler.find_by_value(value)

    def delete_by_key(self, keys)-> list:
        if not self.handler:
            raise ValueError("Handler is not set. Use `set_implementation` to initialize the handler.")
        return self.handler.delete(keys)

    def delete_by_value(self, value)-> list:
        if not self.handler:
            raise ValueError("Handler is not set. Use `set_implementation` to initialize the handler.")
        return self.handler.delete_by_value(value)

    def all_records(self)-> list:
        if not self.handler:
            raise ValueError("Handler is not set. Use `set_implementation` to initialize the handler.")
        return self.handler.all_records()

    def edit(self,record, updated_data) -> bool:
        if not self.handler:
            raise ValueError("Handler is not set. Use `set_implementation` to initialize the handler.")
        return self.handler.edit(record, updated_data)
