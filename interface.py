import tkinter as tk
from tkinter import Label, Entry, Button, filedialog, Checkbutton, IntVar, Canvas, Scrollbar
from tkinter.ttk import Combobox, Frame
import json
import os

from functions import *


class ScrollableWindow(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        # Create a canvas and scrollbar
        self.canvas = Canvas(self)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        # Configure the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class WrappingCheckbutton(tk.Checkbutton):
    def __init__(self, parent, **kwargs):
        text = kwargs.pop('text', '')
        tk.Checkbutton.__init__(self, parent, **kwargs)
        self.bind('<Configure>', lambda e: self._wrap_text(e, text))

    def _wrap_text(self, event, text):
        width = event.width
        if width > 5:
            self.config(wraplength=width-5)
            self.config(text=text)


class App:
    def __init__(self):
        self.create_save_file()
        self.init_window()
        self.load_fields()
        self.chapters = []
        self.chapter_vars = []
        

    def on_create_button_click(self):
        video_url = self.url_entry.get()
        file_name = self.file_name_entry.get()
        save_path = self.path_combo.get()
        template_path = self.template_path_combo.get()
        prompts_path = self.prompts_path_combo.get()
        selected_chapters = [chapter for chapter, var in zip(self.chapters, self.chapter_vars) if var.get()]
        
        self.save_fields()
    
        generate_note_file(video_url, file_name, save_path, template_path, prompts_path, selected_chapters)


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
                
    
    def on_url_change(self, event):
        video_url = self.url_entry.get()
        self.chapters = get_chapters(video_url)
        self.update_chapter_selection()
    
    def toggle_all_chapters(self):
        state = self.select_all_var.get()
        for var in self.chapter_vars:
            var.set(state)

    def update_chapter_selection(self):
        # Clear existing chapter selection
        for widget in self.chapter_frame.winfo_children():
            widget.destroy()
        self.chapter_vars.clear()

        # Create a sub-frame for chapters
        chapter_sub_frame = Frame(self.chapter_frame)
        chapter_sub_frame.pack(fill='x', expand=True)

        if self.chapters:
            # Create "Select All" checkbox
            self.select_all_var = IntVar()
            select_all_cb = WrappingCheckbutton(chapter_sub_frame, text="Select All", 
                                                variable=self.select_all_var, 
                                                command=self.toggle_all_chapters)
            select_all_cb.pack(anchor='w', padx=5, fill='x')

            # Create a checkbox for each chapter
            for chapter in self.chapters:
                var = IntVar()
                cb = WrappingCheckbutton(chapter_sub_frame, text=chapter, variable=var)
                cb.pack(anchor='w', padx=5, fill='x')
                self.chapter_vars.append(var)
        else:
            Label(chapter_sub_frame, text="No chapters found for this video.", wraplength=300).pack(padx=5, fill='x')

        # Update the scroll region
        self.root.update()
        self.scrollable_window.canvas.configure(scrollregion=self.scrollable_window.canvas.bbox("all"))


    def init_window(self):
        self.root = tk.Tk()
        self.root.title("YouTube URL to Markdown")
        
        # Create the scrollable window
        self.scrollable_window = ScrollableWindow(self.root)
        self.scrollable_window.pack(fill="both", expand=True)

        # Main content frame
        self.main_frame = self.scrollable_window.scrollable_frame

        # Set a consistent padding
        padding = 10

        # URL Entry
        url_label = Label(self.main_frame, text="Video url:")
        url_label.pack(pady=(padding, 0), padx=padding, anchor='w')
        self.url_entry = Entry(self.main_frame)
        self.url_entry.pack(pady=(0, padding), padx=padding, fill='x')
        self.url_entry.bind('<FocusOut>', self.on_url_change)

        # File Name Entry
        file_name_label = Label(self.main_frame, text="Note name:")
        file_name_label.pack(pady=(padding, 0), padx=padding, anchor='w')
        self.file_name_entry = Entry(self.main_frame)
        self.file_name_entry.pack(pady=(0, padding), padx=padding, fill='x')

        # Saving Path Combo
        path_label = Label(self.main_frame, text="Folder path:")
        path_label.pack(pady=(padding, 0), padx=padding, anchor='w')
        path_frame = tk.Frame(self.main_frame)
        path_frame.pack(pady=(0, padding), padx=padding, fill='x')
        self.path_combo = Combobox(path_frame)
        self.path_combo.pack(side=tk.LEFT, expand=True, fill='x')
        select_button = Button(path_frame, text="Browse...", command=self.select_folder)
        select_button.pack(side=tk.RIGHT)
        
        # Template Path Combo
        template_path_label = Label(self.main_frame, text="Template path:")
        template_path_label.pack(pady=(padding, 0), padx=padding, anchor='w')
        template_path_frame = tk.Frame(self.main_frame)
        template_path_frame.pack(pady=(0, padding), padx=padding, fill='x')
        self.template_path_combo = Combobox(template_path_frame)
        self.template_path_combo.pack(side=tk.LEFT, expand=True, fill='x')
        select_template_button = Button(template_path_frame, text="Browse...", command=self.select_template_file)
        select_template_button.pack(side=tk.RIGHT)
        
        # Prompts Path Combo
        prompts_path_label = Label(self.main_frame, text="Prompts path:")
        prompts_path_label.pack(pady=(padding, 0), padx=padding, anchor='w')
        prompts_path_frame = tk.Frame(self.main_frame)
        prompts_path_frame.pack(pady=(0, padding), padx=padding, fill='x')
        self.prompts_path_combo = Combobox(prompts_path_frame)
        self.prompts_path_combo.pack(side=tk.LEFT, expand=True, fill='x')
        select_prompts_button = Button(prompts_path_frame, text="Browse...", command=self.select_prompts_file)
        select_prompts_button.pack(side=tk.RIGHT)

        # Chapter selection frame
        chapter_label = Label(self.main_frame, text="Select Chapters:")
        chapter_label.pack(pady=(padding, 0), padx=padding, anchor='w')
        self.chapter_frame = Frame(self.main_frame)
        self.chapter_frame.pack(pady=(0, padding), padx=padding, fill='x', expand=True)

        # Create button
        create_button = Button(self.main_frame, text="Create", command=self.on_create_button_click)
        create_button.pack(pady=padding, padx=padding, fill='x')

        # Set a minimum size for the window
        self.root.update()
        self.root.minsize(400, self.root.winfo_height())

        # Set the initial size of the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(500, screen_width)
        window_height = min(600, screen_height)
        self.root.geometry(f"{window_width}x{window_height}")



    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()