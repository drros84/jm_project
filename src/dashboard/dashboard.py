
import dash
from dash import html
from dash import dcc
import plotly
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd
import numpy as np
import folium
import os
from PIL import Image
from elasticsearch import Elasticsearch
from dashboard_fcts import *

# Connexion à Elasticsearch
es = Elasticsearch(['http://elasticsearch:9200'])

# Construire la requête pour obtenir la taille totale de l'index
total_docs = es.count(index='adzuna_jobs')["count"]

# Construire une nouvelle requête en spécifiant la taille totale
results = es.search(index='adzuna_jobs', body={"query": {"match_all": {}}})
pil_image = Image.open("2018095159_strategie-de-recherche-d-emploi.png")


# Création de la liste des documents
documents = []
for hit in results['hits']['hits']:
    documents.append(hit['_source'])


# dataframe
df = pd.DataFrame(documents)
locations = [{'label': loc, 'value': loc} for loc in df['location']]
titles = [{'label': loc.lower(), 'value': loc.lower()} for loc in df['title'].unique()]
ids = [{'label': df[df['id']==loc]['title'].iloc[0], 'value': loc} for loc in df['id']]
app = dash.Dash(__name__)

tech_list = ['C++', 'Javascript', 'Java', 'SQL', 'R', 'Python']

tech_stats_df = pd.DataFrame(tech_list, columns = ['tech'])
tech_stats_df['frequency'] = 0
tech_stats_df['avg_min_wage'] = 0
tech_stats_df['avg_max_wage'] = 0

for tech in tech_stats_df['tech']:
    tech_stats = get_tech_stats(es, tech)
    print(tech_stats)
    tech_stats_df.loc[tech_stats_df['tech'] == tech, 'frequency'] = tech_stats['frequency']
    tech_stats_df.loc[tech_stats_df['tech'] == tech, 'avg_min_wage'] = tech_stats['avg_min_wage']
    tech_stats_df.loc[tech_stats_df['tech'] == tech, 'avg_max_wage'] = tech_stats['avg_max_wage']


fig1 = px.bar(tech_stats_df, x = 'frequency', y = 'tech')
fig1.update_layout(yaxis={'categoryorder':'total ascending'})
fig1.update_layout(title_text = "Technologies par fréquence",
    xaxis_title = "Nombre de mentions",
    margin_l = 65)

fig2 = px.scatter(tech_stats_df.sort_values('avg_max_wage'), 
                 x = ['avg_min_wage','avg_max_wage'], 
                 y = 'tech')
fig2.update_traces(marker_size = 12)
fig2.update_layout(title_text = "Fourchette moyenne de salaires par compétence",
    xaxis_title = "Salaire annuel (euros)",
    margin_l = 65)


# Fonction pour générer la mise en page de l'application Dash
def generate_layout():
    return html.Div([
         html.Div([
        
        # le titre avec H4 
        #html.Img(src=pil_image, style={'width': '1500px', 'height': '600px'}),
        html.Img(src=pil_image, style={'width': '1000px', 'height': '50%', 'textAlign': 'center'}),
        
        html.Div([
         dcc.Tabs(id = 'tabs', value = "tab-1", children=[
             # Onglet info générales
             #
             dcc.Tab(label='Infos Générales', children=[
                 html.Div([
                     html.H4("Choisissez le métier"),
                     dcc.Dropdown(
                         id='title',
                         options= titles,
                         value= '',
                         )],style={
                             'margin-bottom' : '70px',
                             'width':'50%',
                             'border': '2px solid #eee',
                             'border-radius': '10px',
                             'padding': '30px 30px 30px 120px',
                             'box-shadow': '2px 2px 3px #ccc',
                             'display': 'block',
                             'margin-left': 'auto',
                             'margin-right': 'auto'
                             }),
                 html.Div([
                     # Onglet info Emploi
                     html.H3("Emploi")
                 ], style={'margin': '30px','background':'rgb(0,139,139)', 'color':'white', 
                           'textAlign':'center','padding':'8px 5px 8px 0px'}),
                 
                 html.Div([
                     # table de données
                     html.Div(id='output')
                     
                 ])
                 ]),
             # Onglet Compétences
             dcc.Tab(label='Compétences', children = [
                 dcc.Graph(figure = fig1, style={'display': 'inline-block'}),
                 dcc.Graph(figure = fig2, style={'display': 'inline-block'})
             ])
             ]),
         ])
     ])
        
       
    ])

# Fonction de rappel pour mettre à jour le tableau de données
@app.callback(
    Output('output', 'children'),
    [Input('title', 'value')], 
)
def update_data_table(titre_choisi):
    
    df_col_name = df[[ 'contract','company','title','location', "salary_max", "salary_min", "latitude","longitude", "created"]]
    df_cond = df_col_name[df_col_name['title'].str.lower() == titre_choisi]
    
    df_to_dict = df_cond.to_dict("records")
    table = dash_table.DataTable(df_cond.to_dict("records"), [{"name": i, "id": i} for i in df_cond.columns])
   
    return table

# Définir la mise en page de l'application Dash
app.layout = generate_layout()

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
