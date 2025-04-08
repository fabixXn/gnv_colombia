import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import pandas as pd
import geopandas as gpd
import plotly.express as px

# ===============================
# Cargar y preparar los datos
# ===============================
df = pd.read_csv("consulta_gas.csv")
df['DEPARTAMENTO'] = df['DEPARTAMENTO'].str.lower().str.strip()
df['DEPARTAMENTO'] = df['DEPARTAMENTO'].replace({'bogota d.c.': 'bogotá, d.c.'})

# Cargar shapefile
mapa_col = gpd.read_file("MGN2022_DPTO_POLITICO/MGN_DPTO_POLITICO.shp")
mapa_col['DPTO_CNMBR'] = mapa_col['DPTO_CNMBR'].str.lower().str.strip()
mapa_col['DPTO_CNMBR'] = mapa_col['DPTO_CNMBR'].replace({
    'atlantico': 'atlántico',
    'cordoba': 'córdoba',
    'bolivar': 'bolívar',
    'boyaca': 'boyacá',
    'caqueta': 'caquetá',
    'quindio': 'quindío',
    'guajira': 'la guajira',
    'magdalena': 'magdalena',
    'nariño': 'nariño',
    'putumayo': 'putumayo',
    'santander': 'santander',
    'sucre': 'sucre',
    'tolima': 'tolima',
    'valle': 'valle del cauca',
    'meta': 'meta',
    'cundinamarca': 'cundinamarca',
    'antioquia': 'antioquia',
    'risaralda': 'risaralda',
    'bogota, d.c.': 'bogotá, d.c.'
})

# Procesar cantidades por departamento
agentes_por_departamento = df.groupby('DEPARTAMENTO').size().reset_index(name='cantidad')
datos_unidos = mapa_col.merge(
    agentes_por_departamento,
    left_on='DPTO_CNMBR',
    right_on='DEPARTAMENTO',
    how='left'
).fillna({'cantidad': 0})

# Convertir a GeoJSON
geojson_col = datos_unidos.__geo_interface__

# ===============================
# Crear la aplicación Dash
# ===============================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Agentes GNV Colombia", className="text-center my-4"))
    ]),

    dbc.Tabs([
        # Pestaña Acerca de
        dbc.Tab([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Visualización interactiva de agentes GNV en Colombia", className="card-title"),
                    html.P("Exploración de la distribución geográfica y estadística de los proveedores de Gas Natural Vehicular en el país por departamentos."),
                    html.P("En la visualización de barras, una de las variables clave es el (Tipo) de agente. Esta categoría agrupa los agentes de GNV según su rol o actividad principal."),
                    html.P("El histograma permite observar cuántos agentes hay por cada tipo y por departamento, identificando así la composición del suministro de GNV a lo largo del país.")
                ])
            ], className="mt-4")
        ], label="Acerca de"),

        # Pestaña Mapa
        dbc.Tab([
            dcc.Graph(
                id='mapa-colombia',
                figure=px.choropleth(
                    datos_unidos,
                    geojson=datos_unidos.geometry.__geo_interface__,
                    locations=datos_unidos.index,
                    color="cantidad",
                    color_continuous_scale="YlOrRd",
                    labels={"cantidad": "Agentes"},
                    hover_name="DPTO_CNMBR"
                ).update_geos(
                    fitbounds="locations",
                    visible=False
                ).update_layout(
                    title="Cantidad de Agentes GNV por Departamento",
                    margin={"r":0,"t":50,"l":0,"b":0}
                )
            )
        ], label="Mapa Departamentos"),

        # Pestaña Gráfico de Barras
        dbc.Tab([
            dcc.Graph(
                id='grafico-barras',
                figure=px.bar(
                    df.groupby('DEPARTAMENTO').size().reset_index(name='Conteo').sort_values('Conteo', ascending=False),
                    x='Conteo',
                    y='DEPARTAMENTO',
                    orientation='h',
                    title='Cantidad de Agentes por Departamento',
                    color='Conteo',
                    color_continuous_scale='Teal'
                ).update_layout(
                    xaxis_title='Número de Agentes',
                    yaxis_title='',
                    coloraxis_showscale=False
                )
            )
        ], label="Gráfico de Barras"),

        # Pestaña Distribución Geográfica
        dbc.Tab([
            dcc.Graph(
                id='grafico-distribucion',
                figure=px.scatter(
                    df,
                    x='LONGITUD',
                    y='LATITUD',
                    color='TIPO_AGENTE',
                    title='Distribución Geográfica de Agentes',
                    hover_data=['NOMBRE_COMERCIAL', 'DEPARTAMENTO']
                ).update_traces(
                    marker=dict(size=8, opacity=0.7)
                ).update_layout(
                    xaxis_title='Longitud',
                    yaxis_title='Latitud'
                )
            )
        ], label="Distribución Geográfica"),

        # Pestaña Tabla de Datos
        dbc.Tab([
            dash_table.DataTable(
                id='tabla-datos',
                columns=[{'name': col, 'id': col} for col in df.columns],
                data=df.to_dict('records'),
                page_size=10,
                style_table={'overflowX': 'auto'},
                filter_action="native",
                sort_action="native",
                export_format="csv"
            )
        ], label="Tabla de Datos")
    ])
], fluid=True)

if __name__ == "__main__":
    app.run(debug=True)
