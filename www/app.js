// Welche App gebaut wird: "bus" = Meckerlinie, "bahn" = Meckerbahn.
// index.html und cities.js sind in beiden Apps gleich, nur diese Datei unterscheidet sich.
window.APP={kind:"bahn"};
document.documentElement.setAttribute("data-kind",window.APP.kind);
