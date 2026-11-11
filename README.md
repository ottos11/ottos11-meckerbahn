# Meckerbahn

Android-App für Beschwerden zu Hamburgs U- und S-Bahn. Die Schwester-App der Meckerlinie (Bus).

Gemeldet werden können:

- **Fahrplan:** Zug zu spät, ausgefallen oder zu früh abgefahren
- **Im Zug oder an der Haltestelle:** Belästigung, Betteln, Gestank, Dreck

So läuft eine Meldung ab:

1. Art des Vorfalls wählen. Bei Belästigung, Betteln, Gestank und Dreck zusätzlich: im Zug oder an der Haltestelle, und was genau.
2. Standort verwenden oder die Haltestelle über ihren Namen suchen. Datum und Uhrzeit lassen sich ändern.
3. Im Zug: Linie, Richtung und Abfahrt aus dem Fahrplan wählen, optional die Wagennummer. An der Haltestelle: U-Bahn oder S-Bahn angeben, optional die genaue Stelle.
4. Bis zu drei Fotos anhängen, Mail prüfen und in der Mail-App öffnen.

Die Mail geht automatisch an den richtigen Betrieb: U-Bahn an die HOCHBAHN (info@hochbahn.de), S-Bahn an die S-Bahn Hamburg (s-bahn.hamburg@deutschebahn.com). Für andere Betriebe wie die AKN trägt man die Adresse einmal ein.

Der Verlauf sammelt alle Vorfälle nach Linie und Haltestelle. Frühere Fälle stehen in der nächsten Mail, ab zwei Vorfällen gibt es eine Sammelbeschwerde.

Fahrplan- und Echtzeitdaten kommen von [Transitous](https://transitous.org/). Name, Verlauf und Einstellungen bleiben auf dem Gerät. Fotos speichert die App nicht, sie verlassen das Handy nur als Anhang der Mail.

## APK herunterladen

Bei jedem Push auf `main` baut GitHub Actions automatisch eine neue APK.

1. Im Repo rechts auf **Releases** gehen.
2. `meckerbahn.apk` auf dem Handy herunterladen und installieren, oder das Repo in Obtainium eintragen.

Jede APK wird mit demselben Schlüssel signiert (`signing/debug.keystore`, Standard-Passwort `android`), damit sich neue Versionen als Update installieren lassen.

## Aufbau

- `www/index.html`: die komplette App (HTML, CSS, JavaScript)
- `www/fonts/`: Schrift Barlow (SIL Open Font License)
- `capacitor.config.json`: App-Name und Paket-ID
- `scripts/patch-android.sh`: ergänzt GPS-Rechte, Farben und das App-Symbol im Android-Projekt
- `.github/workflows/build-apk.yml`: baut die APK

Fotos hängt die App über das Plugin `capacitor-email-composer` an die Mail. Das Android-Projekt (`android/`) wird beim Build jedes Mal neu erzeugt und liegt deshalb nicht im Repo.
