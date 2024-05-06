
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

latest_technos = get_latest_technos()

# Construire la requête pour obtenir la taille totale de l'index
total_docs = es.count(index='adzuna_jobs')["count"]

# Construire une nouvelle requête en spécifiant la taille totale
results = es.search(index='adzuna_jobs', body={"query": {"match_all": {}}}, size = total_docs)

pil_image = Image.open("2018095159_strategie-de-recherche-d-emploi.png")


# Création de la liste des documents
documents = []
for hit in results['hits']['hits']:

    # Convert skills list to string
    hit['_source']['skills'] = ', '.join(list(set(hit['_source']['skills'])))

    # Clean title
    title_stop_words = ['(it)', 'h/f', 'f/h', '(h/f)', '(f/h)']
    clean_title = hit['_source']['title'].lower().split(' ')
    clean_title = [word for word in clean_title if word not in title_stop_words]
    hit['_source']['clean_title'] = ' '.join(clean_title).capitalize()
    documents.append(hit['_source'])


# dataframe
df = pd.DataFrame(documents)
locations = [{'label': loc, 'value': loc} for loc in df['location']]
titles = [{'label': loc, 'value': loc} for loc in df['clean_title'].unique()]
ids = [{'label': df[df['id']==loc]['title'].iloc[0], 'value': loc} for loc in df['id']]
app = dash.Dash(__name__)

# tech_list = ['C++', 'Javascript', 'Java', 'SQL', 'R', 'Python']

tech_stats_df = pd.DataFrame(latest_technos, columns = ['tech'])
tech_stats_df['frequency'] = 0
tech_stats_df['avg_min_wage'] = 0
tech_stats_df['avg_max_wage'] = 0

for tech in tech_stats_df['tech']:
    tech_stats = get_tech_stats(es, tech)
    tech_stats_df.loc[tech_stats_df['tech'] == tech, 'frequency'] = tech_stats['frequency']
    tech_stats_df.loc[tech_stats_df['tech'] == tech, 'avg_min_wage'] = tech_stats['avg_min_wage']
    tech_stats_df.loc[tech_stats_df['tech'] == tech, 'avg_max_wage'] = tech_stats['avg_max_wage']

top_10_techs = tech_stats_df.sort_values('frequency', ascending = False).head(10)

# fig1 = px.bar(top_10_techs, x = 'frequency', y = 'tech')
# fig1.update_layout(yaxis={'categoryorder':'total ascending'})
# fig1.update_layout(title_text = "Technologies par fréquence",
#     xaxis_title = "Nombre de mentions (top 10)",
#     margin_l = 65)

# fig2 = px.scatter(top_10_techs.sort_values('avg_max_wage'), 
#                  x = ['avg_min_wage','avg_max_wage'], 
#                  y = 'tech')
# fig2.update_traces(marker_size = 12)
# fig2.update_layout(title_text = "Fourchette moyenne de salaires par technologie",
#     xaxis_title = "Salaire mensuel (top 10)",
#     margin_l = 65)


# Function to generate Dash application layout
def generate_layout():
    return html.Div([
         html.Div([
        # le titre avec H4 
        html.Img(src=pil_image, style={'width': '1850px', 'height': '600px'}),
        html.Div([
        html.H4("Choisissez le métier"),
        dcc.Dropdown(
            id='title',
            options= titles,
            value= 'Ingénieur DevOps Data H/F',
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
                 })
              ]),
        
        html.Div([
         dcc.Tabs(id = 'tabs', value = "tab-1", children=[
             # General info tab
            dcc.Tab(label='infos Générales', children=[
                    html.Div([
                     html.H3("Emploi")
                        ], style={'margin': '30px',
                                  'background':'rgb(0,139,139)',
                                'color':'white',
                                  'textAlign':'center',
                                  'padding':'8px 5px 8px 0px'}),
                 
                 
                     # data table
                    dash_table.DataTable(id='tbl_out', 
                                          editable=True,
                                        #   filter_action="native",
                                        sort_action="native",
                                        sort_mode='multi',
                                          row_selectable='multi',
                                          selected_rows=[],
                                          page_action='native',
                                        page_current= 0,
                                        page_size= 10,
                                        #   style_table={'overflowX': 'auto'},
                                           
                                            
                                            ),
                    #  html.Div(id='output'),
                     html.Div(
                       id='datatable-row-ids-container'
                         )
                #  html.Div(id = "map", style={
                #      'display':'inline-block','verticalAlign':'top','width':'50%', 
                #                             'padding':'15px 0px 15px 10px'
                #  })
             ]),
             # Jobs tab
            dcc.Tab(label='Compétences', children = [
        html.Div([
        html.H3("Choisissez une compétence"),
        dcc.Dropdown(
            id='select_tech',
            options= latest_technos,
            value= ['Python', 'SQL', 'Java', 'C#'],
            multi = True
             )]),
        html.Div([
            dcc.Graph(id = 'frequency_barchart', style={'display': 'inline-block'}),
            dcc.Graph(id = 'dumbbell_chart', style={'display': 'inline-block'})
        ])
             ])
             # Salary tab
            # dcc.Tab(label='Salaire')
         ])
     ])
        
       
    ])



# Fonction de rappel pour mettre à jour le tableau de données
# @app.callback(
#     Output('output', 'children'),
#     State('title', 'value') 
# )
# def update_data_table(title):
    
#     df_col_name = df[['contract','company','title','location', "salary_max", "salary_min", "latitude","longitude", "created"]]
#     df_cond = df_col_name[df_col_name['title'] == title]
    
#     df_to_dict = df_cond.to_dict("records")
#     table = dash_table.DataTable(df_cond.to_dict("records"), [{"name": i, "id": i} for i in df_cond.columns])
   
#     return table

# Callback function to update fig1
@app.callback(
    Output('frequency_barchart', 'figure'),
    Input('select_tech', 'value'),
    )
def update_frequency_barchart(select_tech):

    filtered_techs_fig1 = tech_stats_df[tech_stats_df['tech'].isin(select_tech)]
    
    fig1 = px.bar(filtered_techs_fig1, x = 'frequency', y = 'tech')
    fig1.update_layout(yaxis={'categoryorder':'total ascending'})
    fig1.update_layout(title_text = "Technologies par fréquence",
        xaxis_title = "Nombre de mentions",
        margin_l = 65)
    
    return fig1

# Callback function to update fig2
@app.callback(
    Output('dumbbell_chart', 'figure'),
    Input('select_tech', 'value'),
    )
def update_dumbbell_chart(select_tech):

    filtered_techs_fig2 = tech_stats_df[tech_stats_df['tech'].isin(select_tech)]
    
    fig2 = px.scatter(filtered_techs_fig2.sort_values('avg_max_wage'), 
                    x = ['avg_min_wage','avg_max_wage'], 
                    y = 'tech')
    fig2.update_traces(marker_size = 12)
    fig2.update_layout(title_text = "Fourchette moyenne de salaires par technologie",
        xaxis_title = "Salaire mensuel (top 10)",
        margin_l = 65)
    
    return fig2


# Callback function to update figure 1
@app.callback(
    Output('tbl_out', 'data'),
    [Input('title', 'value')],
    )
def update_data_table(titre_choisi):
    
    df_col_name = df[['contract','company','title','clean_title', 'location', "salary_max", "salary_min", "latitude","longitude", "created", "skills"]]
    df_cond = df_col_name[df_col_name['clean_title'] == titre_choisi]
    # to_df = pd.DataFrame(df_cond)
    data =df_cond.to_dict("records")
    
    return data



# Définir la mise en page de l'application Dash
app.layout = generate_layout()

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
