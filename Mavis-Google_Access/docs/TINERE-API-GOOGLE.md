# TINERE API GOOGLE - gazde, drumuri, scope-uri

Tot ce e mai jos e luat din **discovery documents** (nu din memorie), pe 27
oct 2026. Metoda: `https://<gazda>/$discovery/rest?version=<v>`.

## Gazde (măsurat: `www.googleapis.com` nu ajunge la toate)

| API | Gazdă | Bază |
|---|---|---|
| Drive | `https://www.googleapis.com` | `/drive/v3` |
| Gmail | `https://gmail.googleapis.com` | `/gmail/v1` |
| Calendar | `https://www.googleapis.com` | `/calendar/v3` |
| Books | `https://www.googleapis.com` | `/books/v1` |
| Docs | `https://docs.googleapis.com` | `/v1/documents` |
| Sheets | `https://sheets.googleapis.com` | `/v4/spreadsheets` |
| Slides | `https://slides.googleapis.com` | `/v1/presentations` |
| Forms | `https://forms.googleapis.com` | `/v1/forms` |
| Photos Library | `https://photoslibrary.googleapis.com` | `/v1/mediaItems` |
| Tasks | `https://tasks.googleapis.com` | `/tasks/v1` |
| Apps Script | `https://script.googleapis.com` | `/v1/projects` |
| Chat | `https://chat.googleapis.com` | `/v1/spaces` |
| YouTube | `https://youtube.googleapis.com` | `/youtube/v3` |
| People (Contacts) | `https://people.googleapis.com` | `/v1/people/me/connections` |
| Keep | `https://keep.googleapis.com` | `/v1/notes` |
| Sites | `https://sites.googleapis.com` | `/v1/sites` (API retras) |

## Drumuri reale ale metodelor care le folosim

| Metodă | Drum | Note |
|---|---|---|
| `drive.files.list` | `GET /drive/v3/files` | `q`, `fields`, `pageSize` |
| `drive.files.create` | `POST /drive/v3/files` | multipart pentru conținut |
| `drive.files.export` | `GET /drive/v3/files/{id}/export?mimeType=…` | Docs → text, Sheets → csv |
| `gmail.users.messages.list` | `GET /gmail/v1/users/me/messages` | |
| `gmail.users.messages.get` | `GET /gmail/v1/users/me/messages/{id}?format=full` | |
| `calendar.events.list` | `GET /calendar/v3/calendars/primary/events` | |
| `documents.get` | `GET /v1/documents/{documentId}` | |
| `documents.batchUpdate` | `POST /v1/documents/{id}:batchUpdate` | |
| `spreadsheets.values.get` | `GET /v4/spreadsheets/{id}/values/{range}` | |
| `photoslibrary.mediaItems.list` | `GET /v1/mediaItems?pageSize=…` | **`/v1/photos` nu există** |
| `photoslibrary.albums.list` | `GET /v1/albums` | |
| `tasks.tasklists.list` | `GET /tasks/v1/users/@me/lists` | |
| `chat.spaces.list` | `GET /v1/spaces` | cere `chat.spaces.readonly` |
| `youtube.channels.list` | `GET /youtube/v3/channels?part=…&mine=true` | `channels/mine` nu e listat în discovery |
| `people.connections.list` | `GET /v1/people/me/connections?personFields=…` | |
| `script.projects.*` | `GET /v1/projects/{scriptId}` | **nu există `projects.list`** → listarea se face prin Drive (mimeType `application/vnd.google-apps.script`) |

## Scope-uri pentru care API-ul chiar cere altceva

| Metodă | Scope-uri acceptate (din discovery) |
|---|---|
| `photoslibrary.mediaItems.list` | `photoslibrary`, `photoslibrary.readonly`, `photoslibrary.readonly.appcreateddata` |
| `chat.spaces.list` | `chat.bot`, `chat.spaces`, `chat.spaces.readonly` |

## Scope-uri inexistente (nu se pot cere)

