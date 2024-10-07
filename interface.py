import tkinter as tk
from tkinter import Label, Entry, Button, filedialog
import json
import os

from functions import *

class App:
  def __init__(self):
    self.config_file = "saved_fields.json"  # Path to the config file
    self.init_window()
    self.load_fields()

  # Function to handle the "Create" button click
  def on_create_button_click(self):
    # Get the URL and the path from the entry fields
    video_url = self.url_entry.get()
    file_name = self.file_name_entry.get()
    save_path = self.path_entry.get()
    template_path = self.template_path_entry.get()
    prompts_path = self.prompts_path_entry.get()
    
    # Save fields to a file
    self.save_fields()

    # Call the generate_note_file function
    generate_note_file(video_url, file_name, save_path, template_path, prompts_path)


  # Function to open file dialog and select folder
  def select_folder(self):
    # Open a file dialog to select a folder
    folder_path = filedialog.askdirectory()
    # Update the path_entry field with the selected folder path
    if folder_path:
      self.path_entry.delete(0, tk.END)  # Clear existing text
      self.path_entry.insert(0, folder_path)
      
  def select_template_file(self):
    # Open a file dialog to select a file
    file_path = filedialog.askopenfilename(
      title="Select Template File",
      filetypes=(("Text files", "*.md"), ("All files", "*.*"))
    )
    if file_path:
      self.template_path_entry.delete(0, tk.END)
      self.template_path_entry.insert(0, file_path)
  
  def select_prompts_file(self):
    # Open a file dialog to select a file
    file_path = filedialog.askopenfilename(
      title="Select Prompts File",
      filetypes=(("Text files", "*.md *.txt"), ("All files", "*.*"))
    )
    if file_path:
      self.prompts_path_entry.delete(0, tk.END)
      self.prompts_path_entry.insert(0, file_path)

  def save_fields(self):
    field_data = {
      "video_url": self.url_entry.get(),
      "file_name": self.file_name_entry.get(),
      "save_path": self.path_entry.get(),
      "template_path": self.template_path_entry.get(),
      "prompts_path:": self.prompts_path_entry.get()
    }
    with open(self.config_file, 'w') as f:
      json.dump(field_data, f)

  def load_fields(self):
    if os.path.exists(self.config_file):
      with open(self.config_file, 'r') as f:
        field_data = json.load(f)
      self.url_entry.insert(0, field_data.get("video_url", ""))
      self.file_name_entry.insert(0, field_data.get("file_name", ""))
      self.path_entry.insert(0, field_data.get("save_path", ""))
      self.template_path_entry.insert(0, field_data.get("template_path", ""))
      self.prompts_path_entry.insert(0, field_data.get("prompts_path", ""))

  def init_window(self):
    self.root = tk.Tk()
    self.root.title("YouTube URL to Markdown")
    self.root.geometry("400x400") # Taille auto pour la fenetre ?

    # Entry for the URL
    url_label = Label(self.root, text="Video url :")
    url_label.pack(pady=5)
    self.url_entry = Entry(self.root, width=50)
    self.url_entry.pack(pady=5)
    
    # Entry for the file name
    file_name_label = Label(self.root, text="Note name :")
    file_name_label.pack(pady=5)
    self.file_name_entry = Entry(self.root, width=50)
    self.file_name_entry.pack(pady=5)

    # Entry for the Saving Path
    path_label = Label(self.root, text="Folder path :")
    path_label.pack(pady=5)
    # Frame to hold the path entry and the select button
    path_frame = tk.Frame(self.root)
    path_frame.pack(pady=5)
    # Entry field for the path
    self.path_entry = Entry(path_frame, width=38)
    self.path_entry.pack(side=tk.LEFT)
    # Button to open file dialog to select a folder
    select_button = Button(path_frame, text="Browse...", command=self.select_folder)
    select_button.pack(side=tk.LEFT)
    
    # Entry for the Template Path
    template_path_label = Label(self.root, text="Template path :")
    template_path_label.pack(pady=5)
    template_path_frame = tk.Frame(self.root)
    template_path_frame.pack(pady=5)
    self.template_path_entry = Entry(template_path_frame, width=38)
    self.template_path_entry.pack(side=tk.LEFT)
    select_template_button = Button(template_path_frame, text="Browse...", command=self.select_template_file)
    select_template_button.pack(side=tk.LEFT)
    
    # Entry for the Prompts Path
    prompts_path_label = Label(self.root, text="Prompts path :")
    prompts_path_label.pack(pady=5)
    prompts_path_frame = tk.Frame(self.root)
    prompts_path_frame.pack(pady=5)
    self.prompts_path_entry = Entry(prompts_path_frame, width=38)
    self.prompts_path_entry.pack(side=tk.LEFT)
    select_prompts_button = Button(prompts_path_frame, text="Browse...", command=self.select_prompts_file)
    select_prompts_button.pack(side=tk.LEFT)

    # Create button
    create_button = Button(self.root, text="Create", command=self.on_create_button_click)
    create_button.pack(pady=20)

  def run(self):
    self.root.mainloop()


if __name__ == "__main__":
  # Run the Tkinter event loop
  app = App()
  app.run()
