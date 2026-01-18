import tkinter as tk
from random import paretovariate
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sv_ttk
import json
import os #tEeeeeeeeeeeeeeeeeest

# importuri selenium (sunt aici pentru usurinta)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from scrape_functions import *

# !!!!!!!!!!!!!!!!!!!!!!!!!!!
# daca modifici cod adauga comentarii pentru ca noi,ceilalti sa stim ce si cum ai modificat

# de facut: mai multe articole , docker 4444:4444
# erori de rezolvat: stale element atunci cand dai sa incarce pagina -> trebuie adaugat un for care sa mai incerce
#                   de minim inca 3 ori sa ruleze tot codul pentru ca de cele mai multe ori daca ii dai sa se incarce
#                   din nou... merge

# daca nu au fost adaugate comentarii modifica:
# TOTAL ORE PIERDUTE IN DEBUGGING : 1

# am mutat functiile de scraping in fisierul scrape_functions.py pentru usurinta de verificare si vizuala
# aici adaugi functia noua pentru un alt site

#adaugat interfata pentru site-uri favorite si logica din spate
#i.e sa pastreze in memorie site-urile bifate drept "favorite" intru-un fisier json
#3-10 bife au o marime infinit de mica 100-200 bytes

SCRAPERS = {
    "Digi24": scrape_digi24,
    "ProTV": scrape_PROTV,
    "Libertatea": scrape_Libertatea,
    "HotNews" : scrape_HotNews,
    "Observator" : scrape_Observator,
    "G4Media" : scrape_G4Media,
    "TVRInfo" : scrape_TVRInfo,
}

# //////////////////////////////////////

# GUI(clasa aplicatiei)

class NewsScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("News Scraper GUI")
        master.geometry("900x850")

        # buton de setari
        style = ttk.Style()
        style.configure("Setari.TButton", font=("arial", 17))
        self.settings_btn=ttk.Button(master, text="⚙", width=1.5, command=self.settings_btn_action, style="Setari.TButton")
        self.settings_btn.place(relx=1, x=-20, y=20, anchor="ne")

        # articol curent
        self.current_article = {"title": "", "content": "", "link": "", "site": ""}
        self.active_threads = 0

        # Sursa individuala
        site_label = ttk.Label(master, text="Sursă individuală:", font=("Arial", 12))
        site_label.pack(pady=5)

        self.site_var = tk.StringVar(value="Digi24")
        self.site_dropdown = ttk.Combobox(master, textvariable=self.site_var,
                                          values=list(SCRAPERS.keys()), state="readonly", width=30)
        self.site_dropdown.pack(pady=5)

        # --- SECTIUNE FAVORITE ---
        fav_label = ttk.Label(master, text="Alege site-urile tale favorite (pentru 'My Websites')", font=("Arial", 11, "bold"))
        fav_label.pack(pady=(15, 5))

        checkbox_frame = ttk.Frame(master)
        checkbox_frame.pack(pady=5)

        self.check_vars = {}
        for site in SCRAPERS.keys():
            var = tk.BooleanVar(value=False) # initial debifat
            self.check_vars[site] = var
            # Salveaza automat la fiecare interactiune
            cb = ttk.Checkbutton(checkbox_frame, text=site, variable=var, command=self.save_preferences)
            cb.pack(side=tk.LEFT, padx=10)

        self.load_preferences()

        # zona text pentru articol
        self.text_box = scrolledtext.ScrolledText(master, wrap="word", width=100, height=20, font=("times new roman", 12))
        self.text_box.pack(pady=10, padx=50, fill=tk.BOTH, expand=True)

        self.text_box.tag_configure("Titlu", justify='center', font=("times new roman", 24, "bold", "underline"))
        self.text_box.tag_configure("SursaTag", font=("times new roman", 14, "italic"))
        self.text_box.tag_configure("ContinutTag", font=("times new roman", 16))

        self.text_box.insert(tk.END, "Sistem Gata. Aștept comenzi.", "Titlu")

        # BUTOANE
        button_frame = ttk.Frame(master)
        button_frame.pack(pady=10)

        self.load_btn = ttk.Button(button_frame, text="Cauta articol", width=15, command=self.start_scraper_thread)
        self.load_btn.grid(row=0, column=0, padx=5)

        self.presets_btn = ttk.Button(button_frame, text="My Websites", width=15, command=self.start_presets_news)
        self.presets_btn.grid(row=0, column=1, padx=5)

        self.source_btn = ttk.Button(button_frame, text="Sursa???", width=15, command=self.show_source)
        self.source_btn.grid(row=0, column=2, padx=5)

        self.full_load_btn = ttk.Button(button_frame, text="Stirile zilei", width=15, command=self.start_all_news)
        self.full_load_btn.grid(row=0, column=3, padx=5)


    # --- FUNCTIA DE SETARI ---
    def settings_btn_action(self):
        ana=3

    # --- PERSITANT DATA ---
    def save_preferences(self):
        data = {site: var.get() for site, var in self.check_vars.items()}
        try:
            with open("user_settings.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Eroare salvare: {e}")

    def load_preferences(self):
        if os.path.exists("user_settings.json"):
            try:
                with open("user_settings.json", "r") as f:
                    data = json.load(f)
                    for site, val in data.items():
                        if site in self.check_vars:
                            self.check_vars[site].set(val)
            except: pass

    # --- LOGICA THREADING ---
    def start_all_news(self):
        self.full_load_btn.config(state=tk.DISABLED, text="ASTEAPTA BAAAA!!!")
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, "Se incarca TOATE stirile...\n", "Titlu")
        self.active_threads = len(SCRAPERS)
        for site in SCRAPERS:
            threading.Thread(target=self.special_run_scraper, args=(site,), daemon=True).start()

    def start_presets_news(self):
        selected = [s for s, v in self.check_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("Atentie", "Bifeaza site-uri favorite mai intai!")
            return
        self.presets_btn.config(state=tk.DISABLED, text="RULARE...")
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, "Se incarca site-urile preferate...\n", "Titlu")
        self.active_threads = len(selected)
        for site in selected:
            threading.Thread(target=self.special_run_scraper, args=(site,), daemon=True).start()

    def start_scraper_thread(self):
        site = self.site_var.get()
        self.load_btn.config(state=tk.DISABLED, text="ASTEAPTA BAAAA!!!")
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, f"Se incarca {site}...\n", "Titlu")
        threading.Thread(target=self.run_scraper, args=(site,), daemon=True).start()

    def run_scraper(self, site):
        try:
            data = SCRAPERS[site]()
            self.master.after(0, self.update_gui_success, site, data)
        except Exception as e:
            self.master.after(0, self.update_gui_error, str(e))

    def special_run_scraper(self, site):
        try:
            data = SCRAPERS[site]()
            self.master.after(0, self.add_gui_success, site, data)
        except Exception as e:
            self.master.after(0, self.update_gui_error, str(e))

    def update_gui_success(self, site, data):
        self.current_article = data
        self.current_article["site"] = site
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, f"Sursa: {site}\n", "SursaTag")
        self.text_box.insert(tk.END, f"{data['title']}\n\n", "Titlu")
        self.text_box.insert(tk.END, f"\t{data['content']}\n\n", "ContinutTag")
        self.load_btn.config(state=tk.NORMAL, text="Cauta articol")

    def add_gui_success(self, site, data):
        self.text_box.insert(tk.END, f"Sursa: {site}\n", "SursaTag")
        self.text_box.insert(tk.END, f"{data['title']}\n\n", "Titlu")
        self.text_box.insert(tk.END, f"\t{data['content']}\n\n", "ContinutTag")
        self.text_box.insert(tk.END, "-"*30 + "\n\n")
        self.active_threads -= 1
        if self.active_threads <= 0:
            self.text_box.delete("1.0", "2.0")
            self.full_load_btn.config(state=tk.NORMAL, text="Stirile zilei")
            self.presets_btn.config(state=tk.NORMAL, text="My Websites")

    def update_gui_error(self, error_msg):
        # AICI A FOST EROAREA DE SYNTAXA - REPARATA:
        self.text_box.insert(tk.END, f"\nEroare: {error_msg}\n")
        messagebox.showerror("Error", error_msg)
        self.load_btn.config(state=tk.NORMAL, text="Cauta articol")
        self.presets_btn.config(state=tk.NORMAL, text="My Websites")
        self.full_load_btn.config(state=tk.NORMAL, text="Stirile zilei")

    def show_source(self):
        link = self.current_article.get("link")
        if not link:
            messagebox.showinfo("Info", "Niciun articol incarcat.")
            return
        messagebox.showinfo("Sursa", f"Link articol: {link}")

if __name__ == "__main__":
    root = tk.Tk()
    sv_ttk.set_theme("dark")
    app = NewsScraperApp(root)
    root.mainloop()