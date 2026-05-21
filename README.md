# 📊 Portfolio Tracker

Automatyczny codzienny raport dla 21 pozycji — kursy, trendy, newsy.  
Aktualizuje się codziennie o 18:00 (czas polski). Hosting na GitHub Pages.

---

## ⚙️ Uruchomienie (jednorazowa konfiguracja ~10 minut)

### Krok 1 — Załóż konto GitHub
Wejdź na [github.com](https://github.com) → **Sign up** → załóż konto (email + hasło).

### Krok 2 — Utwórz repozytorium
1. Po zalogowaniu kliknij **+** (prawy górny róg) → **New repository**
2. Nazwa: `portfolio-tracker` (lub dowolna)
3. Ustaw **Public** (wymagane dla darmowego GitHub Pages)
4. Kliknij **Create repository**

### Krok 3 — Wgraj pliki
W nowym repo kliknij **Add file → Upload files** i wgraj:
```
.github/workflows/weekly.yml
scripts/generate.py
README.md
```
> Uwaga: folder `.github` zaczyna się od kropki — upewnij się że jest widoczny.  
> Na Windows możesz go zobaczyć przez `Ctrl+H` w eksploratorze plików.

Alternatywnie możesz użyć GitHub Desktop (prostszy interfejs) — pobierz z [desktop.github.com](https://desktop.github.com).

### Krok 4 — Włącz GitHub Pages
1. W repozytorium → **Settings** → **Pages** (lewy panel)
2. Source: **Deploy from a branch**
3. Branch: **main** / folder: **/ (root)**
4. Kliknij **Save**

Po kilku minutach dostaniesz adres: `https://TWOJA-NAZWA.github.io/portfolio-tracker/`

### Krok 5 — Pierwsze uruchomienie (test)
Nie czekaj do niedzieli — odpal ręcznie:
1. Zakładka **Actions** w repo
2. Kliknij **Weekly Portfolio Update** (lewy panel)
3. **Run workflow** → **Run workflow**
4. Po ~2 minutach odśwież stronę GitHub Pages

---

## 📋 Co pokazuje raport

Dla każdej z 21 pozycji:
- 💰 **Aktualna cena** + zmiana procentowa dziś
- 📈 **Sparkline** — mini wykres ostatnich 60 sesji
- 📊 **Statystyki**: zmiana tygodniowa, miesięczna, % od 52W max, zakres 52W
- 🔼 **Trend** (SMA20 vs SMA50): Wzrostowy / Boczny / Spadkowy
- 📰 **3 ostatnie newsy** z Google News (klikalne linki)

---

## 🕐 Harmonogram

Aktualizacja automatyczna: **co niedziela 18:00 (czas polski)**  
Ręczna aktualizacja: zakładka **Actions** → **Run workflow**

---

## 🛠️ Modyfikacje

Chcesz zmienić godzinę? Edytuj `.github/workflows/weekly.yml`:
```yaml
- cron: '0 16 * * 0'   # format: minuta godzina dzień miesiąc dzień_tygodnia
```
Przykłady:
- `'0 6 * * 1'`  — poniedziałek 8:00 (czas polski, latem UTC+2)
- `'0 15 * * 5'` — piątek 17:00

Chcesz dodać spółkę? Edytuj `scripts/generate.py`, sekcja `PORTFOLIO` na górze pliku.
