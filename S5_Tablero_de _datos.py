import dash
from dash import html, dcc, Input, Output, callback_context
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px
import tensorflow as tf

data = pd.read_csv("datos_con_puntajes.csv")
model = joblib.load('modelo.joblib')

estu_fam_bajo = data[
    (data["fami_estratovivienda"].isin([1, 2, 3])) & 
    (data["fami_tienecomputador"] == 0) & 
    (data["fami_tieneinternet"] == 0)
]
estu_fam_medio = data[
    (data["fami_estratovivienda"] == 4) & 
    (data["fami_tienecomputador"] == 1) & 
    (data["fami_tieneinternet"] == 1)
]
estu_fam_alto = data[
    (data["fami_estratovivienda"].isin([5,6])) & 
    (data["fami_tienecomputador"] == 1) & 
    (data["fami_tieneinternet"] == 1)
]



#Crear la Dash app
app = dash.Dash(__name__)

#Nombres de las variables x
x_vars = [
'cole_bilingue','cole_caracter','cole_cod_mcpio_ubicacion','cole_genero','cole_jornada','cole_naturaleza',
'cole_sede_principal','estu_genero','estu_fechanacimiento','estu_cod_reside_mcpio','desemp_ingles','fami_cuartoshogar',
'fami_educacionmadre','fami_educacionpadre','fami_estratovivienda','fami_personashogar','fami_tieneautomovil','fami_tienecomputador',
'fami_tieneinternet','fami_tienelavadora']

variables_interes= [
'cole_bilingue','cole_caracter','cole_genero','cole_jornada','cole_naturaleza',
'cole_sede_principal','estu_genero','desemp_ingles','fami_cuartoshogar',
'fami_educacionmadre','fami_educacionpadre','fami_estratovivienda','fami_personashogar','fami_tieneautomovil','fami_tienecomputador',
'fami_tieneinternet','fami_tienelavadora']

puntajes= ['punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica', 'punt_global']
# Logo de la Universidad de Los Andes :)
logo_url = "https://images.ctfassets.net/wp1lcwdav1p1/32ZvbT2qtVDItdoxBhRHRf/ee5581294ae18385bf17cbccdcd74a79/LOGOS_Ingenieri__a_Uniandes_2018-_Color.png?q=60"

def create_histogram():
    fig = go.Figure()

    # Agregar los histogramas para cada grupo
    fig.add_trace(go.Histogram(x=estu_fam_bajo['punt_global'], name='Bajo', marker_color='blue', opacity=0.5))
    fig.add_trace(go.Histogram(x=estu_fam_medio['punt_global'], name='Medio', marker_color='green', opacity=0.5))
    fig.add_trace(go.Histogram(x=estu_fam_alto['punt_global'], name='Alto', marker_color='red', opacity=0.5))

    # Configurar el layout de la gráfica
    fig.update_layout(title='Distribución de Puntaje Global del ICFES por nivel socioeconómico',
                      xaxis_title='Puntaje Global del ICFES',
                      yaxis_title='Densidad',
                      barmode='overlay')

    return fig

# definir el app layout con CSS styling (style = {})
app.layout = html.Div([
    html.Img(src=logo_url, style={'width': '300px', 'margin': 'auto'}),
    html.H1("Factores que afectan el desempeño de los estudiantes en la prueba saber 11", style={'textAlign': 'center', "fontFamily": "Courier New"}),
    html.Label("Ingrese la información:", style={'textAlign': 'center', 'fontWeight': 'bold', "fontFamily": "Courier New"}),
    html.Div(
        [dcc.Input(id=f"x-{var}", type='number', placeholder=var, style={'margin': '5px'}) for var in x_vars],
        id='x-values-input', style={'width': '50%', 'margin': 'auto'}
    ),
    html.Button('Calcular', id='submit-val', n_clicks=0, style={'margin': '20px auto', 'display': 'block'}),
    html.Div(id='output-container-button', style={'textAlign': 'center', 'fontSize': '20px'}),
#BOX Plot
            html.Div([
            html.H1("BoxPlot", style={'textAlign': 'center'}),
            html.Div([
            html.Label("Seleccione la variable para mostrar el boxplot:"),
            dcc.Dropdown(
                id='variable-dropdown',
                options=[{'label': var, 'value': var} for var in variables_interes],
                multi=False),]),
            html.Div([
            html.Label("Seleccione el puntaje que desea conocer:"),
            dcc.Dropdown(
                id='variable-dropdown2',
                options=[{'label': var, 'value': var} for var in puntajes],
                multi=False),]),
            dcc.Graph(id='boxplot')
        ],),

        html.Div([
        html.H1("Histograma", style={'textAlign': 'center'}),
        dcc.Graph(id='histogram')
    ]),

            # Foto background watermark
    html.Div([
        html.Div(style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '100%',
                        'background-image': 'url("http://www.sednarino.gov.co/SEDNARINO12/images/Pruebas%20Saber%20Img.jpg")',
                        'opacity': '0.4', 'z-index': '-1'}),
        html.Div(style={'position': 'relative', 'z-index': '0'})   
    ])
])

@app.callback(
    Output('output-container-button', 'children'),
    Input('submit-val', 'n_clicks'),
    [Input("x-{}".format(var), "value") for var in x_vars], prevent_initial_call=True)
def update_output(n_clicks, *x_values_inputs):
    if n_clicks > 0:        
        y_pred = model.predict([x_values_inputs])

        return f"Puntaje global: {y_pred[0]}"


@app.callback(
    Output('boxplot', 'figure'),
    [Input('variable-dropdown', 'value'),
     Input('variable-dropdown2', 'value')]
)
def update_boxplot(selected_var1, selected_var2):
    if not selected_var1 or not selected_var2:
        return {}

    # Filtrar el DataFrame por cada valor único de la variable binaria
    lista = []
    for bin_value in data[selected_var1].unique():
        df_filtered = data[data[selected_var1] == bin_value]
        trace = go.Box(y=df_filtered[selected_var2], name=f'{selected_var1}: {bin_value}')
        lista.append(trace)
    
    # Configurar el layout del gráfico
    layout = go.Layout(title=f'Box Plots para {selected_var2}', yaxis_title=selected_var2)
    
    # Crear la figura
    fig = go.Figure(data=lista, layout=layout)  # Aquí se debe utilizar data en lugar de lista
    
    return fig


@app.callback(
    Output('histogram', 'figure'),
    [Input('submit-val', 'n_clicks')]
)
def update_histogram(n_clicks):
    # Check if the callback is triggered for the first time (app load)
    if not callback_context.triggered:
        return create_histogram()
    else:
        # Your existing code for updating histogram based on button click
        return create_histogram()

   

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)