# Lviv Food Map · Katsurin & Ptushkin

Interaktywna mapa gastronomiczna Lwowa zbudowana wyłącznie z miejsc, które pokazali, odwiedzili lub polecili
**Misha Katsurin** (Міша Кацурін, restaurator, kanał YouTube „Міша Кацурін”) i **Anton Ptushkin** (Антон Птушкін, travel-bloger).

Stack: czysty HTML + CSS + JavaScript, [Leaflet 1.9.4](https://leafletjs.com/) (dołączony lokalnie w `vendor/`),
kafelki OpenStreetMap w stylu CARTO Voyager. **Bez API key, bez builda, bez frameworka.**

---

## Liczby (stan na 29.09.2026)

| | |
|---|---|
| Rekordów w bazie | **13** |
| Z potwierdzonymi współrzędnymi (markery) | **10** |
| Bez współrzędnych (tylko na liście, niepewna identyfikacja) | 3 |
| Status OPEN | 10 |
| Status CLOSED (historyczne) | 1 |
| Status UNKNOWN | 2 |
| Pewność źródła HIGH / MEDIUM / LOW | 7 / 5 / 1 |
| Bezpośrednie źródło Katsurin/Ptushkin (odcinek, TikTok, własny post, własna lista) | 13 |
| Wyłącznie ze źródeł wtórnych | 0 |

Kto polecał: Katsurin 6 · Ptushkin 4 · obaj 3.

Typ wzmianki: odwiedzone osobiście na kamerze 7 · lokal własny Katsurina 1 · polecone / na osobistej liście 5 · źródło wtórne 0.

> **Uwaga o kompletności.** Research prowadzono w środowisku, w którym polityka sieciowa blokowała pobieranie stron
> (YouTube, Instagram, TikTok, ukraińskie media, Wikipedia, Nominatim) i dopuszczała jedynie ograniczoną liczbę
> zapytań do wyszukiwarki (200 na sesję). W efekcie baza zawiera **wyłącznie lokale potwierdzone w streszczeniach
> wyników wyszukiwania**, a pełne listy z opisów odcinków nie zostały odczytane. Sekcja [„Do uzupełnienia”](#do-uzupełnienia)
> opisuje dokładnie, gdzie leży reszta danych. Nie dodano żadnego miejsca „na wyczucie”.

---

## Skąd pochodzą miejsca (źródła pierwotne)

### 1. „Їжа Львова. Великий гід” — 13.12.2022
YouTube, kanał Міша Кацурін: <https://www.youtube.com/watch?v=pX8CMh21Vz4> (nagrywany w sierpniu 2022, ok. 60 min).
Ważne: choć media zapowiadały odcinek jako wspólny, **Ptushkin nie pojawia się w kadrze** („поїхав знімати пеліканів” – ELLE).
Dlatego miejsca z tego odcinka są przypisane tylko Katsurinowi.

Potwierdzone lokale (każdy ma dodatkowo TikTok Katsurina z tagiem `#їжальвова`, często z adresem):
- **Ресторація Бачевських** (Шевська 8) — żurek po lwowsku
- **Дуже висока кухня** (пл. Ринок 14) — banosz z kurkami; *zamknięta / zmiana formatu (2024)*
- **Кафе «Єрусалим»** (Мечникова 39) — gefilte fisz, lwowska kuchnia żydowska
- **Правда** (пл. Ринок 32) — piwo; dziś „Pravda. Craft Beer & Friends”
- **Чебуречна в Брюховичах** (вул. Курортна) — czebureki

Segmenty odcinka, które **nie są lokalami** (nie ma ich na mapie): kuchnia Marianny Duszar (jaworowski pieróg),
kuchnia Pawła Hudimowa („обід в артпросторі”), przepis na sernik „бабці Дзюні”.

### 2. „Їжа України – Львів. Частина 2. ТОП-20” — 29.11.2024
Kanał Міша Кацурін, **obaj prowadzący**. Mirror z opisem: <https://liveam.tv/uk/izha-ukraini-29-11-2024.html>.
Relacja: БЖ, 03.12.2024 — <https://bzh.life/ua/gorod/1733229424-ptushkin-i-katsurin-vipustili-drugiy-gid/>.

Z ~20 miejsc udało się nazwać:
- **Цукерня** (Староєврейська 3) — desery według starych receptur (HIGH)
- **Мрійники** — lokal szefa Олександра Цвігуна (jadalne „kaczuszki” z pianki); identyfikacja lokalu pośrednia (MEDIUM, bez adresu)
- **Epic Cheeseburger** — „сирна ванна”; identyfikacja po unikalnym formacie (MEDIUM, sieć, bez adresu)

### 3. Lista Foursquare Antona Ptushkina „Львов” (09.2014)
<https://foursquare.com/ptuxerman> — 6 zapisanych miejsc, widoczne 4: **Гасова лямпа**, **Під Золотою Розою**, **Дім легенд**, **Music Lab**.
To słaba forma rekomendacji (prywatna lista bez komentarza), oznaczona jako „polecone”, pewność MEDIUM/LOW.

### 4. Lokal własny Katsurina
**Китайський Привіт** (Миколи Вороного 3), otwarty 13.07.2025; masowe zatrucie salmonellą 3 dni po otwarciu,
grzywna 48 tys. UAH, ponowne otwarcie 05.08.2025. Źródła: Instagram Katsurina, NV, ZAXID.NET, The Village.

### Co sprawdzono i nie dało lokali we Lwowie
- „Їжа Галичини” (03.2024, <https://www.youtube.com/watch?v=9w8aKVi5vl8>) — tylko Iwano-Frankiwsk, Kołomyja, Tarnopol i obwód lwowski (nienazwany hotel), zero lokali w mieście.
- Własny kanał Ptushkina (@ptuxermann), wywiady (24tv, RBC, NV, Forbes), relacje z festiwali — brak lwowskich rekomendacji gastronomicznych.
- Instagram/TikTok/Telegram Katsurina poza `#їжальвова` — nic lwowskiego poza własnym lokalem i strefą „Japanese Street Food” na festiwalu Дні Японії (09.2026, pop-up, nie lokal).
- Lista ~25 „oczywistych” lwowskich lokali (Кумпель, Криївка, Львівська майстерня шоколаду, Пструг, Bernardyn, LEM Station, Jam Factory, Світ кави, Manufaktura, Atlas, Ribs itd.) — **żaden nie ma potwierdzenia** w powiązaniu z Katsurinem/Ptushkinem, więc żadnego nie dodano.

---

## Metodologia

1. **Zbieranie.** Zapytania w trzech językach (UA/RU/EN, m.in. „Кацурін Львів де поїсти”, „Кацурин Львов рестораны”, „Птушкін Львів їжа”, „Katsurin Lviv food”), rozdzielone na 4 równoległe wątki: odcinek 2022, odcinek 2024, pozostałe treści Katsurina, treści Ptushkina.
2. **Kryterium włączenia.** Miejsce trafia do bazy tylko, gdy w źródle pierwotnym (odcinek, TikTok/Instagram twórcy, jego lista) lub w relacji medialnej z odcinka pada **nazwa lokalu** albo **jednoznaczny wyróżnik** (np. „сирна ванна” = Epic Cheeseburger). Anonimowe segmenty („кілька піцерій”, „рамен”) nie są mapowane.
3. **Deduplikacja.** Rekord = jeden lokal; zmiany nazw zapisane w `name_uk` i `notes` (np. Театр пива «Правда» → Pravda. Craft Beer & Friends). Dla sieci bez wskazanej filii rekord nie ma współrzędnych.
4. **Weryfikacja statusu.** Osobne zapytania o zamknięcia/zmiany formatu dla każdego lokalu (np. NV o „Дуже висока кухня”; ZAXID/NV/The Village o „Китайський Привіт”).
5. **Współrzędne.** Nominatim/Google były niedostępne; lat/lng przypisano ręcznie z adresów na podstawie siatki ulic Starego Miasta (dokładność ok. 30–80 m, w Brzuchowicach mniejsza). Przed wizytą kliknij „Open in Google Maps”.
6. **Grupy.** Każdy rekord ma `mention_type`: `visited` (pokazane na kamerze), `recommended` (polecone / osobista lista), `own` (lokal własny), `secondary` (przypisywane przez osoby trzecie). Domyślnie mapa pokazuje `visited`, `recommended` i `own`; `secondary` włącza się przełącznikiem (obecnie 0 rekordów).

---

## Uruchomienie

Najprościej: otwórz `index.html` w przeglądarce (działa z `file://`, bo dane są w `data/places.js`).

Z lokalnym serwerem (zalecane dla mobile na tej samej sieci):

```bash
cd lviv-food-map
npm start          # generuje dane i serwuje na http://localhost:5173
# albo bez npm:
python3 -m http.server 5173
```

Kafelki mapy ładują się z internetu (CARTO/OSM); cała reszta działa offline.

## Aktualizacja danych

Jedynym źródłem prawdy jest **`data/places.json`**. Po edycji uruchom:

```bash
npm run build-data      # = node scripts/build-data.js
```

Skrypt waliduje rekordy (kategorie, statusy, współrzędne w granicach Lwowa, brak duplikatów `id`) i generuje
`data/places.js` (dla UI) oraz `data/lviv-katsurin-ptushkin-map.csv` (Google My Maps).

Schemat rekordu:

```json
{
  "id": "unikalny-slug",
  "name": "Latin/English name",
  "name_uk": "Назва українською",
  "address": "вул. …, Львів",
  "lat": 49.84, "lng": 24.03,
  "category": "restaurant | cafe | breakfast | streetfood | ukrainian | galician | finedining | bakery | bar | other",
  "tags": ["dodatkowe kategorie z tej samej listy"],
  "recommended_by": ["katsurin", "ptushkin"],
  "mention_type": "visited | recommended | secondary | own",
  "visited": true,
  "recommended_items": ["danie / produkt"],
  "description": "krótki opis",
  "google_maps": "https://www.google.com/maps/search/?api=1&query=LAT,LNG",
  "website": null, "instagram": null,
  "sources": [{"title": "…", "url": "…", "type": "video | article | social", "date": "YYYY-MM-DD"}],
  "status": "open | closed | unknown",
  "confidence": "high | medium | low",
  "notes": "zastrzeżenia, zmiany nazw/adresów"
}
```

Rekordy z `lat`/`lng` = `null` pojawiają się na liście (z etykietą „brak lokalizacji”), ale nie jako marker;
ich link do Google Maps to wyszukiwanie po nazwie.

## Import CSV do Google My Maps

1. Wejdź na <https://www.google.com/mymaps> → **Utwórz nową mapę**.
2. W warstwie kliknij **Importuj** i wskaż `data/lviv-katsurin-ptushkin-map.csv` (UTF-8 z BOM, cyrylica działa poprawnie).
3. Jako kolumny położenia wybierz **Latitude** i **Longitude** (nie „Address”).
4. Jako tytuł znacznika wybierz **Name** (lub **Ukrainian Name**).
5. Opcjonalnie: „Styl” → grupuj według **Category** lub **Recommended By**.

Wiersze bez współrzędnych (3) Google pominie lub oznaczy jako błędne — możesz je usunąć z CSV albo uzupełnić po weryfikacji adresu.

---

## Do uzupełnienia

Pełne listy lokali istnieją, ale nie były osiągalne z tego środowiska. Aby domknąć bazę, wystarczy otworzyć w przeglądarce:

1. **Opis odcinka 2022** — <https://www.youtube.com/watch?v=pX8CMh21Vz4> (Katsurin zawsze podaje listę lokali z adresami w opisie). Brakujące: pierożki, croissanty, bulbianka/paluszki/kulisz, „lokalny fine dining”.
2. **Opis odcinka TOP-20 (2024)** na kanale <https://www.youtube.com/@misha_katsurin> lub post **@i_sho_kuda_lviv „Що їли та пили Кацурін і Птушкін у Львові”** — <https://www.instagram.com/i_sho_kuda_lviv/p/DDFF-ddt3qH/>. Brakujące: kurczak z grilla z winem musującym, tacos „meksykańsko-lwowskie”, ramen, kilka pizzerii, kilogramowe hot-dogi, lody, stek rocznej dojrzałości za 4500 UAH, kuchnia indyjska, wegańska lasagna, bar z winem naturalnym, bacalao, adres „Мрійників” i konkretna filia Epic Cheeseburger.
3. **Instagram** <https://www.instagram.com/p/DGnFWcPNPOD/> („Заклади, які відвідали Михайло Кацурін…”, ~03.2025) — potencjalna lista, miasto niepotwierdzone.
4. Pozostałe 2 miejsca z listy Foursquare Ptushkina i adres/status **Music Lab**.

Miejsca o **niepewnej identyfikacji** (obecnie w bazie, oznaczone w `notes`): Мрійники (potwierdzony szef, nie nazwa lokalu),
Epic Cheeseburger (identyfikacja po formacie), Music Lab (brak adresu i statusu), Чебуречна (rozbieżne numery przy Курортній).

## Struktura

```
lviv-food-map/
├── index.html
├── styles.css
├── app.js
├── package.json                # npm start / npm run build-data
├── scripts/build-data.js       # walidacja + generowanie places.js i CSV
├── vendor/leaflet/             # Leaflet 1.9.4 (offline)
└── data/
    ├── places.json             # źródło prawdy
    ├── places.js               # generowane
    └── lviv-katsurin-ptushkin-map.csv   # generowane, import do Google My Maps
```

Licencje: Leaflet (BSD-2), dane map © OpenStreetMap contributors (ODbL), kafelki © CARTO.
