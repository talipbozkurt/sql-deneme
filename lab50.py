import os
import sys
import importlib.util
import subprocess
import re
import sqlite3

class MockRunner:
    def __init__(self, command):
        self.command = command
        self.input_queue = []  # Girdileri sırayla tutmak için
        self.stdout_text = ""
        self.returncode = 0
        self.executed = False

    def stdin(self, data):
        """Öğrencinin koduna gönderilecek her bir girdiyi kuyruğa ekler."""
        self.input_queue.append(str(data))
        return self

    def stdout(self, *args):
        if not self.executed: self._decide_and_run()
        match_found = False
        for pattern in args:
            if not isinstance(pattern, str): continue
            # Hem Regex hem de normal string kontrolü
            if re.search(pattern, self.stdout_text, re.MULTILINE | re.IGNORECASE):
                match_found = True
                break
            if str(pattern).lower() in self.stdout_text.lower():
                match_found = True
                break
        
        if not match_found:
            raise Exception(f"Çıktı eşleşmedi.\nBeklenen: {args}\nGelen: {self.stdout_text.strip()[:200]}")
        return self

    def exit(self, code):
        if not self.executed: self._decide_and_run()
        if self.returncode != code:
            raise Exception(f"Hatalı Exit Code! Beklenen: {code}, Gelen: {self.returncode}")
        return self

    def _decide_and_run(self):
        if ".sql" in self.command:
            self._run_sql()
        else:
            self._run_process()

    def _run_sql(self):
        try:
            sql_file_match = re.search(r"(\w+\.sql)", self.command)
            db_file = "movies.db"
            if sql_file_match:
                with open(sql_file_match.group(1), 'r') as f:
                    query = f.read()
            else:
                query = self.command
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute(query)
            self.stdout_text = "\n".join([str(row[0]) for row in cursor.fetchall() if row])
            conn.close()
            self.executed = True
        except Exception as e:
            raise Exception(f"SQL Hatası: {e}")

    def _run_process(self):
        try:
            cmd_list = self.command.split()

            # AKILLI ÇALIŞTIRMA: .c yoksa ve .exe varsa mono ile çalıştır
            if cmd_list[0].startswith("./") or "/" not in cmd_list[0]:
                base_name = cmd_list[0].replace("./", "")
                if not os.path.exists(base_name) and os.path.exists(base_name + ".exe"):
                    cmd_list = ["mono", base_name + ".exe"] + cmd_list[1:]
                elif base_name.endswith(".exe") and sys.platform != "win32":
                    if "mono" not in cmd_list: cmd_list.insert(0, "mono")

            proc = subprocess.Popen(
                cmd_list, 
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )

            # Kuyruktaki girdileri \n ile birleştirip 'Enter' simülasyonu yapıyoruz
            input_str = "\n".join(self.input_queue) + "\n" if self.input_queue else None
            
            # Programı çalıştır ve girdileri gönder
            self.stdout_text, stderr_text = proc.communicate(input=input_str, timeout=5)
            self.returncode = proc.returncode
            
            if self.returncode != 0 and not self.stdout_text:
                self.stdout_text = stderr_text
            self.executed = True
        except Exception as e:
            raise Exception(f"Çalıştırma Hatası: {e}")

