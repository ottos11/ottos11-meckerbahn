# Meckerbahn

Android-App für Beschwerden zu U-Bahn, S-Bahn, Stadt- und Straßenbahn. Die Schwester-App der Meckerlinie (Bus).

Gemeldet werden können:

- **Fahrplan:** Zug zu spät, ausgefallen oder zu früh abgefahren
- **Im Zug oder an der Haltestelle:** Belästigung, Betteln, Gestank, Dreck

So läuft eine Meldung ab:

1. Art des Vorfalls wählen. Bei Belästigung, Betteln, Gestank und Dreck zusätzlich: im Zug oder an der Haltestelle, und was genau.
2. Standort verwenden oder die Haltestelle über ihren Namen suchen. Datum und Uhrzeit lassen sich ändern.
3. Im Zug: Linie, Richtung und Abfahrt aus dem Fahrplan wählen, optional die Wagennummer. An der Haltestelle: angeben, welche Bahn dort hält, optional die genaue Stelle.
4. Bis zu drei Fotos anhängen, Beschwerde prüfen und per Mail-App oder Kontaktformular abschicken.

Der Verlauf sammelt alle Vorfälle nach Linie und Haltestelle. Frühere Fälle stehen in der nächsten Mail, ab zwei Vorfällen gibt es eine Sammelbeschwerde.

Fahrplan- und Echtzeitdaten kommen von [Transitous](https://transitous.org/). Name, Verlauf und Einstellungen bleiben auf dem Gerät. Fotos speichert die App nicht, sie verlassen das Handy nur als Anhang der Mail oder per Upload im Formular.

## Städte

Die App erkennt die Stadt am Standort und schickt die Beschwerde an den zuständigen Betrieb. Hinterlegt sind:

| Stadt | Bus | U-, Stadt- und Straßenbahn | S-Bahn |
|---|---|---|---|
| Hamburg | HOCHBAHN, VHH (Mail) | HOCHBAHN (Mail) | S-Bahn Hamburg (Mail) |
| Berlin | BVG (Mail) | BVG (Mail) | S-Bahn Berlin (Formular) |
| München | MVG (Formular) | MVG (Formular) | S-Bahn München (Formular) |
| Köln | KVB (Formular) | KVB (Formular) | DB Regio NRW (Formular) |
| Frankfurt | RMV-Serviceportal (Formular) | RMV-Serviceportal (Formular) | RMV-Serviceportal (Formular) |
| Augsburg | swa (Mail) | swa, Straßenbahn (Mail) | – |

Bei Betrieben mit Formular kopiert die App den Text und öffnet das Formular. In anderen Städten funktioniert die App auch, die Adresse des Betriebs trägt man dann einmal selbst ein. Die Stadt lässt sich unter Einstellungen auch fest einstellen.

Neue Stadt: Eintrag in `www/cities.js` ergänzen. Welche Namen der Fahrplandienst für die Betriebe einer Stadt verwendet, zeigt der Workflow „Betreiber auflisten“ im Repo der Meckerbahn.

## Gemeinsamer Code

Meckerlinie und Meckerbahn teilen sich `www/index.html` und `www/cities.js`. Nur `www/app.js` legt fest, welche App gebaut wird. Änderungen an den beiden gemeinsamen Dateien gehören in beide Repos.

## APK herunterladen

Bei jedem Push auf `main` baut GitHub Actions automatisch eine neue APK.

1. Im Repo rechts auf **Releases** gehen.
2. `meckerbahn.apk` auf dem Handy herunterladen und installieren, oder das Repo in Obtainium eintragen.

Jede APK wird mit demselben Schlüssel signiert (`signing/debug.keystore`, Standard-Passwort `android`), damit sich neue Versionen als Update installieren lassen.

## Aufbau

- `www/index.html`: die komplette App (HTML, CSS, JavaScript), gemeinsam mit der Meckerlinie
- `www/cities.js`: Städte, Betriebe und Beschwerdeadressen
- `www/app.js`: legt fest, dass die Meckerbahn gebaut wird
- `www/fonts/`: Schrift Barlow (SIL Open Font License)
- `capacitor.config.json`: App-Name und Paket-ID
- `scripts/patch-android.sh`: ergänzt GPS-Rechte, Farben und das App-Symbol im Android-Projekt
- `.github/workflows/build-apk.yml`: baut die APK

Fotos hängt die App über das Plugin `capacitor-email-composer` an die Mail. Das Android-Projekt (`android/`) wird beim Build jedes Mal neu erzeugt und liegt deshalb nicht im Repo.
