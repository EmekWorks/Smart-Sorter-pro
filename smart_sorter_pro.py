import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import datetime
import hashlib
import json

file_types = {
    "Obrazy": [".jpg", ".jpeg", ".png", ".gif"],
    "Dokumenty": [".pdf", ".docx", ".txt"],
    "Wideo": [".mp4", ".mkv", ".avi"],
    "Muzyka": [".mp3", ".wav"]
}

SETTINGS_FILE = "settings.json"
auto_sort_enabled = False


def save_settings():
    settings = {
        "folder": folder_path.get(),
        "sort_mode": sort_mode.get()
    }
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                folder_path.set(settings.get("folder", ""))
                sort_mode.set(settings.get("sort_mode", "type"))
        except Exception:
            folder_path.set("")
            sort_mode.set("type")


def write_log(message):
    with open("log.txt", "a", encoding="utf-8") as log_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - {message}\n")


def open_log():
    if os.path.exists("log.txt"):
        os.startfile("log.txt")
    else:
        messagebox.showinfo("Informacja", "Plik log.txt jeszcze nie istnieje.")


def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()


def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)
        save_settings()


def sort_selected_folder():
    folder = folder_path.get()
    sort_folder(folder, show_message=True)
    save_settings()


def sort_downloads_folder():
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    sort_folder(downloads_folder, show_message=True)
    save_settings()


def sort_folder(folder, show_message=False):
    mode = sort_mode.get()

    if not folder:
        if show_message:
            messagebox.showerror("Błąd", "Najpierw wybierz folder!")
        return

    if not os.path.exists(folder):
        if show_message:
            messagebox.showerror("Błąd", "Folder nie istnieje!")
        return

    files = os.listdir(folder)
    total_files = len(files)
    moved_files = 0
    file_hashes = {}

    progress["value"] = 0
    progress["maximum"] = total_files if total_files > 0 else 1

    duplicate_folder = os.path.join(folder, "Duplikaty")
    if not os.path.exists(duplicate_folder):
        os.makedirs(duplicate_folder)

    for i, filename in enumerate(files):
        file_path = os.path.join(folder, filename)

        if os.path.isfile(file_path):
            try:
                file_hash = get_file_hash(file_path)

                if file_hash in file_hashes:
                    shutil.move(file_path, os.path.join(duplicate_folder, filename))
                    moved_files += 1
                    write_log(f"Duplikat: przeniesiono plik {filename} do folderu Duplikaty")
                    progress["value"] = i + 1
                    root.update_idletasks()
                    continue
                else:
                    file_hashes[file_hash] = filename

            except Exception as e:
                write_log(f"Błąd przy sprawdzaniu duplikatu dla pliku {filename}: {e}")
                progress["value"] = i + 1
                root.update_idletasks()
                continue

            if mode == "type":
                ext = os.path.splitext(filename)[1].lower()
                moved = False

                for category, extensions in file_types.items():
                    if ext in extensions:
                        category_folder = os.path.join(folder, category)

                        if not os.path.exists(category_folder):
                            os.makedirs(category_folder)

                        shutil.move(file_path, os.path.join(category_folder, filename))
                        moved_files += 1
                        moved = True
                        write_log(f"Przeniesiono plik {filename} do folderu {category}")
                        break

                if not moved:
                    other_folder = os.path.join(folder, "Inne")

                    if not os.path.exists(other_folder):
                        os.makedirs(other_folder)

                    shutil.move(file_path, os.path.join(other_folder, filename))
                    moved_files += 1
                    write_log(f"Przeniesiono plik {filename} do folderu Inne")

            elif mode == "date":
                timestamp = os.path.getctime(file_path)
                date = datetime.datetime.fromtimestamp(timestamp)

                year = str(date.year)
                month = date.strftime("%m-%B")

                year_folder = os.path.join(folder, year)
                month_folder = os.path.join(year_folder, month)

                if not os.path.exists(year_folder):
                    os.makedirs(year_folder)

                if not os.path.exists(month_folder):
                    os.makedirs(month_folder)

                shutil.move(file_path, os.path.join(month_folder, filename))
                moved_files += 1
                write_log(f"Przeniesiono plik {filename} do folderu {year}\\{month}")

        progress["value"] = i + 1
        root.update_idletasks()

    save_settings()

    if show_message:
        messagebox.showinfo("Gotowe", f"Przeniesiono {moved_files} plików!")


def toggle_auto_sort():
    global auto_sort_enabled
    auto_sort_enabled = auto_sort_var.get()

    if auto_sort_enabled:
        status_label.config(text="Auto-sortowanie: WŁĄCZONE")
        write_log("Włączono automatyczne sortowanie folderu Pobrane")
        auto_sort_downloads()
    else:
        status_label.config(text="Auto-sortowanie: WYŁĄCZONE")
        write_log("Wyłączono automatyczne sortowanie folderu Pobrane")


def auto_sort_downloads():
    if auto_sort_enabled:
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        sort_folder(downloads_folder, show_message=False)
        root.after(10000, auto_sort_downloads)


def on_mode_change():
    save_settings()


root = tk.Tk()
root.title("Smart Sorter PRO V6")
root.geometry("520x520")
root.configure(bg="#f4f6f8")

folder_path = tk.StringVar()
sort_mode = tk.StringVar(value="type")
auto_sort_var = tk.BooleanVar(value=False)

load_settings()

title_label = tk.Label(
    root,
    text="Smart Sorter PRO V6",
    font=("Arial", 16, "bold"),
    bg="#f4f6f8"
)
title_label.pack(pady=15)

main_frame = tk.Frame(root, bg="white", bd=1, relief="solid", padx=20, pady=20)
main_frame.pack(padx=20, pady=10, fill="both", expand=True)

label = tk.Label(main_frame, text="Wybierz folder do posortowania", font=("Arial", 11), bg="white")
label.pack(pady=5)

entry = tk.Entry(main_frame, textvariable=folder_path, width=55, font=("Arial", 10))
entry.pack(pady=5)

button_choose = tk.Button(main_frame, text="Wybierz folder", command=choose_folder, width=25)
button_choose.pack(pady=8)

mode_label = tk.Label(main_frame, text="Tryb sortowania", font=("Arial", 11, "bold"), bg="white")
mode_label.pack(pady=10)

radio_type = tk.Radiobutton(
    main_frame,
    text="Sortuj po typie",
    variable=sort_mode,
    value="type",
    command=on_mode_change,
    bg="white"
)
radio_type.pack()

radio_date = tk.Radiobutton(
    main_frame,
    text="Sortuj po dacie",
    variable=sort_mode,
    value="date",
    command=on_mode_change,
    bg="white"
)
radio_date.pack()

button_sort = tk.Button(main_frame, text="Sortuj wybrany folder", command=sort_selected_folder, width=25)
button_sort.pack(pady=10)

button_downloads = tk.Button(main_frame, text="Sortuj folder Pobrane", command=sort_downloads_folder, width=25)
button_downloads.pack(pady=5)

auto_checkbox = tk.Checkbutton(
    main_frame,
    text="Włącz automatyczne sortowanie folderu Pobrane",
    variable=auto_sort_var,
    command=toggle_auto_sort,
    bg="white"
)
auto_checkbox.pack(pady=15)

status_label = tk.Label(main_frame, text="Auto-sortowanie: WYŁĄCZONE", bg="white", font=("Arial", 10))
status_label.pack(pady=5)

button_log = tk.Button(main_frame, text="Otwórz log.txt", command=open_log, width=25)
button_log.pack(pady=10)

progress = ttk.Progressbar(main_frame, length=350)
progress.pack(pady=20)

root.mainloop()