| Scope | De ce |
|---|---|
| `https://www.googleapis.com/auth/sites` | API-ul Google Sites a fost retras; scope-ul a ieșit din registrul Google (consola: „not added because they are invalid") |
| `https://www.googleapis.com/auth/keep` | Keep API există (Developer Preview, doar admini de workspace), dar scope-ul nu e în registrul public de scope-uri Google → invalid la cerere |

## API-uri activate în proiect (27 oct 2026)

`drive`, `gmail`, `calendar`, `docs`, `sheets`, `slides`, `forms`,
`photoslibrary`, `tasks`, `script`, `youtube`, `keep`, `people`, `contacts`,
`books` (activat de mine), `chat` (activat de mine). **`sites.googleapis.com`
nu există ca serviciu** - nu poate fi activat.

## Regula

Înainte de a folosi o metodă de API: verific-o în discovery document. Un drum
ghicit înseamnă un 404 măsurat - și un 404 care arată la fel ca o lipsă de
scope.

## Photos după 31 martie 2025 - ce mai există și ce nu

Măsurat pe contul real (27 oct 2026, `scripts/probe-photos.mjs`):
`mediaItems.list` și `albums.list` răspund `403 Request had insufficient
authentication scopes`, **deși** tokenul duce `photoslibrary`,
`photoslibrary.readonly` și `photoslibrary.appendonly`, API-ul e activ în
proiectul clientului OAuth, contul e personal și are bibliotecă reală, iar
același token răspunde 200 pe Drive (control).

Cauza, din documentația oficială
(https://developers.google.com/photos/library/guides/authorization):

> photoslibrary.readonly / photoslibrary.sharing / photoslibrary
> Warning: These scopes are being removed as part of the updates to the Google
> Photos APIs. After March 31, 2025, you will only be able to access content
> created by your application.

Discovery-ul v1 confirmă în descrierile metodelor: `mediaItems.list` = „List
all media items **created by your app**", `albums.list` = „Lists all albums
**created by your app**".

| Scope | Stare pe 27 oct 2026 |
|---|---|
| `photoslibrary` | acordat, dar **nu mai deschide** biblioteca utilizatorului |
| `photoslibrary.readonly` | acordat, dar **nu mai deschide** biblioteca utilizatorului |
| `photoslibrary.appendonly` | **activ și dovedit**: creează album și încarcă media în biblioteca reală (probă fără creare: `POST /v1/albums` cu corp gol -> 400 „Request must have a title for the album.", deci autorizarea a trecut) |
| `photoslibrary.readonly.appcreateddata` | **acordat** la 12:06 (consimțământul #3) - citire doar a conținutului creat de aplicație |
| `photoslibrary.edit.appcreateddata` | **acordat** la 12:06 (consimțământul #3) - editare conținut creat de aplicație |
| `photospicker.mediaitems.readonly` | **acordat și FUNCTIONAL** (consimțământul cu scope nou, 27 oct 2026) - corectat 13:29: afirmația veche („cere un `pollingUri` public") era depășită; API-ul curent **nu** cere `pollingUri` |

Regula rămâne: înainte de a folosi o metodă de API - verific-o în discovery
document și în data retragerii din documentație, nu din memorie.

## Photo Picker API - singura cale de citit biblioteca utilizatorului

Măsurat 27 oct 2026 (nu din documentație):

| Punct | Măsurătoare |
|---|---|
| gazdă | `https://photospicker.googleapis.com` (API deja activat în proiect) |
| scope | `https://www.googleapis.com/auth/photospicker.mediaitems.readonly` |
| creare sesiune | `POST /v1/sessions` cu `{"pickingConfig":{"maxItemCount":"2000"}}` → `HTTP=200` |
| răspuns | `pickerUri` (URL de deschis în browserul autentificat), `expireTime`, `polling.pollInterval=5s` |
| citire | `GET /v1/sessions/{id}` → `mediaItemsSet`; `GET /v1/mediaItems?sessionId=…` → itemele alese |
| curățenie | `DELETE /v1/sessions/{id}` - API-ul cere ca sesiunile să nu se acumuleze |
| **nu cere** | `pollingUri` public - documentația veche din acest repo era depășită |

Uneltele: `gphotos_picker_start` (creează sesiunea, întoarce `picker_uri`) și
`gphotos_picker_result` (citește itemele alese; șterge sesiunea când nu mai
există `nextPageToken`).

**Ce nu poate fi automatizat, prin design:** selectarea pozelor e o acțiune a
utilizatorului în interfața Google (`picker_uri`). API-ul e construit ca
„utilizatorul alege ce îți dă voie să citești". Un agent nu poate apăsa în
selectarea din contul altcuiva - și nici nu ar trebui.

Sesiune măsurată prin container: `c39d0b83-90b2-49a2-bc64-29dd63db92c0`,
`expire_time=2026-11-03T11:28:05Z`. O sesiune anterioară, creată de pe host:
`71f24e8b-7223-48a7-91eb-7c699a46322c`.

**Defect reparat pe drum (măsurat):** după lărgirea consimțământului, containerul
răspundea `403 insufficient authentication scopes` deși scope-ul era acordat -
tokenul de acces era în cache din grantul vechi. Cache-ul poartă acum amprenta
credentialului (`credentialFingerprint`) și se invalidează la schimbare.

