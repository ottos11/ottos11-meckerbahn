// Städte für Meckerlinie (Bus) und Meckerbahn (U-, S-, Stadt- und Straßenbahn).
//
// Diese Datei ist in beiden Apps gleich. Neue Stadt: Eintrag ergänzen.
//
// Je Stadt:
//   center, r     Mittelpunkt [Breite, Länge] und Radius in km für die Erkennung am Standort
//   ops           Betriebe. Entweder mail (Beschwerden per Mail) oder forms (nur Kontaktformular).
//                 forms.default gilt immer, forms.<vorfallart> nur für diese Art.
//                 re erkennt den Betrieb am Namen aus den Fahrplandaten.
//                 authority: Verbund, nur als Standard-Empfänger wählbar.
//   byMode        welcher Betrieb ist zuständig, wenn der Fahrplan keinen Namen liefert
//                 (BUS, SUBWAY = U-Bahn, SUBURBAN = S-Bahn, TRAM = Straßen- und Stadtbahn)
//   fallback      Betrieb für unbekannte Unternehmen (sonst fragt die App nach der Adresse)
//   def           Standard-Empfänger je App
//   groups        Auswahl "Welche Bahn?" für Meldungen an der Haltestelle (nur Meckerbahn)
//   ex            Beispiele für die Eingabefelder
//
// Die Namen in "re" sind so geschrieben, wie der Fahrplandienst Transitous die Betriebe führt
// (geprüft mit dem Workflow "Betreiber auflisten").
//
// Quellen der Adressen: jeweils die offiziellen Kontakt- oder Datenschutzseiten der Betriebe,
// Stand November 2026. Bitte vor Änderungen dort nachsehen.

