# GITHUB CLASSROOM - ÇOKLU DİL GELİŞTİRME ORTAMI (SQL, Python, C, C#)
# Bu Dockerfile, öğrencilerin tarayıcıda (Codespaces) açacağı sanal bilgisayarın
# işletim sistemi ve kurulu programlarını tanımlar.

# Hedef: Gereksiz grafik arayüzlerden arındırılmış, hızlı ve tüm ders araçlarını içeren bir yapı.
# Base Image: Ubuntu 24.04 LTS (En güncel, uzun süreli desteklenen Linux sürümü)
FROM ubuntu:24.04



# ==============================================================================
# SİSTEM AYARLARI
# ==============================================================================
# Kurulum sırasında öğrenciden "Evet/Hayır" onayı beklememesi ve saat dilimi ayarları.
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=Europe/Istanbul \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1

# Kurulumları yönetici (root) yetkisiyle başlatıyoruz.
USER root

# ==============================================================================
# 1. TEMEL ARAÇLAR VE C/C++ KÜTÜPHANELERİ
# ==============================================================================

 # --- Genel Araçlar ---
    # curl/wget: Dosya indirmek için
    # git: Ödevleri GitHub'a göndermek için
    # vim/nano: Terminal üzerinden dosya düzenlemek için basit editörler

 # --- C/C++ Dersi İçin ---
    # gcc/g++: C kodlarını derlemek için standart derleyiciler
    # gdb: Kod hatası ayıklama (Debugging) için
    # valgrind: Öğrencilerin bellek hatalarını (Memory Leak) görmesi için

# --- Python Dersi İçin ---
    # python3-venv: Sanal ortam oluşturmak için

 # --- SQL Dersi İçin ---
    # sqlite3: Dosya tabanlı veritabanı
    # mysql/postgresql-client: Uzaktaki bir sunucuya bağlanmak gerekirse diye eklendi

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    curl wget git unzip zip tar gzip xz-utils \
    vim nano build-essential make cmake pkg-config \
    sudo locales tzdata ca-certificates gnupg \
    software-properties-common apt-transport-https \
    gcc g++ clang clang-format clang-tidy \
    libc6-dev gdb valgrind ltrace strace \
    python3 python3-pip python3-dev python3-venv \
    sqlite3 libsqlite3-dev libreadline-dev \
    postgresql-client mysql-client && \
    locale-gen tr_TR.UTF-8 en_US.UTF-8 && \
    update-locale LANG=C.UTF-8 && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ==============================================================================
# 2. PYTHON PAKETLERİ
# ==============================================================================

# Python ve Veri Bilimi dersleri için gerekli kütüphaneler.
    # Kod Düzeni: Öğrencinin kodunun PEP8 standartlarına uymasını sağlar
    # Test Araçları: Otomatik testler için
    # Veri Bilimi: Grafik çizimi ve veri analizi için (Matplotlib, Pandas, Numpy)
    # SQL CLI: Terminalde renkli ve tamamlamalı SQL yazmak için



RUN pip3 install --no-cache-dir --break-system-packages \
    pylint flake8 black autopep8 mypy \
    pytest \
    numpy pandas matplotlib jupyter ipython \
    litecli pgcli mycli

# Öğrenciler kendi paketlerini eklemek isterse:
# COPY requirements.txt /tmp/
# RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# ==============================================================================
# 3. C# / .NET 8.0 SDK KURULUMU
# ==============================================================================
# Linux depolarında varsayılan olarak gelmediği için Microsoft'tan manuel çekiyoruz.
RUN wget https://dot.net/v1/dotnet-install.sh -O /tmp/dotnet-install.sh && \
    chmod +x /tmp/dotnet-install.sh && \
    /tmp/dotnet-install.sh --channel 8.0 --install-dir /usr/share/dotnet && \
    ln -s /usr/share/dotnet/dotnet /usr/local/bin/dotnet && \
    rm /tmp/dotnet-install.sh

# Mono Runtime (eski .NET Framework kodları için)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    mono-runtime && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ==============================================================================
# 4. GITHUB CLI (GitHub Classroom Entegrasyonu)
# ==============================================================================
# Öğrencilerin terminalden "gh" komutlarını kullanabilmesi için.
RUN mkdir -p -m 755 /etc/apt/keyrings && \
    wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null && \
    chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ==============================================================================
# 5. ÖĞRENCİ KULLANICISI (Güvenlik)
# ==============================================================================

# Root yerine kısıtlı yetkiye sahip "student" kullanıcısı oluşturulur.

RUN useradd -m -s /bin/bash -G sudo student && \
    echo "student:student" | chpasswd && \
    echo "student ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Çalışma dizini oluşturulur
RUN mkdir -p /workspace && chown -R student:student /workspace

# ==============================================================================
# 6. C# ARAÇLARI VE TERMİNAL AYARLARI
# ==============================================================================
USER student
WORKDIR /home/student
ENV PATH="${PATH}:/home/student/.dotnet/tools"

# C# kodunu otomatik düzenleyen araçlar (dotnet format)
RUN dotnet tool install --global dotnet-format && \
    dotnet tool install --global csharpier

# Terminalin renkli görünmesi ve Git branch ismini göstermesi için ayarlar
USER root
RUN echo '\n# Renkli Prompt Ayarı' >> /etc/bash.bashrc && \
    echo 'parse_git_branch() { git branch 2> /dev/null | sed -e "/^[^*]/d" -e "s/* \(.*\)/ (\1)/"; }' >> /etc/bash.bashrc && \
    echo 'export PS1="\[\033[01;32m\]\u@codespace\[\033[00m\]:\[\033[01;34m\]\w\[\033[01;33m\]\$(parse_git_branch)\[\033[00m\]\$ "' >> /etc/bash.bashrc && \
    echo 'alias ll="ls -lah"' >> /etc/bash.bashrc && \
    echo 'alias cls="clear"' >> /etc/bash.bashrc

# Son Temizlik
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/*

# Container Başlatma Ayarları
WORKDIR /workspace
USER student
CMD ["/bin/bash"]

# Mono ve C# Derleyicisi (mcs) kurulumu
USER root
RUN apt-get update && apt-get install -y mono-devel mono-complete && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
USER student
