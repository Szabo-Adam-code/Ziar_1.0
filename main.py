import tkinter as tk
from random import paretovariate
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sv_ttk

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
        master.geometry("900x700")

        # articol curent
        self.current_article = {"title": "", "content": "", "link": "", "site": ""}

        # Lista dropdown, momentan e doar pentru un element
        #daca creezi functii noi trebuie sa modifici lista
        site_label = ttk.Label(master, text="Sursă:", font=("Arial", 12))
        site_label.pack(pady=5)

        self.site_var = tk.StringVar(value="Digi24")
        self.site_dropdown = ttk.Combobox(master, textvariable=self.site_var,
                                          values=list(SCRAPERS.keys()), state="readonly", width=30)
        self.site_dropdown.pack(pady=5)

        # zona text pentru articol
        self.text_box = scrolledtext.ScrolledText(master, wrap="word", width=100, height=25, font=("times new roman", 12))

        # fill=tk.BOTH -> umple spațiul și pe orizontală și pe verticală
        # expand=True  -> permite widget-ului să ocupe spațiul suplimentar generat la redimensionare
        self.text_box.pack(pady=10, padx=50, fill=tk.BOTH, expand=True)

        # lista de tag-uri pt stilul textului
        self.text_box.tag_configure("Titlu", justify='center', font=("times new roman", 24, "bold"))
        self.text_box.tag_configure("SursaTag", font=("times new roman", 14, "italic"))
        self.text_box.tag_configure("ContinutTag", font=("times new roman", 16))

        self.text_box.insert(tk.END, "Apasati Cauta Articol", "Titlu")

        # BUTOANE
        button_frame = ttk.Frame(master)
        button_frame.pack(pady=10)

        self.load_btn = ttk.Button(button_frame, text="Cauta articol", width=20,
                                  command=self.start_scraper_thread)
        self.load_btn.grid(row=0, column=0, padx=10)

        self.source_btn = ttk.Button(button_frame, text="Sursa??? (nu te cred)", width=20,
                                    command=self.show_source)
        self.source_btn.grid(row=0, column=1, padx=10)

        self.full_load_btn = ttk.Button(button_frame, text="Stirile zilei", width=20,
                                     command=self.start_all_news)
        self.full_load_btn.grid(row=0, column=2, padx=10)

    #functie care ruleaza si afiseaza o stire din fiecare sursa
    def start_all_news(self):
        site = self.site_var.get()
        self.full_load_btn.config(state=tk.DISABLED, text="ASTEAPTA BAAAA!!!")
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, "Se incarca. Va rugam sa asteptati...\n", "Titlu")

        # thread start
        for sites in SCRAPERS:
            #site = self.sites.get()
            scraper_thread = threading.Thread(target=self.special_run_scraper, args=(sites,))
            scraper_thread.start()
        #self.text_box.delete("1.0", "2.0")

        #ruleaza in loop toate sursele de stiri

    # functie care rulează scraper-ul într-un thread separat
    #evita blocarea interfetei
    def start_scraper_thread(self):
        site = self.site_var.get()
        self.load_btn.config(state=tk.DISABLED, text="ASTEAPTA BAAAA!!!")
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, "Se incarca. Va rugam sa asteptati...\n", "Titlu")

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

    #tot thread dar adauga in gui fara sa stearga
    def special_run_scraper(self, site):
        try:
            data = SCRAPERS[site]()
            # comunica rezultat la firul principal
            self.master.after(0, self.add_gui_success, site, data)
        except Exception as e:
            # comunica eroarea la firul principal
            self.master.after(0, self.update_gui_error, str(e))

    # functie pentru actualizarea GUI dupa succes
    def update_gui_success(self, site, data):
        self.current_article = data
        self.current_article["site"] = site

        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, f"Sursa: {site}\n", "SursaTag")
        self.text_box.insert(tk.END, f"{self.current_article['title']}\n\n", "Titlu")
        self.text_box.insert(tk.END, f"\t{self.current_article['content']}\n\n", "ContinutTag")
        self.text_box.insert(tk.END, f"Link: {self.current_article['link']}\n", "SursaTag")

        self.load_btn.config(state=tk.NORMAL, text="Find article")

    #functie care adauga text in continuare dupa succes
    def add_gui_success(self, site, data):
        self.current_article = data
        self.current_article["site"] = site

        self.text_box.insert(tk.END, f"Sursa: {site}\n", "SursaTag")
        self.text_box.insert(tk.END, f"{self.current_article['title']}\n\n", "Titlu")
        self.text_box.insert(tk.END, f"\t{self.current_article['content']}\n\n", "ContinutTag")
        self.text_box.insert(tk.END, f"Link: {self.current_article['link']}\n", "SursaTag")
        self.text_box.insert(tk.END, f"\n\n\n")

        self.full_load_btn.config(state=tk.NORMAL, text="Stirile Zilei")
        ##doar adauga in continuare in loc sa stearga ce e pe ecran inainte

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
        self.text_box.insert(tk.END, f"Source {site}:\n{link}", "SursaTag")


if __name__ == "__main__":
    root = tk.Tk()
    app = NewsScraperApp(root)
    sv_ttk.set_theme("dark") #sa fie pe mod intunecat gen
    root.mainloop()