class BTreeNode:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []  # Список ключей
        self.children = []  # Список потомков


class BTree:
    def __init__(self, template, t=2):
        self.root = BTreeNode(True)
        self.t = t
        self.template = template
    
    @staticmethod
    def compare_dicts(dict1, dict2, partial=False):
        """Сравнение двух словарей. Если partial=True, сравнение только по общим ключам."""
        if partial:
            for key, value in dict1.items():
                if key in dict2 and dict2[key] != value:
                    return False
            return True
        for key in sorted(set(dict1.keys()).union(dict2.keys())):
            val1 = dict1.get(key)
            val2 = dict2.get(key)
            if val1 is None:
                return -1
            if val2 is None:
                return 1
            if val1 < val2:
                return -1
            if val1 > val2:
                return 1
        return 0

    def insert(self, data):
        if self.find(data["keys"]):
            raise ValueError("Record already exists with thore keys")
        root = self.root
        if len(root.keys) == (2 * self.t - 1):
            new_node = BTreeNode(False)
            new_node.children.append(self.root)
            self.split_child(new_node, 0)
            self.root = new_node
        self._insert_non_full(self.root, data)

    def split_child(self, parent, i):
        t = self.t
        full_child = parent.children[i]
        new_node = BTreeNode(full_child.is_leaf)
        parent.children.insert(i + 1, new_node)
        parent.keys.insert(i, full_child.keys[t - 1])

        new_node.keys = full_child.keys[t:]
        full_child.keys = full_child.keys[:t - 1]

        if not full_child.is_leaf:
            new_node.children = full_child.children[t:]
            full_child.children = full_child.children[:t]

    def _insert_non_full(self, node, data):
        key = data["keys"]
        i = len(node.keys) - 1
        if node.is_leaf:
            while i >= 0 and self.compare_dicts(key, node.keys[i]["keys"]) < 0:
                i -= 1
            node.keys.insert(i + 1, data)
        else:
            while i >= 0 and self.compare_dicts(key, node.keys[i]["keys"]) < 0:
                i -= 1
            i += 1
            child = node.children[i]
            if len(child.keys) == (2 * self.t - 1):
                self.split_child(node, i)
                if self.compare_dicts(key, node.keys[i]["keys"]) > 0:
                    i += 1
            self._insert_non_full(node.children[i], data)

    def find(self, key_query):
        """Поиск данных по ключу."""
        results = []
        self._find(self.root, key_query, results)
        return results

    def _find(self, node, key_query, results):
        i = 0
        while i < len(node.keys) and self.compare_dicts(key_query, node.keys[i]["keys"]) > 0:
            i += 1
        if i < len(node.keys) and self.compare_dicts(key_query, node.keys[i]["keys"]) == 0:
            results.append(node.keys[i])
        if not node.is_leaf:
            if i < len(node.keys) and self.compare_dicts(key_query, node.keys[i]["keys"]) <= 0:
                self._find(node.children[i], key_query, results)
            if i == len(node.keys) or self.compare_dicts(key_query, node.keys[i]["keys"]) > 0:
                self._find(node.children[i + 1], key_query, results)

    def find_by_value(self, value_query):
        """Поиск данных по значению."""
        results = []
        self._find_by_value(self.root, value_query, results)
        return results

    def _find_by_value(self, node, value_query, results):
        for key in node.keys:
            if self.compare_dicts(value_query, key["values"], partial=True):
                results.append(key)
        if not node.is_leaf:
            for child in node.children:
                self._find_by_value(child, value_query, results)

    def delete(self, key_query):
        """Удаление записей по ключу."""
        results = []
        self._delete(self.root, key_query, results)
        return results

    def _delete(self, node, key_query, results):
        i = 0
        while i < len(node.keys) and self.compare_dicts(key_query, node.keys[i]["keys"]) > 0:
            i += 1
        if i < len(node.keys) and self.compare_dicts(key_query, node.keys[i]["keys"]) == 0:
            results.append(node.keys.pop(i))
        if not node.is_leaf:
            if i < len(node.keys) and self.compare_dicts(key_query, node.keys[i]["keys"]) <= 0:
                self._delete(node.children[i], key_query, results)
            if i == len(node.keys) or self.compare_dicts(key_query, node.keys[i]["keys"]) > 0:
                self._delete(node.children[i + 1], key_query, results)

    def delete_by_value(self, value_query):
        """Удаление записей по значению."""
        results = []
        self._delete_by_value(self.root, value_query, results)
        return results

    def _delete_by_value(self, node, value_query, results):
        i = 0
        while i < len(node.keys):
            if self.compare_dicts(value_query, node.keys[i]["values"], partial=True):
                results.append(node.keys.pop(i))
            else:
                i += 1
        if not node.is_leaf:
            for child in node.children:
                self._delete_by_value(child, value_query, results)

    def all_records(self):
        """Возврат всех записей в дереве."""
        return self._all_records(self.root)

    def _all_records(self, node):
        records = []
        for i in range(len(node.keys)):
            if not node.is_leaf:
                records.extend(self._all_records(node.children[i]))
            records.append(node.keys[i])
        if not node.is_leaf:
            records.extend(self._all_records(node.children[-1]))
        return records

    def edit(self, key_query, new_data):

        deleted = self.delete(key_query["keys"])
        if deleted:
            self.insert(new_data)
            return True
        return False
