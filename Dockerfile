FROM python:3.11-slim
#defineste versiunea de python 

#setez variabila display pentru procesele din docker
ENV DISPLAY=:99

#accept pt linux sa nu mai am prompt de da/nu cand instalez pachetele
ENV DEBIAN_FRONTEND=noninteractive

#Dependinte de sistem ca nu vreau sa mut tot codul de scraping in alt .py
RUN apt-get update && apt-get install -y \
    xvfb \
    x11-utils \
    xauth \
    tk \
    tcl \
    libtk8.6 \
    libx11-6 \
    libxrender1 \
    libxext6 \
    libsm6 \
    libgl1 \
    wget \
    unzip \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

#instalam dependintele de python

COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

# codul aplicatiei
COPY . .

# pornest un display server virtual care sa ruleze tkinter
CMD Xvfb :99 -screen 0 1280x800x16 & python main.py
