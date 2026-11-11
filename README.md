# Fahrgastecho

Android-App für Beschwerden zu Bus und Bahn: Die App schreibt eine fertige Beschwerde und schickt sie an den zuständigen Verkehrsbetrieb.

Gemeldet werden können:

- **Die Fahrt:** zu spät gekommen, ausgefallen, zu früh abgefahren, gefährliche Fahrweise
- **Im Fahrzeug oder an der Haltestelle:** Belästigung, Betteln, Gestank, Dreck

So läuft eine Meldung ab:

1. Art des Vorfalls wählen. Bei Belästigung, Betteln, Gestank und Dreck zusätzlich: im Fahrzeug oder an der Haltestelle, und was genau.
2. Standort verwenden oder die Haltestelle über ihren Namen suchen. Datum und Uhrzeit lassen sich ändern.
3. Linie, Richtung und Abfahrt aus dem Fahrplan wählen. Die Haltestelle zeigt alle Linien, nach Bus, U-Bahn, S-Bahn und Tram sortiert. Bei Meldungen an der Haltestelle reicht die Angabe, was dort hält.
4. Beschwerde prüfen und per Mail-App oder Kontaktformular abschicken. Bei Dreck und Gestank lassen sich bis zu drei Fotos anhängen, Fotos von Menschen sind nicht vorgesehen.

„Meckern mit Maß“: Schritt 1 erinnert je nach Vorfall daran, was eine berechtigte Beschwerde ist. Bei einer Verspätung von höchstens drei Minuten weist die App vor dem Absenden darauf hin, dass das meist noch normal ist.

Zum Ausprobieren gibt es unter Einstellungen einen Testmodus: Dann gehen alle Beschwerden mit „[Test]“ im Betreff an die eigene Adresse statt an den Verkehrsbetrieb.

Der Verlauf sammelt alle Vorfälle nach Linie und Haltestelle. Frühere Fälle stehen in der nächsten Beschwerde, ab zwei Vorfällen gibt es eine Sammelbeschwerde.

Der Fahrplan kommt aus eigenen Fahrplandateien (siehe unten). Die Suche nach Haltestellen läuft auf dem Handy, der Standort verlässt es nicht. Name, Verlauf und Einstellungen bleiben auf dem Gerät. Fotos speichert die App nicht, sie verlassen das Handy nur als Anhang der Mail oder per Upload im Formular.

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

Bei Betrieben mit Formular kopiert die App den Text und öffnet das Formular. In anderen Orten funktioniert die App auch, Haltestelle, Linie und Adresse des Betriebs trägt man dann selbst ein. Die Stadt lässt sich unter Einstellungen auch fest einstellen.

Neue Stadt: Eintrag in `www/cities.js` ergänzen und den Workflow „Fahrplan aufbereiten“ von Hand starten. Welche Betriebe in der Stadt fahren und wie der Fahrplan sie nennt, steht danach im Zweig `fahrplan` in `manifest.json`.

## Fahrplandateien

Der Workflow „Fahrplan aufbereiten“ (`.github/workflows/fahrplan.yml`) lädt jeden Dienstag den Sollfahrplan Deutschland von DELFI (GTFS, rund 500 MB) und erzeugt mit `tools/fahrplan.py` kleine Dateien je Stadt: eine Liste aller Haltestellen und je Haltestelle die Abfahrten von Bus, U-, S- und Straßenbahn. Sie liegen im Zweig `fahrplan`, die App lädt nur die Haltestelle, die gerade gebraucht wird.

Die Dateien reichen 14 Tage zurück und 21 Tage voraus, damit sich Vorfälle auch nachträglich melden lassen. Echtzeit enthalten sie nicht: Ob ein Bus zu früh, zu spät oder gar nicht kam, beruht auf der Beobachtung der Fahrgäste.

Aufbereitet werden alle Städte aus `www/cities.js`. Beim Start von Hand lässt sich die Auswahl im Feld `staedte` eingrenzen.

Lizenz der Daten: DELFI e.V., CC BY 4.0. Die App nennt die Quelle unter „Über“.

## Gestaltung

Verkehrsbetriebe haben je Stadt eigene Farben, deshalb ist die App neutral: Schwarz auf hellem Grau und das Gelb des Haltestellenschilds, das bundesweit gleich ist. Linienschilder tragen die üblichen Zeichenfarben: Blau für U-Bahn, Grün für S-Bahn, sonst Schwarz.

## APK herunterladen

Bei jedem Push auf `main` baut GitHub Actions automatisch eine neue APK.

1. Im Repo rechts auf **Releases** gehen.
2. `fahrgastecho.apk` auf dem Handy herunterladen und installieren, oder das Repo in Obtainium eintragen.

Die Test-APK wird mit demselben Schlüssel signiert (`signing/debug.keystore`, Standard-Passwort `android`), damit sich neue Versionen als Update installieren lassen. Sie hat die Paket-ID `de.ottos11.meckerbahn` und ist nur zum Testen gedacht.

## Google Play

Derselbe Build erzeugt zusätzlich ein App-Bundle für Google Play (`fahrgastecho-play.aab`, unter Actions beim jeweiligen Lauf als Build-Ergebnis). Es hat die Paket-ID `de.ottos11.fahrgastecho` und ist mit dem Upload-Schlüssel signiert.

- Der Upload-Schlüssel liegt nur in den Repo-Secrets: `UPLOAD_KEYSTORE_BASE64` (die PKCS12-Datei als Base64, Alias `upload`) und `UPLOAD_KEY_PASSWORD`. Fehlen sie, wird nur die Test-APK gebaut.
- Den eigentlichen App-Signaturschlüssel verwaltet Google (Play App Signing). Geht der Upload-Schlüssel verloren, lässt er sich in der Play Console zurücksetzen.
- Ziel-Android-Version ist Android 16 (API 36), wie Google Play es für neue Apps verlangt.

## Aufbau

- `www/index.html`: die komplette App (HTML, CSS, JavaScript)
- `www/cities.js`: Städte, Betriebe und Beschwerdeadressen
- `www/fonts/`: Schrift Barlow (SIL Open Font License)
- `capacitor.config.json`: App-Name und Paket-ID
- `scripts/patch-android.sh`: ergänzt GPS-Rechte, Farben und das App-Symbol im Android-Projekt
- `.github/workflows/build-apk.yml`: baut die APK
- `.github/workflows/fahrplan.yml` und `tools/fahrplan.py`: erzeugen die Fahrplandateien

Die Paket-ID `de.ottos11.meckerbahn` der Test-APK stammt aus der Zeit, als die App noch Meckerbahn hieß. Sie bleibt, damit sich die Test-APK weiter als Update installieren lässt.

Fotos hängt die App über das Plugin `capacitor-email-composer` an die Mail. Das Android-Projekt (`android/`) wird beim Build jedes Mal neu erzeugt und liegt deshalb nicht im Repo.

## Lizenz

Der Code steht unter der [MIT-Lizenz](LICENSE). Die Schrift Barlow steht unter der SIL Open Font License (`www/fonts/OFL.txt`).

Die Fahrplandaten stammen von DELFI e.V. (Sollfahrplandaten Deutschland) und stehen unter [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). `tools/fahrplan.py` kürzt sie auf Bus, U-, S- und Straßenbahn je Stadt und wandelt sie in ein eigenes Format um. Die App nennt die Quelle unten auf der Startseite und unter „Über“.
