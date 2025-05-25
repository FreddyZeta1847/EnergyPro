from flask import Flask, request, render_template, abort
import folium
import json
import os
import requests
import plotly.graph_objs as go
import plotly.offline as pyo



app = Flask(__name__)



def get_cities():
    DATA_PATH = os.path.join(os.path.dirname(__file__), 'cities.json')
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"File non trovato: {DATA_PATH}")
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    cities = data.get('cities', [])
    if not isinstance(cities, list) or not cities:
        raise ValueError("Formato JSON errato: aspettavo chiave 'cities' con una lista di oggetti.")
    else:
        return cities



# Funzione per ottenere i pannelli solari tramite Overpass API
def get_solar_panels(lat, lon, radius=30000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
    node["generator:source"="solar"](around:{radius},{lat},{lon});
    way["generator:source"="solar"](around:{radius},{lat},{lon});
    relation["generator:source"="solar"](around:{radius},{lat},{lon});
    );
    out center;
    """
    try:
        response = requests.get(overpass_url, params={'data': query}, timeout=30)
        response.raise_for_status()
        data = response.json()
        panels = []
        for el in data.get('elements', []):
            if 'lat' in el and 'lon' in el:
                panels.append((el['lat'], el['lon']))
            elif 'center' in el:
                panels.append((el['center']['lat'], el['center']['lon']))
        return panels
    except Exception as e:
        print(f"Errore nel recupero dati OSM: {e}")
        return []
   
def get_hydro(lat, lon, radius=30000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
    node["generator:source"="hydro"](around:{radius},{lat},{lon});
    way["generator:source"="hydro"](around:{radius},{lat},{lon});
    relation["generator:source"="hydro"](around:{radius},{lat},{lon});
    );
    out center;
    """
    try:
        response = requests.get(overpass_url, params={'data': query}, timeout=30)
        response.raise_for_status()
        data = response.json()
        hydro = []
        for el in data.get('elements', []):
            if 'lat' in el and 'lon' in el:
                hydro.append((el['lat'], el['lon']))
            elif 'center' in el:
                hydro.append((el['center']['lat'], el['center']['lon']))
        return hydro
    except Exception as e:
        print(f"Errore nel recupero dati OSM: {e}")
        return []



def create_energy_charts(city1, city2, solar1, hydro1, solar2, hydro2):
    # 1) Grafico Solare
    sol = go.Bar(
        x=[city1, city2],
        y=[solar1, solar2],
        name='Solare',
        marker=dict(
            color='orange',
            pattern=dict(shape='/', fgcolor='rgba(255,255,255,0.3)')
        )
    )
    layout_solar = go.Layout(
        title='Confronto Pannelli Solari',
        barmode='group',
        template='plotly_dark',
        paper_bgcolor='rgba(20,20,20,1)',
        plot_bgcolor='rgba(30,30,30,1)',
        font_color='white'
    )
    fig_solar = go.Figure(data=[sol], layout=layout_solar)
    solar_chart_html = pyo.plot(fig_solar, include_plotlyjs=False, output_type='div')


    # 2) Grafico Idroelettrico
    hydro = go.Bar(
        x=[city1, city2],
        y=[hydro1, hydro2],
        name='Idroelettrica',
        marker=dict(
            color='blue',
            pattern=dict(shape='.', fgcolor='rgba(255,255,255,0.3)')
        )
    )
    layout_hydro = go.Layout(
        title='Confronto Impianti Idroelettrici',
        barmode='group',
        template='plotly_dark',
        paper_bgcolor='rgba(20,20,20,1)',
        plot_bgcolor='rgba(30,30,30,1)',
        font_color='white'
    )
    fig_hydro = go.Figure(data=[hydro], layout=layout_hydro)
    hydro_chart_html = pyo.plot(fig_hydro, include_plotlyjs=False, output_type='div')


    # restituisci i due div HTML distinti
    return solar_chart_html, hydro_chart_html


# Handler
@app.route('/', methods=['GET', 'POST'])
def index():
    cities = get_cities()

    sel1 = cities[0]['nome']
    sel2 = cities[1]['nome'] if len(cities) > 1 else sel1

    if request.method == 'POST':
        c1 = request.form.get('city1')
        c2 = request.form.get('city2')
        if any(c['nome']==c1 for c in cities): sel1 = c1
        if any(c['nome']==c2 for c in cities): sel2 = c2

    try:
        city1 = next(c for c in cities if c['nome']==sel1)
        city2 = next(c for c in cities if c['nome']==sel2)
    except StopIteration:
        abort(400, "Città selezionata non valida")

    # Ottieni pannelli fotovoltaici da OSM
    panels_city1 = get_solar_panels(city1['lat'], city1['lon'], city1['radius'])
    panels_city2 = get_solar_panels(city2['lat'], city2['lon'], city2['radius'])


    hydro_city1 = get_hydro(city1['lat'], city1['lon'], city1['radius'])
    hydro_city2 = get_hydro(city2['lat'], city2['lon'], city2['radius'])


    # Crea mappa centrata sull'Italia
    m = folium.Map(
        location=[41.5, 12.5],
        zoom_start=6,
        min_zoom=4,
        max_bounds=[[35.0, 6.0], [48.5, 18.5]]
    )

    # Cerchi per città
    folium.Circle(
        location=[city1['lat'], city1['lon']],
        radius=city1['radius'],
        color='blue',
        fill=True,
        fill_opacity=0.5,
        popup=sel1
    ).add_to(m)
    folium.Circle(
        location=[city2['lat'], city2['lon']],
        radius=city2['radius'],
        color='red',
        fill=True,
        fill_opacity=0.5,
        popup=sel2
    ).add_to(m)

        # Marker per impianti solari - città 1
    for lat, lon in panels_city1:
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color='blue', icon='sun', prefix='fa'),
            popup=f"Impianto solare - {sel1}: {lat}, {lon}"
        ).add_to(m)

    # Marker per impianti solari - città 2
    for lat, lon in panels_city2:
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color='red', icon='sun', prefix='fa'),
            popup=f"Impianto solare - {sel2}: {lat}, {lon}"
        ).add_to(m)

    # Marker per impianti idroelettrici - città 1
    for lat, lon in hydro_city1:
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color='darkblue', icon='tint', prefix='fa'),
            popup=f"Impianto idroelettrico - {sel1}: {lat}, {lon}"
        ).add_to(m)

    # Marker per impianti idroelettrici - città 2
    for lat, lon in hydro_city2:
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color='darkred', icon='tint', prefix='fa'),
            popup=f"Impianto idroelettrico - {sel2}: {lat}, {lon}"
        ).add_to(m)

    solar_chart_html, hydro_chart_html = create_energy_charts(
        sel1, sel2,
        len(panels_city1), len(hydro_city1),
        len(panels_city2), len(hydro_city2)
    )


    map_html = m._repr_html_()
    return render_template(
    "index.html",
    cities=cities,
    sel1=sel1,
    sel2=sel2,
    map_html=map_html,
    solar_chart_html=solar_chart_html,
    hydro_chart_html = hydro_chart_html
)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/team/santini')
def team_santini():
    return render_template('team/santini.html')


@app.route('/team/chiapparino')
def team_chiapparino():
    return render_template('team/chiapparino.html')


@app.route('/team/montanari')
def team_montanari():
    return render_template('team/montanari.html')


@app.route('/team/panora')
def team_panora():
    return render_template('team/panora.html')

@app.route("/province")
def return_cities():
    cities = get_cities()
    return render_template('province.html', cities=cities)

@app.route('/game')
def game():
    return render_template('game.html')


if __name__ == '__main__':
    app.run(debug=True)























