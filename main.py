import tkinter as tk
from random import paretovariate
from tkinter import ttk, scrolledtext, messagebox
import threading
import time

#importuri selenium (sunt aici pentru usurinta)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from scrape_functions import *

#!!!!!!!!!!!!!!!!!!!!!!!!!!!
#daca modifici cod adauga comentarii pentru ca noi,ceilalti sa stim ce si cum ai modificat

#de facut: mai multe articole , docker 4444:4444, si sa updatam interfata
#erori de rezolvat: stale element atunci cand dai sa incarce pagina -> trebuie adaugat un for care sa mai incerce
#                   de minim inca 3 ori sa ruleze tot codul pentru ca de cele mai multe ori daca ii dai sa se incarce
#                   din nou... merge

#daca nu au fost adaugate comentarii modifica:
#TOTAL ORE PIERDUTE IN DEBUGGING : 1


#am mutat functiile de scraping in fisierul scrape_functions.py pentru usurinta de verificare si vizuala
#aici adaugi functia noua pentru un alt site
SCRAPERS = {
    "Digi24": scrape_digi24,
    "ProTV": scrape_PROTV,
    "Libertatea": scrape_Libertatea,
    #exemplu "ProTV": scrape_protv
}


#//////////////////////////////////////

#GUI(clasa aplicatiei)

class NewsScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("News Scraper GUI")
        master.geometry("900x600")

        # articol curent
        self.current_article = {"title": "", "content": "", "link": "", "site": ""}

        # Lista dropdown, momentan e doar pentru un element
        #daca creezi functii noi trebuie sa modifici lista
        site_label = tk.Label(master, text="Sursă:", font=("Arial", 12))
        site_label.pack(pady=5)

        self.site_var = tk.StringVar(value="Digi24")
        self.site_dropdown = ttk.Combobox(master, textvariable=self.site_var,
                                          values=list(SCRAPERS.keys()), state="readonly", width=30)
        self.site_dropdown.pack(pady=5)

        # zona text pentru articol
        self.text_box = scrolledtext.ScrolledText(master, width=100, height=25, font=("Arial", 11))
        self.text_box.pack(pady=10)
        self.text_box.insert(tk.END, "Press Find Article")

        # BUTOANE
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        self.load_btn = tk.Button(button_frame, text="Find Article", width=20,
                                  command=self.start_scraper_thread)
        self.load_btn.grid(row=0, column=0, padx=10)

        self.source_btn = tk.Button(button_frame, text="Show source link", width=20,
                                    command=self.show_source)
        self.source_btn.grid(row=0, column=1, padx=10)

    # functie care rulează scraper-ul într-un thread separat
    #evita blocarea interfetei
    def start_scraper_thread(self):
        site = self.site_var.get()
        self.load_btn.config(state=tk.DISABLED, text="Loading")
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, "Loading. Please wait\n")

        # thread start
        scraper_thread = threading.Thread(target=self.run_scraper, args=(site,))
        scraper_thread.start()

    # functie rulata de thread (executa selenium)
    def run_scraper(self, site):
        try:
            data = SCRAPERS[site]()
            # comunica rezultat la firul principal
            self.master.after(0, self.update_gui_success, site, data)
        except Exception as e:
            # comunica eroarea la firul principal
            self.master.after(0, self.update_gui_error, str(e))

    # functie pentru actualizarea GUI dupa succes
    def update_gui_success(self, site, data):
        self.current_article = data
        self.current_article["site"] = site

        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, f"Sursa: {site}\n")
        self.text_box.insert(tk.END, f"Titlu: {self.current_article['title']}\n\n", ("header", "bold"))
        self.text_box.insert(tk.END, f"{self.current_article['content']}\n\n")
        self.text_box.insert(tk.END, f"Link: {self.current_article['link']}\n")

        self.load_btn.config(state=tk.NORMAL, text="Find article")

    # functie pentru actualizarea GUI dupa eroare
    def update_gui_error(self, error_msg):
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, f"scraping error:\n{error_msg}")
        messagebox.showerror("error", error_msg)
        self.load_btn.config(state=tk.NORMAL, text="Find Article")

    # functia Show source link
    def show_source(self):
        link = self.current_article.get("link")
        site = self.current_article.get("site")

        if not link or site == "":
            messagebox.showinfo("Informație",
                                "There is no article. Please use Find Article.")
            return

        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, f"Source {site}:\n{link}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NewsScraperApp(root)
    root.mainloop()