window.CITIES = [
  {
    id: "hamburg", name: "Hamburg", center: [53.55, 10.0], r: 35,
    ops: {
      hochbahn: { name: "HOCHBAHN", mail: "info@hochbahn.de", re: /hochbahn/i },
      vhh: { name: "VHH", mail: "kundendialog@vhh-mobility.de", re: /vhh|verkehrsbetriebe hamburg-holstein/i },
      sbahn: { name: "S-Bahn Hamburg", mail: "s-bahn.hamburg@deutschebahn.com", re: /s-bahn hamburg/i },
      hvv: { name: "hvv", mail: "info@hvv.de", authority: true }
    },
    byMode: { BUS: "hochbahn", SUBWAY: "hochbahn", SUBURBAN: "sbahn" },
    def: { bus: "hochbahn", bahn: "hochbahn" },
    groups: [
      { key: "U", label: "U-Bahn", badge: "U", modes: ["SUBWAY"] },
      { key: "S", label: "S-Bahn", badge: "S", modes: ["SUBURBAN"] }
    ],
    ex: { stop: "Jungfernstieg", bus: "5 oder X35", bahn: "U1 oder S3", dir: "Ohlstedt" }
  },
  {
    id: "berlin", name: "Berlin", center: [52.52, 13.405], r: 35,
    ops: {
      bvg: { name: "BVG", mail: "info@bvg.de", re: /bvg|berliner verkehrsbetriebe/i },
      sbahn: {
        name: "S-Bahn Berlin", re: /s-bahn berlin/i,
        forms: {
          default: "https://sbahn.berlin/en/contact/contact-form-inquiries-about-the-company/",
          frueh: "https://sbahn.berlin/en/contact/contact-form-train-dispatches/",
          belaestigt: "https://sbahn.berlin/en/contact/contact-form-compliance-with-conditions-of-transportation/",
          betteln: "https://sbahn.berlin/en/contact/contact-form-compliance-with-conditions-of-transportation/",
          gestank: "https://sbahn.berlin/en/contact/contact-form-information-on-defects/",
          dreck: "https://sbahn.berlin/en/contact/contact-form-information-on-defects/"
        }
      }
    },
    byMode: { BUS: "bvg", SUBWAY: "bvg", TRAM: "bvg", SUBURBAN: "sbahn" },
    def: { bus: "bvg", bahn: "bvg" },
    groups: [
      { key: "U", label: "U-Bahn", badge: "U", modes: ["SUBWAY"] },
      { key: "T", label: "Tram", badge: "Tram", modes: ["TRAM"] },
      { key: "S", label: "S-Bahn", badge: "S", modes: ["SUBURBAN"] }
    ],
    ex: { stop: "Alexanderplatz", bus: "M41 oder 100", bahn: "U2 oder S5", dir: "Pankow" }
  },
  {
    id: "muenchen", name: "München", center: [48.137, 11.575], r: 30,
    ops: {
      mvg: { name: "MVG", re: /mvg|m(ü|ue)nchner verkehrsgesellschaft|^(sev )?(bus|u-bahn|stra(ß|ss)enbahn) m(ü|ue)nchen/i, forms: { default: "https://www.mvg.de/services/kontakt/kundendialog.html" } },
      sbahn: { name: "S-Bahn München", re: /s-bahn m(ü|ue)nchen/i, forms: { default: "https://www.s-bahn-muenchen.de/service/kontakt/kontaktformular" } },
      mvv: { name: "MVV", authority: true, forms: { default: "https://www.mvv-muenchen.de/kontakt" } }
    },
    byMode: { BUS: "mvg", SUBWAY: "mvg", TRAM: "mvg", SUBURBAN: "sbahn" },
    fallback: "mvv",
    def: { bus: "mvg", bahn: "mvg" },
    groups: [
      { key: "U", label: "U-Bahn", badge: "U", modes: ["SUBWAY"] },
      { key: "T", label: "Tram", badge: "Tram", modes: ["TRAM"] },
      { key: "S", label: "S-Bahn", badge: "S", modes: ["SUBURBAN"] }
    ],
    ex: { stop: "Marienplatz", bus: "58 oder 100", bahn: "U3 oder S1", dir: "Fürstenried West" }
  },
  {
    id: "koeln", name: "Köln", center: [50.938, 6.96], r: 22,
    ops: {
      kvb: { name: "KVB", re: /kvb|k(ö|oe)lner (vb|verkehrs)/i, forms: { default: "https://www.kvb.koeln/unternehmen/kontakt/verbesserungsmanagement.html" } },
      db: { name: "DB Regio NRW", re: /db regio|s-bahn k(ö|oe)ln|deutsche bahn/i, forms: { default: "https://www.bahn.de/hilfe#/feedbackanfragen/nahverkehr" } }
    },
    byMode: { BUS: "kvb", SUBWAY: "kvb", TRAM: "kvb", SUBURBAN: "db" },
    def: { bus: "kvb", bahn: "kvb" },
    groups: [
      { key: "B", label: "Stadtbahn", badge: "Bahn", modes: ["SUBWAY", "TRAM"] },
      { key: "S", label: "S-Bahn", badge: "S", modes: ["SUBURBAN"] }
    ],
    ex: { stop: "Neumarkt", bus: "136 oder 142", bahn: "18 oder S12", dir: "Thielenbruch" }
  },
  {
    id: "frankfurt", name: "Frankfurt", center: [50.11, 8.682], r: 22,
    // Die VGF verweist für Beschwerden zum Nahverkehr in Frankfurt auf das Serviceportal des RMV.
    ops: {
      rmv: { name: "RMV", forms: { default: "https://www.rmv.de/elma/static/start.html" } }
    },
    byMode: { BUS: "rmv", SUBWAY: "rmv", TRAM: "rmv", SUBURBAN: "rmv" },
    fallback: "rmv",
    def: { bus: "rmv", bahn: "rmv" },
    groups: [
      { key: "U", label: "U-Bahn", badge: "U", modes: ["SUBWAY"] },
      { key: "T", label: "Tram", badge: "Tram", modes: ["TRAM"] },
      { key: "S", label: "S-Bahn", badge: "S", modes: ["SUBURBAN"] }
    ],
    ex: { stop: "Hauptwache", bus: "36 oder 30", bahn: "U4 oder S8", dir: "Enkheim" }
  },
  {
    id: "augsburg", name: "Augsburg", center: [48.366, 10.894], r: 14,
    // swa-Linien heißen im Fahrplan schlicht "OMNIBUS" und "STRASSENBAHN".
    // Regionalbusse anderer Unternehmen: Die App fragt einmal nach deren Adresse.
    ops: {
      swa: { name: "swa", mail: "kundenservice-verkehr@sw-augsburg.de", re: /^(omnibus|stra(ss|ß)enbahn)$|swa\b|stadtwerke augsburg/i }
    },
    byMode: { BUS: "swa", TRAM: "swa" },
    def: { bus: "swa", bahn: "swa" },
    groups: [
      { key: "T", label: "Straßenbahn", badge: "Tram", modes: ["TRAM"] }
    ],
    ex: { stop: "Königsplatz", bus: "22 oder 32", bahn: "3 oder 6", dir: "Haunstetten West" }
  }
];
