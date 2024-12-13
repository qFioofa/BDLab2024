import os
import json

class BTree:
    root_node: str
    t: int = 3
    __counter: int = -1

    def __init__(self, template: dict[str, dict], dir: str) ->None:
        self.dir: str = dir
        self.template: dict[str,str] = template
        self.__define_root()
        self.__counter = self.__determine_counter()

    def __determine_counter(self) -> int:
        max_counter = -1

        for file_name in os.listdir(self.dir):
            if file_name.startswith("node") and file_name.endswith(".json"):
                try:
                    count = int(file_name[4:-5])
                    if count > max_counter:
                        max_counter: int = count
                except ValueError:
                    continue

        return max_counter

    def __define_root(self) -> None:
        for record in os.listdir(self.dir):
            node_info: dict = self.__read_node(os.path.join(self.dir, record))
            if "is_leaf" in node_info and not node_info.get("is_leaf"):
                self.root_node = record
                return

        self.root_node = self.__get_next_node_name()

        with open(self.__get_full_path(self.root_node), 'w', encoding='utf-8') as file:
            json.dump(self.__root_node(), file, indent=4, ensure_ascii=False)

    def __get_next_node_name(self) -> str:
        while True:
            self.__counter += 1
            node_name: str = f"node{self.__counter}.json"
            if not os.path.exists(self.__get_full_path(node_name)):
                return node_name

    def __root_node(self) -> dict[str]:
        return {
            "is_leaf": True,
            "children": [],
            "record": []
        }

    @staticmethod
    def __compare_records(dict1, dict2, partial = False) -> bool:
        if partial:
            for key, value in dict1.items():
                if str(dict2.get(key)) != str(value):
                    return False
            return True

        for key in sorted(set(dict1.keys()).union(dict2.keys())):
            val1 = str(dict1.get(key, ""))
            val2 = str(dict2.get(key, ""))
            if val1 < val2:
                return -1
            if val1 > val2:
                return 1
        return 0

    def __sord_records(self, records: list[dict[str, str]]) -> list:
        return sorted(records, key=lambda x: [str(v) for v in x.values()])

    def read_node(self, file_name)-> dict:
        return self.__read_node(self.__get_full_path(file_name))

    def __get_full_path(self, record) -> str:
        return os.path.join(self.dir, record)

    def __read_node(self, file_path) -> dict:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def insert(self, data: dict[str, str]) -> None:
        existing_records: list[dict[str, str]] = self.find(data["keys"])
        if existing_records:
            print(f"Запись с ключами {data['keys']} уже существует. Вставка не выполнена.")
            return
        root_data: dict = self.read_node(self.root_node)
        if len(root_data["record"]) == 2 * self.t - 1:
            new_root: str = self.__get_next_node_name()
            new_root_data = {
                "is_leaf": False,
                "children": [self.root_node],
                "record": []
            }
            with open(self.__get_full_path(new_root), 'w', encoding='utf-8') as file:
                json.dump(new_root_data, file, indent=4, ensure_ascii=False)
            self.__split_children(new_root, 0)
            self.root_node = new_root
            self.__insert_non_full(new_root, data)
        else:
            self.__insert_non_full(self.root_node, data)

    def __split_children(self, node_file: str, position: int) -> None:
        node_data: dict = self.read_node(node_file)
        child_file: str = node_data["children"][position]
        child_data: dict = self.read_node(child_file)

        mid_index: int = self.t - 1
        mid_record: str = child_data["record"][mid_index%len(child_data["record"])]

        new_node_file: str = self.__get_next_node_name()
        new_node_data: dict[str] = {
            "is_leaf": child_data["is_leaf"],
            "children": child_data["children"][mid_index + 1:] if not child_data["is_leaf"] else [],
            "record": child_data["record"][mid_index + 1:]
        }

        child_data["record"] = child_data["record"][:mid_index]
        if not child_data["is_leaf"]:
            child_data["children"] = child_data["children"][:mid_index + 1]

        node_data["record"].insert(position, mid_record)
        node_data["children"].insert(position + 1, new_node_file)

        with open(self.__get_full_path(child_file), 'w', encoding='utf-8') as file:
            json.dump(child_data, file, indent=4, ensure_ascii=False)
        with open(self.__get_full_path(new_node_file), 'w', encoding='utf-8') as file:
            json.dump(new_node_data, file, indent=4, ensure_ascii=False)
        with open(self.__get_full_path(node_file), 'w', encoding='utf-8') as file:
            json.dump(node_data, file, indent=4, ensure_ascii=False)

    def __insert_non_full(self, node_file: str, data: dict[str, str]) -> None:
        node_data = self.read_node(node_file)
        if node_data["is_leaf"]:
            node_data["record"] = self.__sord_records(node_data["record"] + [data])
            with open(self.__get_full_path(node_file), 'w', encoding='utf-8') as file:
                json.dump(node_data, file, indent=4, ensure_ascii=False)
        else:
            i: int = len(node_data["record"]) - 1
            while i >= 0 and self.__compare_records(data, node_data["record"][i]) < 0:
                i -= 1
            i += 1

            child_file = node_data["children"][i]
            child_data: dict = self.read_node(child_file)

            if len(child_data["record"]) == 2 * self.t - 1:
                self.__split_children(node_file, i)

                node_data: dict = self.read_node(node_file)
                if self.__compare_records(data, node_data["record"][i]) > 0:
                    i += 1
            self.__insert_non_full(node_data["children"][i], data)

    def find(self, query: dict[str, str]) -> list[dict[str, str]]:
        result: list = []

        def _search_in_node(node_file: str, query: dict[str, str]) -> None:
            node_data: dict = self.read_node(node_file)
            for record in node_data["record"]:
                if self.__compare_records(query, record["keys"], partial=True):
                    result.append(record)

            if node_data["is_leaf"]:
                return []

            for child in node_data["children"]:
                _search_in_node(child, query)

        _search_in_node(self.root_node, query)
        return result

    def find_by_value(self, values: dict[str, str]) -> list[dict[str, str]]:
        all_data: list[dict[str, str]] = self.all_records()
        result: list = []

        for record in all_data:
            if self.__values_check(record["values"], values):
                result.append(record)

        return result

    def __values_check(self, values1 : dict[str, str], values2 : dict[str, str]) -> bool:
        v_values1 : list[str] = values1.keys()
        v_values2 : list[str] = values2.keys()
        if len(v_values1) < len(v_values2):
            v_values1, v_values2 = v_values2, v_values1
        if all(values1[key] == values2[key] for key in v_values2): return True
        return False

    def all_records(self) -> list[dict[str, str]]:
        result: list = []

        def _collect_records(node_file: str) -> None:
            node_data: dict = self.read_node(node_file)
            result.extend(node_data["record"])

            for child in node_data["children"]:
                _collect_records(child)

        _collect_records(self.root_node)
        return result

    def delete(self, query: dict[str, str]) -> bool:
        result: list = []
        def _delete_from_node(node_file: str, query: dict[str, str]) -> bool:
            node_data: dict = self.read_node(node_file)
            for i, record in enumerate(node_data["record"]):
                if self.__compare_records(query, record["keys"], partial=True):
                    result.append(node_data["record"][i])
                    node_data["record"].pop(i)

                    with open(self.__get_full_path(node_file), 'w', encoding='utf-8') as file:
                        json.dump(node_data, file, indent=4, ensure_ascii=False)

                    return result

            if node_data["is_leaf"]:
                return result

            for child in node_data["children"]:
                if _delete_from_node(child, query):
                    return result

            return result

        return _delete_from_node(self.root_node, query)

    def delete_by_value(self, values: dict[str, str]) -> list[dict[str, str]]:
        result: list = []

        def _delete_from_node_by_value(node_file: str, values: dict[str, str]) -> None:
            node_data: dict = self.read_node(node_file)
            i = 0

            while i < len(node_data["record"]):
                if self.__values_check(node_data["record"][i]["values"], values):
                    result.append(node_data["record"].pop(i))
                else:
                    i += 1

            with open(self.__get_full_path(node_file), 'w', encoding='utf-8') as file:
                json.dump(node_data, file, indent=4, ensure_ascii=False)

            if not node_data["is_leaf"]:
                for child in node_data["children"]:
                    _delete_from_node_by_value(child, values)

        _delete_from_node_by_value(self.root_node, values)

        return result

    def edit(self, new_data: dict[str, str]) -> bool:
        def _edit_in_node(node_file: str, new_data: dict[str, str]) -> bool:
            node_data: dict = self.read_node(node_file)
            for i, record in enumerate(node_data["record"]):
                if self.__compare_records(new_data["keys"], record["keys"], partial=True):

                    node_data["record"][i] = new_data
                    with open(self.__get_full_path(node_file), 'w', encoding='utf-8') as file:
                        json.dump(node_data, file, indent=4, ensure_ascii=False)
                    return True

            if not node_data["is_leaf"]:
                for child in node_data["children"]:
                    if _edit_in_node(child, new_data):
                        return True

            return False

        if _edit_in_node(self.root_node, new_data):
            print(f"Запись с ключами {new_data['keys']} успешно обновлена.")
            return True
        else:
            raise ValueError("Records doesn't match by keys")

