# Meckerlinie

Android-App für Beschwerden zu Bus und Bahn: Die App schreibt eine fertige Beschwerde und schickt sie an den zuständigen Verkehrsbetrieb.

Gemeldet werden können:

- **Die Fahrt:** zu spät gekommen, ausgefallen, zu früh abgefahren, gefährliche Fahrweise
- **Im Fahrzeug oder an der Haltestelle:** Belästigung, Betteln, Gestank, Dreck

So läuft eine Meldung ab:

1. Art des Vorfalls wählen. Bei Belästigung, Betteln, Gestank und Dreck zusätzlich: im Fahrzeug oder an der Haltestelle, und was genau.
2. Standort verwenden oder die Haltestelle über ihren Namen suchen. Datum und Uhrzeit lassen sich ändern.
3. Linie, Richtung und Abfahrt aus dem Fahrplan wählen. Die Haltestelle zeigt alle Linien, nach Bus, U-Bahn, S-Bahn und Tram sortiert. Bei Meldungen an der Haltestelle reicht die Angabe, was dort hält.
4. Bis zu drei Fotos anhängen, Beschwerde prüfen und per Mail-App oder Kontaktformular abschicken.

Zum Ausprobieren gibt es unter Einstellungen einen Testmodus: Dann gehen alle Beschwerden mit „[Test]“ im Betreff an die eigene Adresse statt an den Verkehrsbetrieb.

Der Verlauf sammelt alle Vorfälle nach Linie und Haltestelle. Frühere Fälle stehen in der nächsten Beschwerde, ab zwei Vorfällen gibt es eine Sammelbeschwerde.

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

Neue Stadt: Eintrag in `www/cities.js` ergänzen. Welche Namen der Fahrplandienst für die Betriebe einer Stadt verwendet, zeigt der Workflow „Betreiber auflisten“ (unter Actions von Hand starten, Orte als `Name|Breite,Länge`).

## Gestaltung

Verkehrsbetriebe haben je Stadt eigene Farben, deshalb ist die App neutral: Schwarz auf hellem Grau und das Gelb des Haltestellenschilds, das bundesweit gleich ist. Linienschilder tragen die üblichen Zeichenfarben: Blau für U-Bahn, Grün für S-Bahn, sonst Schwarz.

## APK herunterladen

Bei jedem Push auf `main` baut GitHub Actions automatisch eine neue APK.

1. Im Repo rechts auf **Releases** gehen.
2. `meckerlinie.apk` auf dem Handy herunterladen und installieren, oder das Repo in Obtainium eintragen.

Jede APK wird mit demselben Schlüssel signiert (`signing/debug.keystore`, Standard-Passwort `android`), damit sich neue Versionen als Update installieren lassen.

## Aufbau

- `www/index.html`: die komplette App (HTML, CSS, JavaScript)
- `www/cities.js`: Städte, Betriebe und Beschwerdeadressen
- `www/fonts/`: Schrift Barlow (SIL Open Font License)
- `capacitor.config.json`: App-Name und Paket-ID
- `scripts/patch-android.sh`: ergänzt GPS-Rechte, Farben und das App-Symbol im Android-Projekt
- `.github/workflows/build-apk.yml`: baut die APK
- `.github/workflows/betreiber.yml`: listet die Betriebe einer Stadt aus dem Fahrplandienst
- `.github/workflows/haltestelle.yml`: zeigt, zu welcher Haltestelle die Abfahrten an einem Ort gehören

Die Paket-ID `de.ottos11.meckerbahn` stammt aus der Zeit, als Bus und Bahn noch zwei Apps waren. Sie bleibt, damit sich die App als Update über die bisherige Meckerbahn installieren lässt.

Fotos hängt die App über das Plugin `capacitor-email-composer` an die Mail. Das Android-Projekt (`android/`) wird beim Build jedes Mal neu erzeugt und liegt deshalb nicht im Repo.

## Lizenz

Der Code steht unter der [MIT-Lizenz](LICENSE). Die Schrift Barlow steht unter der SIL Open Font License (`www/fonts/OFL.txt`).

Die Fahrplandaten kommen von Transitous. Transitous erlaubt die Nutzung nur für nicht kommerzielle Open-Source-Projekte und verlangt einen sichtbaren Hinweis auf [seine Datenquellen](https://transitous.org/sources/) sowie die Namensnennung von OpenStreetMap. Beides steht in der App. Wer die App kommerziell nutzen will, etwa mit Werbung, braucht eine andere Quelle für die Fahrplandaten.
