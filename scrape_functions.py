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

#     functie scraper
# aici poti adauga mai multe pentru fiecare site in parte
#daca adaugi functie de scapring nu uita sa actualizezi SCRAPERS


def scrape_digi24():
   #logica selenium de a citi site-uri

    # chromedrivermanager pentru a evita erori de compatibilitate cu chrome
   #ajuta pentru a rula pe windows/linux doar sa ai facut enviroment cu tkinter pt interfata
    service = Service(ChromeDriverManager().install())


    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless=new") ##asta face ca pagina sa ruleze in fundal

    driver = webdriver.Chrome(service=service, options=chrome_options)#docker 4444:4444 ca sa ruleze selenium in background

    # return data
    data = {"title": "Fara titlu", "content": "Fara continut", "link": driver.current_url}

    try:
        driver.get("https://www.digi24.ro/stiri")
        wait = WebDriverWait(driver, 15)

        #am folosit id in loc de xpath
        cookie_id = "onetrust-accept-btn-handler"

        try:
            # timer ca butonul sa poata fi apasat
            #fara site-ul nu inregistreaza click pe buton de accept cookies
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, cookie_id)))
            cookie_btn.click()
        except:
            print("error cookie banner not found")
            pass  # Ignorăm dacă nu apare

        time.sleep(1)  # Pauză scurtă

        # 2. click pe primul articol(article-thumb)
        first_article_thumb = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "article-thumb"))
        )

        try:
            first_article_thumb.click()
        except Exception as e:
            # forteaza click pe primul element ce il gaseste
            if 'element click intercepted' in str(e):
                driver.execute_script("arguments[0].click();", first_article_thumb)
            else:
                raise e

        # s-a deschis pagina, salvam
        data["link"] = driver.current_url

        # 3. extrage titlu
        title_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        )
        data["title"] = title_element.text

        # 4. extrage paragrafe
        paragraphs = driver.find_elements(By.CSS_SELECTOR, "main article p, h2")
        data["content"] = "\n\n".join([p.text for p in paragraphs if p.text])

        if not data["content"]:
            data["content"] = "error fara continut extras"

    except Exception as e:
        # afiseaza eroare in GUI
        raise Exception(f"error scraping: {str(e)}")

    finally:
        # ALWAYS CLOSE BROWSER
        driver.quit()

    # returneaza ce ai pescuit
    return data

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def scrape_PROTV():
   #logica selenium de a citi site-uri

    # chromedrivermanager pentru a evita erori de compatibilitate cu chrome
   #ajuta pentru a rula pe windows/linux doar sa ai facut enviroment cu tkinter pt interfata
    service = Service(ChromeDriverManager().install())


    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(service=service, options=chrome_options)

    # return data
    data = {"title": "Fara titlu", "content": "Fara continut", "link": driver.current_url}

    try:
        driver.get("https://stirileprotv.ro/")
        wait = WebDriverWait(driver, 15)

        #am folosit id in loc de xpath
        cookie_id = "onetrust-accept-btn-handler"

        try:
            # timer ca butonul sa poata fi apasat
            #fara site-ul nu inregistreaza click pe buton de accept cookies
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, cookie_id)))
            cookie_btn.click()
        except:
            print("error cookie banner not found")
            pass  # Ignorăm dacă nu apare

        time.sleep(1)  # Pauză scurtă

        # 2. click pe primul articol(article-thumb)
        first_article_thumb = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "article-picture"))
        )

        try:
            first_article_thumb.click()
        except Exception as e:
            # forteaza click pe primul element ce il gaseste
            if 'element click intercepted' in str(e):
                driver.execute_script("arguments[0].click();", first_article_thumb)
            else:
                raise e

        # s-a deschis pagina, salvam
        data["link"] = driver.current_url

        # cookie nou
        cookie_id = "didomi-notice-agree-button"

        try:
            # timer ca butonul sa poata fi apasat
            # fara site-ul nu inregistreaza click pe buton de accept cookies
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, cookie_id)))
            cookie_btn.click()
        except:
            print("error cookie banner not found")
            pass  # Ignorăm dacă nu apare

        time.sleep(1)  # Pauză scurtă

        # 3. extrage titlu
        title_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "article--title"))
        )
        data["title"] = title_element.text

        # 4. extrage paragrafe
        paragraphs = driver.find_elements(By.CSS_SELECTOR, "div.article--text p, h2")
        data["content"] = "\n\n".join([p.text for p in paragraphs if p.text])

        if not data["content"]:
            data["content"] = "error fara continut extras"

    except Exception as e:
        # afiseaza eroare in GUI
        raise Exception(f"error scraping: {str(e)}")

    finally:
        # ALWAYS CLOSE BROWSER
        driver.quit()

    # returneaza ce ai pescuit
    return data

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def scrape_Libertatea():
   #logica selenium de a citi site-uri

    # chromedrivermanager pentru a evita erori de compatibilitate cu chrome
   #ajuta pentru a rula pe windows/linux doar sa ai facut enviroment cu tkinter pt interfata
    service = Service(ChromeDriverManager().install())


    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(service=service, options=chrome_options)

    # return data
    data = {"title": "Fara titlu", "content": "Fara continut", "link": driver.current_url}

    try:
        driver.get("https://www.libertatea.ro/stiri")
        wait = WebDriverWait(driver, 15)

        #am folosit id in loc de xpath
        cookie_id = "onetrust-accept-btn-handler"

        try:
            # timer ca butonul sa poata fi apasat
            #fara site-ul nu inregistreaza click pe buton de accept cookies
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, cookie_id)))
            cookie_btn.click()
        except:
            print("error cookie banner not found")
            pass  # Ignorăm dacă nu apare

        time.sleep(1)  # Pauză scurtă

        # 2. click pe primul articol(article-thumb)
        first_article_thumb = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "thumb"))
        )

        try:
            first_article_thumb.click()
        except Exception as e:
            # forteaza click pe primul element ce il gaseste
            if 'element click intercepted' in str(e):
                driver.execute_script("arguments[0].click();", first_article_thumb)
            else:
                raise e

        # s-a deschis pagina, salvam
        data["link"] = driver.current_url


        # 3. extrage titlu
        title_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        )
        data["title"] = title_element.text

        # 4. extrage paragrafe
        paragraphs = driver.find_elements(By.CSS_SELECTOR, "div.artC1 p, div.artC1 h2")
        data["content"] = "\n\n".join([p.text for p in paragraphs if p.text])

        if not data["content"]:
            data["content"] = "error fara continut extras"

    except Exception as e:
        # afiseaza eroare in GUI
        raise Exception(f"error scraping: {str(e)}")

    finally:
        # ALWAYS CLOSE BROWSER
        driver.quit()

    # returneaza ce ai pescuit
    return data
