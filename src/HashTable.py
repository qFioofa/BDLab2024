class CityHash:
    def __init__(self):
        self.k2 = 0x9ae16a3b2f90404f
        self.k0 = 0xc3a5c85c97cb3127
        self.k1 = 0xb492b66fbe98f273

    def _rotate(self, val, shift):
        return ((val << shift) & 0xFFFFFFFFFFFFFFFF) | (val >> (64 - shift))

    def _finalize_hash(self, hash_value, mul):
        hash_value ^= hash_value >> 33
        hash_value *= mul
        hash_value ^= hash_value >> 29
        hash_value *= mul
        hash_value ^= hash_value >> 32
        return hash_value & 0xFFFFFFFFFFFFFFFF

    def cityhash64(self, s):
        s = s.encode('utf-8') if isinstance(s, str) else s
        length = len(s)
        if length <= 16:
            mul = self.k2 + length * 2
            a = int.from_bytes(s[:8].ljust(8, b'\0'), 'little') + self.k2
            b = int.from_bytes(s[-8:].ljust(8, b'\0'), 'little')
            c = self._rotate(b, 37) * mul + a
            d = (self._rotate(a, 25) + b) * mul
            return self._finalize_hash(c ^ d, mul)
        return 0


class HashTable:
    def __init__(self, template):
        self.template = template
        self.table_size = 1024
        self.hash_table = [None] * self.table_size
        self.hasher = CityHash()

    def _hash_key(self, key):
        composite_key = "_".join(str(key.get(field, "")) for field in self.template["keys"].keys())
        return self.hasher.cityhash64(composite_key) % self.table_size

    def insert(self, record):
        key = record["keys"]
        value = record["values"]

        if self.find(key):
            raise ValueError("Record already exists with thore keys")

        hash_index = self._hash_key(key)
        if not self.hash_table[hash_index]:
            self.hash_table[hash_index] = []

        for item in self.hash_table[hash_index]:
            if item[0] == key:
                item[1] = value
                return
        self.hash_table[hash_index].append([key, value])

    def _matches_partial_key(self, record_key, search_key):
        for field, value in search_key.items():
            if field in record_key and record_key[field] != value:
                return False
        return True

    def find(self, search_key):
        matching_records = []
        for bucket in self.hash_table:
            if bucket:
                for record_key, record_value in bucket:
                    if self._matches_partial_key(record_key, search_key):
                        matching_records.append({"keys": record_key, "values": record_value})
        return matching_records

    def find_by_value(self, search_value):
        matching_records = []
        for bucket in self.hash_table:
            if bucket:
                for record_key, record_value in bucket:
                    if any(
                        record_value.get(field, None) == value
                        for field, value in search_value.items()
                    ):
                        matching_records.append({"keys": record_key, "values": record_value})
        return matching_records

    def delete(self, key):
        hash_index = self._hash_key(key)
        bucket = self.hash_table[hash_index]
        deleted_records = []

        if bucket:
            for i in range(len(bucket) - 1, -1, -1):
                record_key, record_value = bucket[i]
                if record_key == key:
                    deleted_records.append({"keys": record_key, "values": record_value})
                    del bucket[i]

        return deleted_records

    def delete_by_value(self, value):
        deleted_records = []

        for bucket in self.hash_table:
            if bucket:
                for i in range(len(bucket) - 1, -1, -1):
                    record_key, record_value = bucket[i]
                    if all(record_value.get(field, None) == val for field, val in value.items()):
                        deleted_records.append({"keys": record_key, "values": record_value})
                        del bucket[i]

        return deleted_records
    
    def all_records(self):
        records = []
        for bucket in self.hash_table:
            if bucket:
                for record_key, record_value in bucket:
                    records.append({"keys": record_key, "values": record_value})
        return records
    
    def edit(self, record, updated_data):
        key = updated_data["keys"]
        hash_index = self._hash_key(key)

        bucket = self.hash_table[hash_index]
        
        if not bucket:
            raise ValueError(f"Record with key {key} not found.")

        for idx, (record_key, record_value) in enumerate(bucket):
            if record_key == key:
                bucket[idx] = [updated_data["keys"], updated_data["values"]]
                return

        raise ValueError(f"Record with key {key} not found.")
