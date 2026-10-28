---
name: mavis-cloud-skill-calendar
description: Capabilitatea Calendar a botului mavis-cloud-google-access-bot. Cum listez calendare, creez, actualizez si sterg evenimente din Mavis Cloud. Trigger-uri: "calendar", "eveniment", "agenda", "programare", "disponibilitate", "meeting".
---

# Calendar — evenimente din cloud

Scope-uri: `calendar` (citit) · **`calendar.events`** (scriere) — ambele în token.

## Ce e măsurat ca funcțional (28 oct 2026)

| Operație | Endpoint | Rezultat măsurat |
|---|---|---|
| listare calendare | `GET calendar/v3/users/me/calendarList` | 4 calendare |
| listare evenimente | `GET .../calendars/{id}/events?singleEvents=true&orderBy=startTime` | ✅ |
| **create** | `POST .../calendars/{id}/events` | ✅ id returnat |
| **read back** | `GET .../calendars/{id}/events/{eventId}` | ✅ |
| **update** | `PATCH .../calendars/{id}/events/{eventId}` | ✅ summary modificat |
| delete | `DELETE .../calendars/{id}/events/{eventId}` | ✅ |

## API-ul

```js
// listare
const cals = await kit.calendar.list();            // cals.items[]
const evs  = await kit.calendar.events(calId, 50);

// creare — datele trebuie ISO 8601 cu Z sau offset
const ev = await kit.calendar.insert(calId, {
  summary: 'Titlu',
  description: 'Corp',
  start: { dateTime: '2026-10-28T10:00:00Z' },
  end:   { dateTime: '2026-10-28T10:30:00Z' },
});

// actualizare — PATCH partial
await kit.req('PATCH', `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(calId)}/events/${evId}`, {
  summary: 'Titlu nou',
});
```

## Ce măsurat la POPY

- `apvizual@gmail.com` — calendarul principal (4 calendare în total)
- `Family` · `Holidays in Romania` · `Sărbători în România`

## Capcane

- **`dateTime` fără fus** → evenimentul plouă în altă zonă. Folosește întotdeauna
  `Z` sau `+03:00` explicit. `date` (fără oră) e „toată ziua".
- **`singleEvents=true`** → evenimentele recurente sunt expandate. Fără, primești
  seria, nu instanțele.
- **`orderBy=startTime`** cere `singleEvents=true`, altfel 400.
- **Calendarul țintă** — nu presupune că e primul din listă. `items[0]` e
  calendarul principal *la POPY*, dar asta e o convenție, nu o garanție.

## Reguli

- **Nu mut evenimente existente** fără comanda explicită.
- Evenimentele create ca probe **se șterg** la final (sunt artefacte mele).
- Înainte să creez ceva pe calendarul lui POPY, verific dacă nu există deja
  (evit dubluri).
- Pentru orice workflow recurent: preferă **probe + raport**, nu scriere directă
  în calendarul lui.

## Legături

Skill central: `mavis-cloud-google-access-bot` · sibling: `mavis-cloud-skill-verification`
