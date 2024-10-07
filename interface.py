import tkinter as tk
from tkinter import Label, Entry, Button, filedialog
from tkinter.ttk import Combobox
import json
import os

from functions import *


class App:
    def __init__(self):
        self.create_save_file()
        self.init_window()
        self.load_fields()
        

    def on_create_button_click(self):
        video_url = self.url_entry.get()
        file_name = self.file_name_entry.get()
        save_path = self.path_combo.get()
        template_path = self.template_path_combo.get()
        prompts_path = self.prompts_path_combo.get()
        
        self.save_fields()

        generate_note_file(video_url, file_name, save_path, template_path, prompts_path)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.path_combo.set(folder_path)
            self.update_combo_history(self.path_combo, folder_path)
        self.save_fields()
            
    def select_template_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Template File",
            filetypes=(("Text files", "*.md"), ("All files", "*.*"))
        )
        if file_path:
            self.template_path_combo.set(file_path)
            self.update_combo_history(self.template_path_combo, file_path)
        self.save_fields()
    
    def select_prompts_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Prompts File",
            filetypes=(("Text files", "*.md *.txt"), ("All files", "*.*"))
        )
        if file_path:
            self.prompts_path_combo.set(file_path)
            self.update_combo_history(self.prompts_path_combo, file_path)
        self.save_fields()

    def update_combo_history(self, combo, value):
        values = list(combo['values'])
        if value not in values:
            values.insert(0, value)
            combo['values'] = values[:10]  # Keep only the 10 most recent entries

    def create_save_file(self):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define the path to the 'files' folder
        files_folder = os.path.join(script_dir, 'files')
        
        # Check if the 'files' folder exists, create it if it doesn't
        if not os.path.exists(files_folder):
            try:
                os.makedirs(files_folder)
            except OSError as e:
                print(f"Error creating 'files' folder: {e}")
        
        # Construct the path to saved_fields.json
        self.config_file = os.path.join(files_folder, 'saved_fields.json')
        return self.config_file

    def save_fields(self):
        field_data = {
            "video_url": self.url_entry.get(),
            "file_name": self.file_name_entry.get(),
            "save_path": list(self.path_combo['values']),
            "template_path": list(self.template_path_combo['values']),
            "prompts_path": list(self.prompts_path_combo['values'])
        }
        with open(self.config_file, 'w') as f:
            json.dump(field_data, f, indent=4)

    def load_fields(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                field_data = json.load(f)
            self.url_entry.insert(0, field_data.get("video_url", ""))
            self.file_name_entry.insert(0, field_data.get("file_name", ""))
            self.path_combo['values'] = field_data.get("save_path", [])
            self.template_path_combo['values'] = field_data.get("template_path", [])
            self.prompts_path_combo['values'] = field_data.get("prompts_path", [])
            
            # Set the most recent value (first in the list) as the current value
            if self.path_combo['values']:
                self.path_combo.set(self.path_combo['values'][0])
            if self.template_path_combo['values']:
                self.template_path_combo.set(self.template_path_combo['values'][0])
            if self.prompts_path_combo['values']:
                self.prompts_path_combo.set(self.prompts_path_combo['values'][0])

    def init_window(self):
        self.root = tk.Tk()
        self.root.title("YouTube URL to Markdown")
        self.root.geometry("500x500")

        # URL Entry
        url_label = Label(self.root, text="Video url:")
        url_label.pack(pady=5)
        self.url_entry = Entry(self.root, width=50)
        self.url_entry.pack(pady=5)
        
        # File Name Entry
        file_name_label = Label(self.root, text="Note name:")
        file_name_label.pack(pady=5)
        self.file_name_entry = Entry(self.root, width=50)
        self.file_name_entry.pack(pady=5)

        # Saving Path Combo
        path_label = Label(self.root, text="Folder path:")
        path_label.pack(pady=5)
        path_frame = tk.Frame(self.root)
        path_frame.pack(pady=5)
        self.path_combo = Combobox(path_frame, width=35)
        self.path_combo.pack(side=tk.LEFT)
        select_button = Button(path_frame, text="Browse...", command=self.select_folder)
        select_button.pack(side=tk.LEFT)
        
        # Template Path Combo
        template_path_label = Label(self.root, text="Template path:")
        template_path_label.pack(pady=5)
        template_path_frame = tk.Frame(self.root)
        template_path_frame.pack(pady=5)
        self.template_path_combo = Combobox(template_path_frame, width=35)
        self.template_path_combo.pack(side=tk.LEFT)
        select_template_button = Button(template_path_frame, text="Browse...", command=self.select_template_file)
        select_template_button.pack(side=tk.LEFT)
        
        # Prompts Path Combo
        prompts_path_label = Label(self.root, text="Prompts path:")
        prompts_path_label.pack(pady=5)
        prompts_path_frame = tk.Frame(self.root)
        prompts_path_frame.pack(pady=5)
        self.prompts_path_combo = Combobox(prompts_path_frame, width=35)
        self.prompts_path_combo.pack(side=tk.LEFT)
        select_prompts_button = Button(prompts_path_frame, text="Browse...", command=self.select_prompts_file)
        select_prompts_button.pack(side=tk.LEFT)

        # Create button
        create_button = Button(self.root, text="Create", command=self.on_create_button_click)
        create_button.pack(pady=20)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()