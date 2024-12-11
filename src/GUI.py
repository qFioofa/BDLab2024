import os
import json
import shutil
import openpyxl
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage, ttk
from DataBaseHandler import DataBaseHandler
from dbInfo import (
    DATA_TEMPLATES
)

from GUIstyle import *


class DatabaseGUI:
    def __init__(self, root):
        self.root = root
        self.selected_folder = None

        try:
            icon = PhotoImage(file='./assets/icon.png')
            self.root.iconphoto(False, icon)
        except Exception as e:
            print(f"Error loading icon: {e}")

        self.main_screen()

    def main_screen(self):
        self.clear_screen()
        
        self.root.geometry(GUI_WELCOME_RESOLUTION)
        self.current_screen = "main"
        self.root.title("Database Manager")

        title_label = tk.Label(self.root, text="Main Screen", font=GUI_DB_TITLE)
        title_label.pack(pady=20)

        create_button = tk.Button(self.root, text="Create", font=GUI_DB_TITLE, command=self.create_section)
        create_button.pack(pady=10)

        open_button = tk.Button(self.root, text="Open",font=GUI_DB_TITLE,command=self.open_database)
        open_button.pack(pady=10)

        backup_button = tk.Button(self.root, text="Backup", font=GUI_DB_SUB_TITLE, command=self.backup_section)
        backup_button.pack(pady=10)

        delete_button = tk.Button(self.root, text="Delete", font=GUI_DB_SUB_TITLE, command=self.delete_section)
        delete_button.pack(pady=10)

    def create_section(self):
        self.clear_screen()
        tk.Label(self.root, text="Data Base Info", font=GUI_DB_TITLE).pack(pady=5)

        tk.Label(self.root, text="Database Name:", font=GUI_DB_SUB_TITLE).pack(pady=5)
        self.db_name_entry = tk.Entry(self.root)
        self.db_name_entry.pack(pady=5)

        tk.Label(self.root, text="Implementation:", font=GUI_DB_SUB_TITLE).pack(pady=5)
        self.implementation_option = tk.StringVar(value="B-Tree")
        tk.Checkbutton(self.root, text="B-Tree", variable=self.implementation_option,
                    onvalue="B-Tree", offvalue="", font=GUI_DB_SUB_TITLE).pack(pady=10)
        tk.Checkbutton(self.root, text="Hash-table", variable=self.implementation_option,
                    onvalue="Hash-table", offvalue="", font=GUI_DB_SUB_TITLE).pack()

        tk.Label(self.root, text="Data Templates:", font=GUI_DB_SUB_TITLE).pack(pady=5)
        self.template_option = tk.StringVar(value="Default")
        template_list = DATA_TEMPLATES.keys()

        self.template_dropdown = tk.OptionMenu(self.root, self.template_option, *template_list)
        self.template_dropdown.config(font=GUI_DB_TEXT)
        self.template_dropdown.pack(pady=10)

        tk.Label(self.root, text="Folder:", font=GUI_DB_SUB_TITLE).pack(pady=5)
        self.folder_label = tk.Label(self.root, text="No folder chosen", font=GUI_DB_TEXT)
        self.folder_label.pack(pady=10)

        tk.Button(self.root, text="Choose Folder", font=GUI_DB_TEXT, command=self.choose_folder).pack()
        tk.Button(self.root, text="Create", font=GUI_DB_TEXT, command=self.create_db_folder).pack(pady=10)

        back_button = tk.Button(self.root, text="Back", font=GUI_DB_SUB_TITLE, command=self.main_screen)
        back_button.pack(pady=30)

    def create_db_folder(self):
        self._create_db_folder(self.db_name_entry.get(),self.implementation_option.get().strip(), self.template_option.get().strip(), os.path.join(self.selected_folder, self.db_name_entry.get()))

    def _create_db_folder(self, db_name, implementation, template, db_path):
        if not self.selected_folder:
            messagebox.showerror("Error", "Please choose a folder first.")
            return

        if not db_name or not implementation or not template:
            messagebox.showerror("Error", "Please provide:\nDatabase name\nImplementation\nData template.")
            return
        if not os.path.exists(db_path):
            os.makedirs(db_path)
            db_info = {
                "name": db_name,
                "implementation": implementation,
                "template": template
            }
            with open(os.path.join(db_path, "BDInfo.json"), 'w') as json_file:
                json.dump(db_info, json_file, ensure_ascii=False, indent=4)
            messagebox.showinfo("Success", "Database created successfully.\nBack to main menu and open the database.")
        else:
            messagebox.showerror("Error", "A database with this name already exists.")

    
    def open_database(self):
        folder = filedialog.askdirectory()
        if not self.valid_folder(folder): return

        self.selected_folder = folder
        db_info_path = os.path.join(folder, "BDInfo.json")
        with open(db_info_path) as json_file:
            db_info = json.load(json_file)
        self.bd_info = db_info
        self.__init_database_handler()
        self.__init_base()

    def __init_database_handler(self):
        if(not self.bd_info): messagebox.showerror("Error", "Info about data base was not found")

        self.__database_handler = DataBaseHandler()
        try:
            self.__database_handler.set_data_template(self.bd_info["template"])
            self.__database_handler.set_implementation(self.bd_info["implementation"], self.selected_folder)
        except Exception as e:
            print(e)    

    def delete_section(self):
        self.clear_screen()
        title_label = tk.Label(self.root, text="Delete Folder", font=GUI_DB_TITLE)
        title_label.pack(pady=20)

        self.folder_label = tk.Label(self.root, text="No folder selected", font=GUI_DB_SUB_TITLE)
        self.folder_label.pack(pady=10)

        choose_folder_button = tk.Button(self.root, text="Choose Folder", font=GUI_DB_SUB_TITLE, command=self.choose_folder)
        choose_folder_button.pack(pady=10)

        delete_button = tk.Button(self.root, text="Delete", font=GUI_DB_SUB_TITLE, command=self.delete_folder)
        delete_button.pack(pady=10)

        back_button = tk.Button(self.root, text="Back", font=GUI_DB_SUB_TITLE, command=self.main_screen)
        back_button.pack(pady=10)

    def choose_folder(self):
        self.selected_folder = filedialog.askdirectory()
        if self.selected_folder:
            self.folder_label.config(text=f"Selected Folder: {self.selected_folder}")
        else:
            self.folder_label.config(text="No folder selected")

    def delete_folder(self):
        if not self.valid_folder(self.selected_folder): return

        try:
            shutil.rmtree(self.selected_folder)
            messagebox.showinfo("Success", "Folder deleted successfully.")
            self.selected_folder = None
            self.folder_label.config(text="No folder selected")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def backup_section(self):
        self.clear_screen()
        self.root.title("Backup")
        tk.Label(self.root, text="Open Backup", font=GUI_DB_TITLE).pack(pady=10)
        self.backup_file_label = tk.Label(self.root, text="No backup file chosen", font=GUI_DB_TEXT)

        self.backup_file_label.pack(pady=5)
        self.extract_folder_label = tk.Label(self.root, text="No extract folder chosen", font=GUI_DB_TEXT)

        self.extract_folder_label.pack(pady=5)
        tk.Button(self.root, text="Choose Backup File", command=self.choose_backup_file).pack(pady=5)
        tk.Button(self.root, text="Choose Extract Folder", command=self.open_extract_folder).pack(pady=5)
        tk.Button(self.root, text="Extract Backup", command=self.open_backup).pack(pady=10)

        back_button = tk.Button(self.root, text="Back", font=GUI_DB_SUB_TITLE, command=self.main_screen)
        back_button.pack(pady=30)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def valid_folder(self, folder):
        """Validate if the given folder contains a valid database."""
        if not folder:
            messagebox.showerror("Error", "Please choose a folder first.")
            return False

        db_info_path = os.path.join(folder, "BDInfo.json")
        if not os.path.isfile(db_info_path):
            messagebox.showerror("Error", "This folder does not contain a valid database.")
            return False

        try:
            with open(db_info_path, 'r') as json_file:
                db_info = json.load(json_file)

            required_fields = ["name", "implementation", "template"]
            if not all(db_info.get(field) for field in required_fields):
                messagebox.showerror("Error", "This folder does not contain a valid database.")
                return False

            return True
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while validating the folder: {e}")
            return False


