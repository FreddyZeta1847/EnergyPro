# 🌱 EnergyPro

## ⚡ Confronto Energie Rinnovabili per Province

EnergyPro è un progetto scolastico nato all'interno dell'**ITIS P. Hensemberger di Monza**, con l’obiettivo di **analizzare e visualizzare la distribuzione di impianti per energie rinnovabili (solari e idroelettrici)** nelle diverse province italiane.

---

## 🎯 Obiettivi del Progetto

- Evidenziare le **disparità territoriali** nell’adozione delle energie rinnovabili.
- Rendere i dati accessibili tramite **mappe interattive** e **grafici dinamici**.
- Sensibilizzare l'opinione pubblica attraverso una piattaforma web chiara e coinvolgente.

---

## 🧰 Tecnologie Utilizzate

| Tecnologia     | Ruolo                                         |
|----------------|-----------------------------------------------|
| `Python` + `Flask` | Backend e routing dell'applicazione         |
| `Folium`       | Mappa interattiva con cerchi proporzionali    |
| `Plotly`       | Creazione di grafici interattivi              |
| `Overpass API` | Ottenimento dei dati sugli impianti rinnovabili |
| `HTML` + `CSS` | Interfaccia web responsive e accessibile      |

---

## 🌐 Funzionalità Principali

- 🔍 **Confronto diretto tra province**
- 🗺️ **Visualizzazione geografica** su mappa interattiva `Folium`
- 📊 **Grafici dinamici** e aggiornati con `Plotly`
- 🎮 **Minigioco educativo** integrato
- 👥 **Team dedicato** di studenti sviluppatori e data analyst

---

## 🧪 Struttura del Progetto

```bash
EnergyPro/
├── static/
│   └── images/             # Immagini e risorse statiche
├── templates/              # File HTML Jinja2 per le view
│   └── team/               # Pagine html del team di EnergyPro       
├── app.py                  # Server Flask (entry point)
├── .gitignore              # File per escludere cartelle (es: /images)
└── README.md
