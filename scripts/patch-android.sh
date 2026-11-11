#!/usr/bin/env bash
# Ergänzt das von Capacitor erzeugte Android-Manifest um GPS-Rechte
# und erlaubt der App, Mail-Apps (mailto:) zu öffnen.
set -euo pipefail
MANIFEST="android/app/src/main/AndroidManifest.xml"

if ! grep -q "ACCESS_FINE_LOCATION" "$MANIFEST"; then
  sed -i 's#</manifest>#    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />\n    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />\n    <uses-feature android:name="android.hardware.location.gps" android:required="false" />\n    <queries>\n        <intent>\n            <action android:name="android.intent.action.SENDTO" />\n            <data android:scheme="mailto" />\n        </intent>\n        <intent>\n            <action android:name="android.intent.action.VIEW" />\n            <data android:scheme="mailto" />\n        </intent>\n    </queries>\n</manifest>#' "$MANIFEST"
fi

# Fensterhintergrund in App-Farbe (hell/dunkel), damit die Statusleiste nicht weiß hinterlegt ist
RES="android/app/src/main/res"
mkdir -p "$RES/values" "$RES/values-night"
cat > "$RES/values/mb_colors.xml" <<'XML'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="mb_bg">#F4F4F1</color>
</resources>
XML
cat > "$RES/values-night/mb_colors.xml" <<'XML'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="mb_bg">#141516</color>
</resources>
XML
python3 - "$RES/values/styles.xml" <<'PY'
import re,sys
p=sys.argv[1]; s=open(p).read()
if "mb_bg" not in s:
    s,n=re.subn(r'(<style name="AppTheme\.NoActionBar"[^>]*>)', r'\1\n        <item name="android:windowBackground">@color/mb_bg</item>', s, count=1)
    print("styles.xml angepasst" if n else "WARNUNG: AppTheme.NoActionBar nicht gefunden")
    open(p,"w").write(s)
print(s)
PY

# App-Symbol: gelbe Sprechblase mit dem H der Haltestelle
mkdir -p "$RES/drawable" "$RES/mipmap-anydpi-v26"
cat > "$RES/drawable/mb_icon_fg.xml" <<'XML'
<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp"
    android:viewportWidth="108" android:viewportHeight="108">
    <!-- Sprechblase im Gelb des Haltestellenschilds -->
    <path android:fillColor="#F5B800"
        android:pathData="M34,26h40a8,8 0 0 1 8,8v28a8,8 0 0 1 -8,8H48.5l-10.4,9.1c-1.9,1.6 -4.8,0.2 -4.6,-2.3l0.6,-7.2A8,8 0 0 1 26,62V34a8,8 0 0 1 8,-8z"/>
    <!-- Das H der Haltestelle -->
    <path android:strokeColor="#1C1D1F" android:strokeWidth="7.5" android:strokeLineCap="round"
        android:pathData="M43.5,36.5v23M64.5,36.5v23M43.5,48h21"/>
</vector>
XML
cat > "$RES/values/mb_icon.xml" <<'XML'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="mb_icon_bg">#FFFFFF</color>
</resources>
XML
for n in ic_launcher ic_launcher_round; do
cat > "$RES/mipmap-anydpi-v26/$n.xml" <<'XML'
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/mb_icon_bg" />
    <foreground android:drawable="@drawable/mb_icon_fg" />
</adaptive-icon>
XML
done

echo "Manifest nach dem Patch:"
cat "$MANIFEST"