##############################################################

    def __init_base(self):
        self.clear_screen()
        self.root.title("Database GUI")
        self.root.geometry(GUI_MAIN_RESOLUTION)

        self.__init_left_panel()
        self.__init_main_screen()
        self.__init_operation_frames()

    def __init_left_panel(self):
        self.left_panel = tk.Frame(self.root)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)

        tk.Button(self.left_panel, text="Info", font=GUI_DB_SUB_TITLE, command=lambda: self.prepare_operation('info')).pack(fill=tk.X)
        tk.Button(self.left_panel, text="Insert", font=GUI_DB_SUB_TITLE, command=lambda: self.prepare_operation('insert')).pack(fill=tk.X)
        tk.Button(self.left_panel, text="Find",font=GUI_DB_SUB_TITLE, command=lambda: self.prepare_operation('find')).pack(fill=tk.X)
        tk.Button(self.left_panel, text="Delete",font=GUI_DB_SUB_TITLE, command=lambda: self.prepare_operation('delete')).pack(fill=tk.X)
        tk.Button(self.left_panel, text="Backup",font=GUI_DB_SUB_TITLE, command=lambda: self.prepare_operation('backup')).pack(fill=tk.X)
        tk.Button(self.left_panel, text="Export",font=GUI_DB_SUB_TITLE, command=lambda: self.prepare_operation('export')).pack(fill=tk.X)
        tk.Button(self.left_panel, text="All records",font=GUI_DB_SUB_TITLE, command=self.all_records).pack(fill=tk.X)
        tk.Button(self.left_panel, text="Back", font=GUI_DB_SUB_TITLE, command=self.main_screen).pack(fill=tk.X)

    def __init_main_screen(self):
        self.main_screen = tk.Frame(self.root)
        self.main_screen.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.main_label = tk.Label(self.main_screen, text="Welcome to the Database GUI", font=GUI_DB_TITLE)
        self.main_label.pack(pady=10)

        self.key_entry = tk.Entry(self.main_screen)
        self.value_entry = tk.Entry(self.main_screen)

        self.info_label = tk.Label(self.main_screen, text="")
        self.info_label.pack(pady=10)

        self.operation_buttons_frame = tk.Frame(self.main_screen)
        self.operation_buttons_frame.pack(pady=20)

    def __init_operation_frames(self):
        self.info_frame = tk.Frame(self.main_screen)
        self.insert_frame = tk.Frame(self.main_screen)
        self.find_frame = tk.Frame(self.main_screen)
        self.delete_frame = tk.Frame(self.main_screen)
        self.backup_frame = tk.Frame(self.main_screen)
        self.export_frame = tk.Frame(self.main_screen)

        self.setup_info_frame()
        self.setup_insert_frame()
        self.setup_find_frame()
        self.setup_delete_frame()
        self.setup_backup_frame()
        self.setup_export_frame()

    def setup_info_frame(self):
        tk.Label(self.info_frame, text="Database Info", font=GUI_DB_TITLE).pack(pady=10)
        tk.Label(self.info_frame, text=f"Database Name: {self.bd_info['name']}\nImplementation: {self.bd_info['implementation']}\nData template: {self.bd_info["template"]}", font=GUI_DB_SUB_TITLE).pack(pady=10)

    def setup_insert_frame(self):
        tk.Label(self.insert_frame, text="Insert Key-Value", font=GUI_DB_TITLE).pack(pady=10)

        template = self.__database_handler.get_template()
        keys = template["keys"]
        values = template["values"]

        keys_frame = tk.Frame(self.insert_frame)
        keys_frame.pack(pady=10, fill=tk.X)
        tk.Label(keys_frame, text="Keys", font=GUI_DB_SUB_TITLE).grid(row=0, column=0, columnspan=2, pady=5)

        self.key_entries = {}
        row = 1
        for key, key_type in keys.items():
            tk.Label(keys_frame, text=f"{key} ({key_type}):", font=GUI_DB_TEXT).grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
            entry = tk.Entry(keys_frame)
            entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
            self.key_entries[key] = entry
            row += 1

        values_frame = tk.Frame(self.insert_frame)
        values_frame.pack(pady=10, fill=tk.X)
        tk.Label(values_frame, text="Values", font=GUI_DB_SUB_TITLE).grid(row=0, column=0, columnspan=2, pady=5)

        self.value_entries = {}
        row = 1
        for value, value_type in values.items():
            tk.Label(values_frame, text=f"{value} ({value_type}):", font=GUI_DB_TEXT).grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
            entry = tk.Entry(values_frame)
            entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
            self.value_entries[value] = entry
            row += 1

        tk.Button(self.insert_frame, text="Submit", font=GUI_DB_SUB_TITLE, command=self.insert_key_value).pack(pady=10)

    def setup_find_frame(self):
        tk.Label(self.find_frame, text="Find", font=GUI_DB_TITLE).pack(pady=10)

        template = self.__database_handler.get_template()
        keys = template["keys"]
        values = template["values"]

        keys_frame = tk.Frame(self.find_frame)
        keys_frame.pack(pady=10, fill=tk.X)
        tk.Label(keys_frame, text="Find by Key", font=GUI_DB_SUB_TITLE).grid(row=0, column=0, columnspan=2, pady=5)

        self.find_key_entries = {}
        row = 1
        for key, key_type in keys.items():
            tk.Label(keys_frame, text=f"{key} ({key_type}):", font=GUI_DB_TEXT).grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
            entry = tk.Entry(keys_frame)
            entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
            self.find_key_entries[key] = entry
            row += 1

        values_frame = tk.Frame(self.find_frame)
        values_frame.pack(pady=10, fill=tk.X)
        tk.Label(values_frame, text="Find by Value", font=GUI_DB_SUB_TITLE).grid(row=0, column=0, columnspan=2, pady=5)

        self.find_value_entries = {}
        row = 1
        for value, value_type in values.items():
            tk.Label(values_frame, text=f"{value} ({value_type}):", font=GUI_DB_TEXT).grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
            entry = tk.Entry(values_frame)
            entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
            self.find_value_entries[value] = entry
            row += 1

        buttons_frame = tk.Frame(self.find_frame)
        buttons_frame.pack(pady=20)

        tk.Button(buttons_frame, text="Find by Key", font=GUI_DB_SUB_TITLE, command=self.find_by_key).grid(row=0, column=0, padx=10)
        tk.Button(buttons_frame, text="Find by Value", font=GUI_DB_SUB_TITLE, command=self.find_by_value).grid(row=0, column=1, padx=10)


    def setup_delete_frame(self):
        tk.Label(self.delete_frame, text="Delete", font=GUI_DB_TITLE).pack(pady=10)

        template = self.__database_handler.get_template()
        keys = template["keys"]
        values = template["values"]

        keys_frame = tk.Frame(self.delete_frame)
        keys_frame.pack(pady=10, fill=tk.X)
        tk.Label(keys_frame, text="Delete by Key", font=GUI_DB_SUB_TITLE).grid(row=0, column=0, columnspan=2, pady=5)

        self.delete_key_entries = {}
        row = 1
        for key, key_type in keys.items():
            tk.Label(keys_frame, text=f"{key} ({key_type}):", font=GUI_DB_TEXT).grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
            entry = tk.Entry(keys_frame)
            entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
            self.delete_key_entries[key] = entry
            row += 1

        values_frame = tk.Frame(self.delete_frame)
        values_frame.pack(pady=10, fill=tk.X)
        tk.Label(values_frame, text="Delete by Value", font=GUI_DB_SUB_TITLE).grid(row=0, column=0, columnspan=2, pady=5)

        self.delete_value_entries = {}
        row = 1
        for value, value_type in values.items():
            tk.Label(values_frame, text=f"{value} ({value_type}):", font=GUI_DB_TEXT).grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
            entry = tk.Entry(values_frame)
            entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
            self.delete_value_entries[value] = entry
            row += 1

        buttons_frame = tk.Frame(self.delete_frame)
        buttons_frame.pack(pady=20)

        tk.Button(buttons_frame, text="Delete by Key", font=GUI_DB_SUB_TITLE, command=self.delete_by_key).grid(row=0, column=0, padx=10)
        tk.Button(buttons_frame, text="Delete by Value", font=GUI_DB_SUB_TITLE, command=self.delete_by_value).grid(row=0, column=1, padx=10)

    def setup_backup_frame(self):
        tk.Label(self.backup_frame, text="Make Backup", font=GUI_DB_TITLE).pack(pady=10)
        self.backup_folder_label = tk.Label(self.backup_frame, text="No folder chosen", font=GUI_DB_TEXT)
        self.backup_folder_label.pack(pady=5)
        tk.Button(self.backup_frame, text="Choose Folder", command=self.choose_backup_folder).pack(pady=5)
        tk.Button(self.backup_frame, text="Make backup", command=self.make_backup).pack(pady=5)

        tk.Label(self.backup_frame, text="Open Backup", font=GUI_DB_TITLE).pack(pady=10)
        self.backup_file_label = tk.Label(self.backup_frame, text="No backup file chosen", font=GUI_DB_TEXT)
        self.backup_file_label.pack(pady=5)
        self.extract_folder_label = tk.Label(self.backup_frame, text="No extract folder chosen", font=GUI_DB_TEXT)
        self.extract_folder_label.pack(pady=5)
        tk.Button(self.backup_frame, text="Choose File", command=self.choose_backup_file).pack(pady=5)
        tk.Button(self.backup_frame, text="Choose extract Folder", command=self.open_extract_folder).pack(pady=5)
        tk.Button(self.backup_frame, text="Extract", command=self.open_backup).pack(pady=5)

    def setup_export_frame(self):
        tk.Label(self.export_frame, text="Export", font=GUI_DB_TITLE).pack(pady=10)
        self.export_folder_label = tk.Label(self.export_frame, text="No folder chosen", font=GUI_DB_TEXT)
        self.export_folder_label.pack(pady=5)
        tk.Button(self.export_frame, text="Choose Folder", command=self.choose_export_folder).pack(pady=5)

        tk.Button(self.export_frame, text="Export", command=self.execute_export).pack(pady=5)

    def clear_main_screen(self):
        for widget in self.main_screen.winfo_children():
            widget.pack_forget()

    def prepare_operation(self, operation):
        self.current_operation = operation
        self.clear_main_screen()

        self.info_frame.pack_forget()
        self.insert_frame.pack_forget()
        self.find_frame.pack_forget()
        self.delete_frame.pack_forget()
        self.backup_frame.pack_forget()
        self.export_frame.pack_forget()

        match operation:
            case 'info':
                self.info_frame.pack(fill=tk.BOTH, expand=True)
            case 'insert':
                self.insert_frame.pack(fill=tk.BOTH, expand=True)
            case 'find':
                self.find_frame.pack(fill=tk.BOTH, expand=True)
            case 'delete':
                self.delete_frame.pack(fill=tk.BOTH, expand=True)
            case 'backup':
                self.backup_frame.pack(fill=tk.BOTH, expand=True)
            case 'export':
                self.export_frame.pack(fill=tk.BOTH, expand=True)

    def insert_key_value(self):
        key_values = {}
        for key, entry in self.key_entries.items():
            if entry.get():
                key_values[key] = entry.get()

        value_values = {}
        for value, entry in self.value_entries.items():
            if entry.get():
                value_values[value] = entry.get()

        if not key_values or not value_values:
            messagebox.showerror("Error", "Please fill in all key and value fields.")
            return

        try:
            data = {}
            data["keys"] = key_values
            data["values"] = value_values
            self.__database_handler.insert_data(data)
            messagebox.showinfo("Success", "Data inserted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to insert data: {e}")

    def display_results(self, results, query_type):
        if not results:
            messagebox.showinfo("Result", f"No data found for the given {query_type}.")
            return

        result_window = tk.Toplevel(self.root)
        result_window.title("Search Results")
        result_window.geometry(GUI_FIND_DELETE_RESOLUTION)

        canvas = tk.Canvas(result_window)
        scrollbar = ttk.Scrollbar(result_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for idx, record in enumerate(results):
            record_frame = ttk.LabelFrame(scrollable_frame, text=f"Record {idx + 1}", padding=(10, 5))
            record_frame.pack(fill="x", pady=5, padx=10)

            entries = {}

            row = 0
            for key, value in record["keys"].items():
                tk.Label(record_frame, text=f"Key: {key}", font=("Arial", 12)).grid(row=row, column=0, sticky="w", padx=5)
                entry = tk.Entry(record_frame, font=("Arial", 12), width=30)
                entry.insert(0, str(value))
                entry.grid(row=row, column=1, padx=5)
                entry.config(state="disabled")
                entries[f"keys.{key}"] = entry
                row += 1

            for key, value in record["values"].items():
                tk.Label(record_frame, text=f"Value: {key}", font=("Arial", 12)).grid(row=row, column=0, sticky="w", padx=5)
                entry = tk.Entry(record_frame, font=("Arial", 12), width=30)
                entry.insert(0, str(value))
                entry.grid(row=row, column=1, padx=5)
                entries[f"values.{key}"] = entry
                row += 1

            edit_button = ttk.Button(record_frame, text="Edit", command=lambda e=entries: self.toggle_edit(e, True))
            edit_button.grid(row=row, column=0, pady=5, padx=5)

            cancel_button = ttk.Button(record_frame, text="Cancel", command=lambda e=entries: self.toggle_edit(e, False))
            cancel_button.grid(row=row, column=2, pady=5, padx=5)

            submit_button = ttk.Button(record_frame, text="Submit", command=lambda e=entries, r=record: self.submit_edit(e, r))
            submit_button.grid(row=row, column=1, pady=5, padx=5)

            self.toggle_edit(entries, False)


    def toggle_edit(self, entries, enable):
        state = "normal" if enable else "disabled"
    
        for key, entry in entries.items():
            section, field = key.split(".")
            
            if section == "values":
                entry.config(state=state)

    def submit_edit(self, entries, record):
        updated_data = {"keys": {}, "values": {}}
        try:
            for key, entry in entries.items():
                section, field = key.split(".")
                updated_data[section][field] = entry.get()

            self.__database_handler.edit(record, updated_data)
            messagebox.showinfo("Success", "Record updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update record: {e}")

    def find_by_key(self):
        query = {}
        for key, entry in self.find_key_entries.items():
            if entry.get():
                query[key] = entry.get()

        if not query:
            messagebox.showerror("Error", "Please fill in at least one key field.")
            return

        try:
            results = self.__database_handler.find_by_key(query)
            self.display_results(results, "key")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to find by key: {e}")

    def find_by_value(self):
        query = {}
        for value, entry in self.find_value_entries.items():
            if entry.get():
                query[value] = entry.get()

        if not query:
            messagebox.showerror("Error", "Please fill in at least one value field.")
            return

        try:
            results = self.__database_handler.find_by_value(query)
            self.display_results(results, "value")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to find by value: {e}")

    def display_deleted_records(self, deleted_records, query_type):
        if not deleted_records:
            messagebox.showinfo("Result", f"No records were deleted for the given {query_type}.")
            return

        deleted_window = tk.Toplevel(self.root)
        deleted_window.title("Deleted Records")
        deleted_window.geometry(GUI_FIND_DELETE_RESOLUTION)

        canvas = tk.Canvas(deleted_window)
        scrollbar = ttk.Scrollbar(deleted_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for idx, record in enumerate(deleted_records):
            record_frame = ttk.LabelFrame(scrollable_frame, text=f"Deleted Record {idx + 1}", padding=(10, 5))
            record_frame.pack(fill="x", pady=5, padx=10)

            for row, (key, value) in enumerate(record["keys"].items()):
                tk.Label(record_frame, text=f"Key: {key} - {value}", font=("Arial", 12)).grid(row=row, column=0, sticky="w", padx=5)

            for row, (key, value) in enumerate(record["values"].items(), start=len(record["keys"])):
                tk.Label(record_frame, text=f"Value: {key} - {value}", font=("Arial", 12)).grid(row=row, column=0, sticky="w", padx=5)


    def delete_by_key(self):
        query = {}
        for key, entry in self.delete_key_entries.items():
            if entry.get():
                query[key] = entry.get()

        if not query:
            messagebox.showerror("Error", "Please fill in at least one key field.")
            return

        try:
            deleted_records = self.__database_handler.delete_by_key(query)
            self.display_deleted_records(deleted_records, "key")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete by key: {e}")

    def delete_by_value(self):
        query = {}
        for value, entry in self.delete_value_entries.items():
            if entry.get():
                query[value] = entry.get()

        if not query:
            messagebox.showerror("Error", "Please fill in at least one value field.")
            return

        try:
            deleted_records = self.__database_handler.delete_by_value(query)
            self.display_deleted_records(deleted_records, "value")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete by value: {e}")

    def all_records(self):
        all_records = self.__database_handler.all_records()
        if not all_records:
            messagebox.showinfo("Result", "No records found")
            return

        total_records = len(all_records)
        records_window = tk.Toplevel(self.root)
        records_window.title(f"All Records - Total: {total_records}")
        records_window.geometry(GUI_FIND_DELETE_RESOLUTION)

        canvas = tk.Canvas(records_window)
        scrollbar = ttk.Scrollbar(records_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        title_frame = ttk.Frame(scrollable_frame)
        title_frame.pack(fill="x", pady=10, padx=10)
        tk.Label(title_frame, text=f"Total Records: {total_records}", font=("Arial", 16, "bold")).pack()

        for idx, record in enumerate(all_records):
            record_frame = ttk.LabelFrame(scrollable_frame, text=f"Record {idx + 1}", padding=(10, 5))
            record_frame.pack(fill="x", pady=5, padx=10)

            for row, (key, value) in enumerate(record["keys"].items()):
                tk.Label(record_frame, text=f"Key: {key} - {value}", font=("Arial", 12)).grid(row=row, column=0, sticky="w", padx=5)

            for row, (key, value) in enumerate(record["values"].items(), start=len(record["keys"])):
                tk.Label(record_frame, text=f"Value: {key} - {value}", font=("Arial", 12)).grid(row=row, column=0, sticky="w", padx=5)

    def make_backup(self):
        records = self.__database_handler.all_records()
        if not records:
            messagebox.showerror("Error", "No data to backup")
            return

        template = self.__database_handler.get_template()
        if not template:
            messagebox.showerror("Error", "Template not found")
            return

        db_info = {
            "name": self.bd_info['name'],
            "template": template,
            "implementation": self.bd_info['implementation']
        }

        backup_data = {
            "db_info": db_info,
            "records": records
        }

        backup_folder = self.backup_folder_label.cget("text")
        if backup_folder == "No folder chosen":
            messagebox.showerror("Error", "No folder selected for backup")
            return

        backup_file = os.path.join(backup_folder, f"{db_info['name']}_backup.json")
        
        try:
            with open(backup_file, 'w', encoding='utf-8') as file:
                json.dump(backup_data, file, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success", f"Backup saved to {backup_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save backup: {e}")

    def open_backup(self):
        backup_file = self.backup_file_label.cget("text")
        if not os.path.exists(backup_file):
            messagebox.showerror("Error", "Backup file does not exist")
            return

        try:
            with open(backup_file, 'r', encoding='utf-8') as file:
                backup_data = json.load(file)

            db_info = backup_data.get("db_info")
            records = backup_data.get("records")

            if not db_info or not records:
                messagebox.showerror("Error", "Backup file is corrupted or incomplete")
                return

            self._create_db_folder(db_info['name'], db_info['implementation'], db_info['template'], self.extract_folder_label.cget("text"))
            return
            for record in records:
                self.__database_handler.insert_data(record)

            messagebox.showinfo("Success", "Database restored from backup")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore backup: {e}")

    def choose_backup_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.backup_folder_label.config(text=folder)

    def choose_backup_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.backup_file_label.config(text=file)

    def open_extract_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.extract_folder_label.config(text=folder)

    def choose_export_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.export_folder_label.config(text=folder)

    def execute_export(self):
        records = self.__database_handler.all_records()
        if not records:
            messagebox.showinfo("Result", "No records found")
            return

        template = self.__database_handler.get_template()
        if not template:
            messagebox.showinfo("Result", "No template found")
            return
        db_name = self.bd_info['name']
        file_path = os.path.join(self.export_folder_label.cget("text"), f"{db_name}.xlsx")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = db_name

        headers = list(template['keys'].keys()) + list(template['values'].keys())
        ws.append(headers)

        for record in records:
            row = []
            row += [record['keys'].get(i,"") for i in template['keys'].keys()]
            row += [record['values'].get(i,"") for i in template['values'].keys()]
            ws.append(row)

        wb.save(file_path)
        messagebox.showinfo("Success", f"Exported data saved to {file_path}")