class MockCheck50:
    def __init__(self):
        self.c = self.C(self)
        self.csharp = self.CSharp()

    def check(self, *args, **kwargs):
        def decorator(func):
            func._is_check = True
            func._name = func.__name__
            func._points = kwargs.get('points', 0) # Varsayılan: 0 Puan (Sadece kontrol, puan yok)
            return func
        return decorator

    def exists(self, filename):
        if not os.path.exists(filename):
            alt_file = filename.replace(".c", ".cs")
            if not os.path.exists(alt_file):
                raise Exception(f"Dosya bulunamadı: {filename} (veya {alt_file})")

    def include(self, *args):
        pass

    def run(self, command):
        return MockRunner(command)

    class C:
        def __init__(self, parent):
            self.parent = parent

        def compile(self, filename, lcs50=False):
            if not os.path.exists(filename):
                cs_file = filename.replace(".c", ".cs")
                if os.path.exists(cs_file):
                    return self.parent.csharp.compile(cs_file)
                raise Exception(f"Dosya bulunamadı: {filename}")

            output = filename.replace(".c", "")
            cmd = ["clang", "-o", output, filename]
            if lcs50: cmd.append("-lcs50")
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"C Derleme Hatası:\n{res.stderr}")

    class CSharp:
        def compile(self, filename):
            output = filename.replace(".cs", ".exe")
            cmd = ["mcs", "-out:" + output, filename]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise Exception(f"C# Derleme Hatası:\n{res.stderr}")

    class Failure(Exception):
        def __init__(self, message):
            super().__init__(message)

    class Mismatch(Exception):
        def __init__(self, expected, actual):
            self.expected = expected
            self.actual = actual
            
            try:
                # Beklenen veriyi satırlarına ayır ve temizle
                exp_list = [line.strip() for line in str(expected).splitlines() if line.strip()]
                act_list = [line.strip() for line in str(actual).splitlines() if line.strip()]
                
                exp_set = set(exp_list)
                act_set = set(act_list)
                
                # Kesişim hesapla
                matches = exp_set.intersection(act_set)
                match_count = len(matches)
                total_expected = len(exp_set)
                
                percentage = 0
                if total_expected > 0:
                    percentage = (match_count / total_expected) * 100
                
                # Eksik olanlar
                missing = list(exp_set - act_set)
                missing.sort()
                
                # Fazla olanlar
                extra = list(act_set - exp_set)
                extra.sort()
                
                msg = f"\n\n📊 Test Analizi:\n---------------\n✅ Başarı: {match_count}/{total_expected} (%{percentage:.1f} Eşleşme)"
                
                if missing:
                    msg += f"\n❌ Eksik Olanlar ({len(missing)} adet):\n" + "\n".join([f"   - {m}" for m in missing[:5]])
                    if len(missing) > 5: msg += f"\n   ...ve {len(missing)-5} tane daha."
                
                if extra:
                    msg += f"\n⚠️ Fazladan Gelenler ({len(extra)} adet):\n" + "\n".join([f"   + {e}" for e in extra[:5]])
                    if len(extra) > 5: msg += f"\n   ...ve {len(extra)-5} tane daha."
                
                msg += f"\n\n📋 Tam Beklenen Liste:\n{str(expected)}\n\n📋 Sizin Çıktınız:\n{str(actual)}"
                
                super().__init__(msg)
            except Exception:
                # Hata durumunda (veya simple strings ise) standart mesaj
                super().__init__(f"\nBeklenen:\n{str(expected)}\n\nGerçekleşen:\n{str(actual)}")

mock_c50 = MockCheck50()

def reset_database():
    try:
        db_path = "movies.db"
        setup_sql_path = "setup.sql"
        
        if not os.path.exists(setup_sql_path):
            print(f"UYARI: {setup_sql_path} bulunamadı, veritabanı sıfırlanamadı!")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Mevcut tabloları temizle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table_name in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name[0]}")
            
        # setup.sql dosyasını oku ve çalıştır
        with open(setup_sql_path, "r") as f:
            sql_script = f.read()
        
        cursor.executescript(sql_script)
        conn.commit()
        conn.close()
        print("✅ Veritabanı başarıyla sıfırlandı ve setup.sql ile yeniden oluşturuldu.")
        
    except Exception as e:
        print(f"❌ Veritabanı sıfırlama hatası: {e}")

def run_local_test(test_folder):
    # Veritabanını sıfırla (Temiz test ortamı)
    reset_database()

    # Mock modüllerini sisteme tanıt
    sys.modules["check50"] = mock_c50
    sys.modules["check50.c"] = mock_c50.c
    sys.modules["check50.csharp"] = mock_c50.csharp

    init_path = os.path.join(test_folder, "__init__.py")
    if not os.path.exists(init_path):
        print(f"Hata: {init_path} bulunamadı!")
        return

    spec = importlib.util.spec_from_file_location("test_module", init_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    print(f"🚀 Yerel Test Motoru Başladı: {test_folder}\n" + "="*50)
    
    # Test fonksiyonlarını bul ve sırala
    test_funcs = [getattr(module, a) for a in dir(module) if hasattr(getattr(module, a), "_is_check")]
    test_funcs.sort(key=lambda x: 0 if x._name in ['exists', 'compiles'] else 1)

    earned_points = 0
    max_points = 0
    passed_count = 0
    total_count = len(test_funcs)

    for func in test_funcs:
        points = getattr(func, "_points", 0) # Puan tanımlı değilse 0 say
        max_points += points

        if points > 0:
            print(f"[*] {func._name:30} ({points} Puan)", end=" ")
        else:
            print(f"[*] {func._name:30} (Kontrol)", end=" ")

        try:
            func()
            print("✅ PASS")
            passed_count += 1
            earned_points += points
        except Exception as e:
            print(f"❌ FAIL\n    👉 {str(e)}")
    
    print("="*50)
    print("📊 TEST SONUÇLARI ÖZETİ")
    print("="*50)
    print(f"✅ Geçen Testler : {passed_count} / {total_count}")
    
    failed_count = total_count - passed_count
    if failed_count > 0:
        print(f"❌ Kalan Testler : {failed_count}")
        
    print(f"🏆 TOPLAM PUAN  : {earned_points} / {max_points}")
    print("="*50)
    
    if passed_count < total_count:
        print("\n⚠️  DİKKAT: Tüm testler geçmediği için 'Autograding' kırmızı işaretlenecektir.")
        print("    Bu normaldir. Tam puan aldığınızda yeşile dönecektir.")
        sys.exit(1)
    else:
        print("\n🎉 TEBRİKLER! Tüm testleri geçtiniz.")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python3 lab50.py <test_klasoru>")
    else:
        run_local_test(sys.argv[1])
