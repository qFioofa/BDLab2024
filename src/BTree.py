import os
import json
import shutil

class BTreeNode:
    def __init__(self, path: str, is_leaf: bool):
        self.path = path
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        if os.path.exists(path):
            self._load_node()

    def _load_node(self):
        files = os.listdir(self.path)
        for file in files:
            if file.endswith(".json"):
                self.keys.append(os.path.join(self.path, file))
        for child in os.listdir(self.path):
            child_path = os.path.join(self.path, child)
            if os.path.isdir(child_path):
                self.children.append(child_path)

    def _save_node(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if not self.is_leaf:
            for child in self.children:
                child_name = os.path.basename(child)
                child_dir = os.path.join(self.path, child_name)
                if not os.path.exists(child_dir):
                    os.makedirs(child_dir)

    def split(self):
        mid_index = len(self.keys) // 2
        mid_key = self.keys[mid_index]
        sibling_path = os.path.join(self.path, f"Sibling_{mid_index}")
        sibling = BTreeNode(sibling_path, self.is_leaf)
        sibling.keys = self.keys[mid_index + 1:]
        self.keys = self.keys[:mid_index]
        if not self.is_leaf:
            sibling.children = self.children[mid_index + 1:]
            self.children = self.children[:mid_index + 1]
        self._save_node()
        sibling._save_node()
        return mid_key, sibling.path

    def insert_non_full(self, key, value, minimum_degree):
        if self.is_leaf:
            key_file = self._save_record(key, value)
            self.keys.append(key_file)
            self.keys.sort()
            self._save_node()
        else:
            index = 0
            while index < len(self.keys):
                with open(self.keys[index], "r") as f:
                    record = json.load(f)
                    file_key = tuple(record["keys"])
                if key > file_key:
                    index += 1
                else:
                    break
            child_path = self.children[index]
            child = BTreeNode(child_path, os.path.isdir(child_path))
            if len(child.keys) >= 2 * minimum_degree - 1:
                mid_key, sibling_path = child.split()
                self.keys.insert(index, mid_key)
                self.children.insert(index + 1, sibling_path)
                if key > mid_key:
                    index += 1
                    child_path = sibling_path
                    child = BTreeNode(child_path, os.path.isdir(child_path))
            child.insert_non_full(key, value, minimum_degree)

    def _save_record(self, key, value):
        record = {"keys": key, "values": value}
        filename = "_".join(map(str, key)) + ".json"
        file_path = os.path.join(self.path, filename)
        with open(file_path, "w") as f:
            json.dump(record, f, ensure_ascii=False, indent=4)
        return file_path

    def clean_empty_folders(self):
        if not os.listdir(self.path):
            if os.path.exists(self.path):
                shutil.rmtree(self.path)

class BTree:
    def __init__(self, db_path, template):
        self.db_path = db_path
        self.template = template
        self.root = None
        self.minimum_degree = 1
        if os.path.exists(os.path.join(self.db_path, "DBInfo.json")):
            self._load_tree()
        else:
            self._initialize_tree()

    def _initialize_tree(self):
        os.makedirs(self.db_path, exist_ok=True)
        db_info = {
            "template": self.template
        }
        with open(os.path.join(self.db_path, "DBInfo.json"), "w") as file:
            json.dump(db_info, file, ensure_ascii=False, indent=4)
        root_path = os.path.join(self.db_path, "Root")
        os.makedirs(root_path, exist_ok=True)
        self.root = BTreeNode(root_path, is_leaf=True)
        self.root._save_node()

    def _load_tree(self):
        root_path = os.path.join(self.db_path, "Root")
        self.root = BTreeNode(root_path, is_leaf=os.path.isdir(root_path))

    def insert(self, record):
        key = tuple(record["keys"][k] for k in self.template["keys"].keys())
        value = {k: record["values"][k] for k in self.template["values"].keys()}
        if len(self.root.keys) >= 2 * self.minimum_degree - 1:
            new_root_path = os.path.join(self.db_path, "RootSplit")
            new_root = BTreeNode(new_root_path, is_leaf=False)
            new_root.keys = []
            new_root.children = [self.root.path]
            mid_key, sibling_path = self.root.split()
            new_root.keys.append(mid_key)
            new_root.children.append(sibling_path)
            self.root = new_root
            self.root._save_node()
        self.root.insert_non_full(key, value, self.minimum_degree)

    def find(self, keys):
        def _find_in_node(node, keys):
            if node.is_leaf:
                for key_file in node.keys:
                    with open(key_file, "r") as f:
                        record = json.load(f)
                        if tuple(record["keys"]) == keys:
                            return record["values"]
                return None
            else:
                index = 0
                while index < len(node.keys) and keys > node.keys[index]:
                    index += 1
                child_path = node.children[index]
                child = BTreeNode(child_path, os.path.isdir(child_path))
                return _find_in_node(child, keys)
        return _find_in_node(self.root, keys)

    def all_records(self):
        def _traverse_in_node(node):
            if node.is_leaf:
                records = []
                for key_file in node.keys:
                    with open(key_file, "r") as f:
                        record = json.load(f)
                        records.append(record)
                return records
            else:
                records = []
                for child_path in node.children:
                    child = BTreeNode(child_path, os.path.isdir(child_path))
                    records.extend(_traverse_in_node(child))
                return records
        return _traverse_in_node(self.root)
