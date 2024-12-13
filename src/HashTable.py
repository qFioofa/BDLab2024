import os
import json
from typing import NoReturn


class CityHash:
    def __init__(self) -> None:
        self.k2 = 0x9ae16a3b2f90404f
        self.k0 = 0xc3a5c85c97cb3127
        self.k1 = 0xb492b66fbe98f273

    def _rotate(self, val, shift) -> int:
        return ((val << shift) & 0xFFFFFFFFFFFFFFFF) | (val >> (64 - shift))

    def _finalize_hash(self, hash_value, mul) -> int:
        hash_value ^= hash_value >> 33
        hash_value *= mul
        hash_value ^= hash_value >> 29
        hash_value *= mul
        hash_value ^= hash_value >> 32
        return hash_value & 0xFFFFFFFFFFFFFFFF

    def cityhash64(self, s) -> int:
        s: bytes = s.encode('utf-8') if isinstance(s, str) else s
        length: int = len(s)
        if length <= 16:
            mul: int = self.k2 + length * 2
            a: int = int.from_bytes(s[:8].ljust(8, b'\0'), 'little') + self.k2
            b: int = int.from_bytes(s[-8:].ljust(8, b'\0'), 'little')
            c: int = self._rotate(b, 37) * mul + a
            d: int = (self._rotate(a, 25) + b) * mul
            return self._finalize_hash(c ^ d, mul)
        return 0


class HashTable:
    template : dict[str,dict[str,str]]
    hasher : CityHash
    dir : str
    unreadable_files : set[str] = ("BDInfo.json")
    MAX_CAPASITY: int = 2**10

    def __init__(self, template, dir) ->None:
        self.template = template
        self.hasher = CityHash()
        self.dir = dir

    def _hash_key(self, key: dict[str,str]) -> int:
        composite_key : str = "_".join(str(key.get(field, "")) for field in self.template["keys"].keys())
        return self.hasher.cityhash64(composite_key) % self.MAX_CAPASITY

    def insert(self, record) -> None:
        data_path : str = self.__hash_path(record["keys"])
        if os.path.exists(data_path):
            raise ValueError("Record already exists with thore keys")

        try:
            with open(data_path, 'w', encoding='utf-8') as file:
                json.dump(record, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(e)

    def find(self, search_key) -> list:
        file_path: str = self.__hash_path(search_key)
        if not (os.path.exists(file_path)):
            return []

        return [self.read_info(file_path)]

    def find_by_value(self, search_value)-> list:
        found_records: list = []
        records: list = self.all_records()

        for record in records:
            if self.__values_check(record["values"], search_value):
                file_path: str = self.__hash_path(record["keys"])
                found_records.append(self.read_info(file_path))

        return found_records

    def delete(self, key) -> list:
        file_path : str = self.__hash_path(key)
        if not os.path.exists(file_path):
            raise ValueError("No such record")
        records: list = [self.read_info(file_path)]
        os.remove(file_path)
        return records

    def delete_by_value(self, value) -> list:
        deleted_records: list = []
        records: list = self.all_records()

        for record in records:
            if self.__values_check(record["values"], value):
                file_path: str = self.__hash_path(record["keys"])
                deleted_records.append(self.read_info(file_path))
                os.remove(file_path)

        return deleted_records

    def __values_check(self, values1 : dict[str, str], values2 : dict[str, str]) -> bool:
        v_values1 : list[str] = values1.keys()
        v_values2 : list[str] = values2.keys()
        if len(v_values1) < len(v_values2):
            v_values1, v_values2 = v_values2, v_values1
        if all(values1[key] == values2[key] for key in v_values2): return True
        return False

    def __keys_check(self, keys1: dict[str, str], keys2: dict[str,str])-> bool:
        v_keys1 :list[str] = keys1.keys()
        v_keys2 : list[str] = keys2.keys()
        if any(key not in v_keys2 for key in v_keys1): return False
        if any(keys1[key] != keys2[key] for key in v_keys1): return False
        return True

    def all_records(self) -> list:
        records: list = []
        for record in os.listdir(self.dir):
            if os.path.isfile(os.path.join(self.dir, record)) and record not in self.unreadable_files:
                records.append(self.read_info(self.__get_full_path(record)))

        return records

    def edit(self, record, updated_data) -> NoReturn:
        if not self.__keys_check(record["keys"], updated_data["keys"]):
            raise ValueError("Records doesn't match by keys")

        data_path: str = self.__hash_path(updated_data["keys"])
        try:
            with open(data_path, 'w', encoding='utf-8') as file:
                json.dump(updated_data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(e)

    def __hash_path(self, keys: dict[str,str]) -> str:
        return self.__hashed_file_path(self._hash_key(keys))

    def __hashed_file_path(self,hash : int) -> str:
        return self.__get_full_path(f"{hash}.json")

    def __get_full_path(self, record) -> str:
        return os.path.join(self.dir, record)

    def read_info(self, file_path) -> dict[str,str]:
        info: dict[str, None] = {
            "keys" : None,
            "values" : None
        }
        with open(file_path, 'r', encoding='utf-8') as file:
            data: dict = json.load(file)
            info["keys"] = data.get("keys")
            info["values"] = data.get("values")
        return info
