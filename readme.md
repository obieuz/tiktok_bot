# Reddit to TikTok Video Bot

Automatyzacja tworzenia krótkich filmów na TikToka na podstawie historii pobieranych z Reddita. Projekt łączy integrację z API Reddita, syntezę mowy, automatyczne generowanie napisów oraz przygotowanie filmu w formacie gotowym do publikacji.

## Jak działa projekt

1. Aplikacja uwierzytelnia się w Reddit API i pobiera historię z wybranego subreddita.
2. Sprawdza, czy historia nie została wcześniej przetworzona i czy ma odpowiednią długość.
3. Biblioteka `pyttsx3` zamienia tekst historii na mowę.
4. `faster-whisper` analizuje wygenerowany dźwięk i tworzy zsynchronizowane napisy w formacie SRT.
5. MoviePy łączy mowę, napisy i materiał wideo w jeden plik MP4.
6. Moduł TikTok zawiera obsługę OAuth oraz wysyłania filmu przez TikTok Content Posting API.

Przetworzone historie są zapisywane w `resources/stories.json`, dzięki czemu aplikacja nie wykorzystuje ponownie tych samych postów. Obecny punkt wejścia (`main.py`) domyślnie generuje film. Wywołanie uploadu do TikToka jest przygotowane w kodzie i może zostać włączone po skonfigurowaniu autoryzacji TikTok.

## Technologie

- Python 3.9–3.11
- Reddit OAuth API
- TikTok Content Posting API
- `requests` do komunikacji z API
- `pyttsx3` do syntezy mowy
- `faster-whisper` do generowania napisów na podstawie audio
- MoviePy do montażu wideo
- `translate` do opcjonalnego tłumaczenia tekstu

## Wymagania

- Python w wersji od 3.9 do 3.11
- FFmpeg dostępny w systemie lub skonfigurowany zgodnie z wymaganiami MoviePy
- Konto Reddit z aplikacją OAuth
- Aplikacja TikTok z dostępem do Content Posting API
- Głos systemowy obsługiwany przez `pyttsx3`

## Konfiguracja

Utwórz w głównym katalogu projektu plik `.env.local` i uzupełnij go własnymi danymi:

```env
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_SECRET=your_reddit_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

TIKTOK_CLIENT_ID=your_tiktok_client_id
TIKTOK_SECRET=your_tiktok_secret
TIKTOK_REDIRECT_URL=https://your-domain.example/callback
```

Plik `.env.local` zawiera dane uwierzytelniające i nie powinien być dodawany do repozytorium. Jest już uwzględniony w `.gitignore`.

## Instalacja

W PowerShellu:

```powershell
py -3.10 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Można użyć dowolnej wersji Pythona od 3.9 do 3.11, na przykład `py -3.9`, `py -3.10` lub `py -3.11`.

## Uruchomienie

Po aktywowaniu środowiska wirtualnego uruchom:

```powershell
python main.py
```

Wygenerowany film zostanie zapisany jako `video.mp4`. Do działania pipeline'u wymagane są pliki wejściowe znajdujące się w katalogu `resources/`, w szczególności materiał tła oraz font używany do napisów.

## Upload na TikToka

Moduł `functions/tiktok.py` obsługuje:

- pobieranie tokenu OAuth,
- pobieranie adresu uploadu,
- dzielenie pliku na części zgodnie z wymaganiami TikTok API,
- wysyłanie pliku MP4.

Podczas autoryzacji TikTok aplikacja może poprosić o kod zwrócony na skonfigurowany adres redirect. Przed włączeniem publikacji należy skonfigurować aplikację TikTok i odpowiednie uprawnienia API.

## Struktura projektu

```text
main.py                  # punkt wejścia aplikacji
settings.py              # konfiguracja aplikacji i odczyt .env.local
requirements.txt         # zależności Pythona
functions/
	reddit.py              # pobieranie i śledzenie historii z Reddita
	video.py               # synteza mowy, napisy i montaż filmu
	tiktok.py              # autoryzacja i upload do TikToka
resources/
	stories.json           # historia przetworzonych postów
	subtitles.srt          # wygenerowane napisy
	fonts/                 # font używany przez MoviePy
```
