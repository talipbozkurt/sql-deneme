# Temel python ve ubuntu araçları olan bir imaj
FROM mcr.microsoft.com/devcontainers/python:3.10

# Öğrencilerin SQL dosyalarını test etmeleri için SQLite3 ve gerekli paketleri kur
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install sqlite3 libsqlite3-dev

# Eğer öğrencilerin test dosyalarını (CS50 gibi) kullanmasını istiyorsan python paketleri
RUN pip3 install --no-cache-dir cs50 sqlparse
