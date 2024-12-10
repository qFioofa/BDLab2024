
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
        composite_key = "_".join(str(key[field]) for field in self.template["keys"].keys())
        return self.hasher.cityhash64(composite_key) % self.table_size

    def _validate_record(self, record):
        if "keys" not in record or "values" not in record:
            raise ValueError("Record must contain 'keys' and 'values'.")
        for field, field_type in self.template["keys"].items():
            if field not in record["keys"] or not isinstance(record["keys"][field], eval(field_type)):
                raise ValueError(f"Key '{field}' must be of type {field_type}.")

        for field, field_type in self.template["values"].items():
            if field not in record["values"] or not isinstance(record["values"][field], eval(field_type)):
                raise ValueError(f"Value '{field}' must be of type {field_type}.")

    def insert(self, record):
        #self._validate_record(record)
        key = record["keys"]
        value = record["values"]

        hash_index = self._hash_key(key)
        if not self.hash_table[hash_index]:
            self.hash_table[hash_index] = []

        for item in self.hash_table[hash_index]:
            if item[0] == key:
                item[1] = value
                return
        self.hash_table[hash_index].append([key, value])
        for k in self.hash_table:
            if k!=None:
                print(k)

    def find(self, key):
        hash_index = self._hash_key(key)
        bucket = self.hash_table[hash_index]
        for k in self.hash_table:
            if k!=None:
                print(k)
        if bucket:
            for k, v in bucket:
                if k == key:
                    return v
        return None

    def find_by_value(self, value):
        for bucket in self.hash_table:
            if bucket:
                for k, v in bucket:
                    if v == value:
                        return k
        for k in self.hash_table:
            if k!=None:
                print(k)
        return None

    def delete(self, key):
        hash_index = self._hash_key(key)
        bucket = self.hash_table[hash_index]
        for k in self.hash_table:
            if k!=None:
                print(k)
        if bucket:
            for i, (k, v) in enumerate(bucket):
                if k == key:
                    del bucket[i]
                    return True
        return False

    def delete_by_value(self, value):
        for k in self.hash_table:
            if k!=None:
                print(k)
        for bucket in self.hash_table:
            if bucket:
                for i, (k, v) in enumerate(bucket):
                    if v == value:
                        del bucket[i]
                        return True
        return False