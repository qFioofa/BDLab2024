IMPLEMENTATIONS : list[str] = [
    "B-Tree",
    "Hash-table"
]

DATA_TEMPLATES: dict[str, dict[str,str]] = {
    "shop": {
        "keys": {
            "ID": "int",
            "Address": "str"
        },
        "values": {
            "Exporter": "str",
            "Revenue" : "int"
        }
    },
    "library": {
        "keys": {
            "ISBN": "str",
            "ShelfLocation": "str"
        },
        "values": {
            "Title": "str",
            "Author": "str",
            "YearPublished": "int"
        }
    },
    "hospital": {
        "keys": {
            "PatientID": "int",
            "RoomNumber": "str"
        },
        "values": {
            "Name": "str",
            "Age": "int",
            "Diagnosis": "str"
        }
    },
    "warehouse": {
        "keys": {
            "ProductID": "int",
            "Section": "str"
        },
        "values": {
            "ProductName": "str",
            "Quantity": "int",
            "Supplier": "str"
        }
    }
}
