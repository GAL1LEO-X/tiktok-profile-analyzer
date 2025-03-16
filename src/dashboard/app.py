import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import logging
from pathlib import Path

from config.config import (
    OUTPUT_DIR,
    DASHBOARD_UPDATE_INTERVAL,
    API_HOST,
    API_PORT
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inizializza l'app Dash
app = dash.Dash(__name__, 
    title='TikTok Profile Analyzer Dashboard',
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

# Layout principale
app.layout = html.Div([
    # Header
    html.Div([
        html.H1('TikTok Profile Analyzer Dashboard'),
        html.P('Analisi in tempo reale dei profili TikTok con AI')
    ], className='header'),

    # Contenitore principale
    html.Div([
        # Sidebar per la selezione del profilo
        html.Div([
            html.H3('Seleziona Profilo'),
            dcc.Dropdown(
                id='profile-selector',
                placeholder='Seleziona un profilo...'
            ),
            html.Button('Aggiorna Dati', id='refresh-button', n_clicks=0),
            html.Div(id='last-update-info')
        ], className='sidebar'),

        # Area principale dei grafici
        html.Div([
            # Metriche principali
            html.Div([
                html.Div([
                    html.H4('Engagement Rate'),
                    html.Div(id='engagement-rate-value')
                ], className='metric-card'),
                html.Div([
                    html.H4('Sentiment Score'),
                    html.Div(id='sentiment-score-value')
                ], className='metric-card'),
                html.Div([
                    html.H4('Risk Level'),
                    html.Div(id='risk-level-value')
                ], className='metric-card')
            ], className='metrics-container'),

            # Grafici
            html.Div([
                # Engagement over time
                html.Div([
                    html.H4('Engagement nel Tempo'),
                    dcc.Graph(id='engagement-timeline')
                ], className='chart-container'),

                # Sentiment distribution
                html.Div([
                    html.H4('Distribuzione del Sentiment'),
                    dcc.Graph(id='sentiment-distribution')
                ], className='chart-container')
            ], className='charts-row'),

            html.Div([
                # Top hashtags
                html.Div([
                    html.H4('Top Hashtag'),
                    dcc.Graph(id='top-hashtags')
                ], className='chart-container'),

                # Interaction network
                html.Div([
                    html.H4('Network di Interazioni'),
                    dcc.Graph(id='interaction-network')
                ], className='chart-container')
            ], className='charts-row')
        ], className='main-content')
    ], className='container'),

    # Footer con informazioni aggiuntive
    html.Div([
        html.Div(id='analysis-summary'),
        dcc.Interval(
            id='interval-component',
            interval=DASHBOARD_UPDATE_INTERVAL * 1000,  # in millisecondi
            n_intervals=0
        )
    ], className='footer')
], className='app-container')

# Callback per aggiornare la lista dei profili
@app.callback(
    Output('profile-selector', 'options'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_profile_list(n_intervals, n_clicks):
    try:
        output_dir = Path(OUTPUT_DIR)
        profile_files = list(output_dir.glob('*_report_*.json'))
        profiles = set(f.stem.split('_')[0] for f in profile_files)
        
        return [{'label': f'@{profile}', 'value': profile} for profile in profiles]
    except Exception as e:
        logger.error(f"Error updating profile list: {str(e)}")
        return []

# Callback per aggiornare le metriche principali
@app.callback(
    [Output('engagement-rate-value', 'children'),
     Output('sentiment-score-value', 'children'),
     Output('risk-level-value', 'children'),
     Output('last-update-info', 'children')],
    Input('profile-selector', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_metrics(selected_profile, n_intervals):
    if not selected_profile:
        return 'N/A', 'N/A', 'N/A', ''

    try:
        # Carica il report più recente
        output_dir = Path(OUTPUT_DIR)
        report_files = list(output_dir.glob(f"{selected_profile}_report_*.json"))
        
        if not report_files:
            return 'N/A', 'N/A', 'N/A', 'Nessun dato disponibile'
        
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_report, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Estrai le metriche
        engagement = report['raw_data']['engagement']['average_engagement']
        sentiment = report['raw_data']['sentiment']['basic_sentiment']
        risk_level = report['raw_data']['reputation_risks']['risk_level']
        
        last_update = datetime.fromtimestamp(latest_report.stat().st_mtime)
        update_info = f'Ultimo aggiornamento: {last_update.strftime("%Y-%m-%d %H:%M:%S")}'
        
        return f'{engagement:.2%}', f'{sentiment:.2f}', risk_level.upper(), update_info
    
    except Exception as e:
        logger.error(f"Error updating metrics: {str(e)}")
        return 'Error', 'Error', 'Error', 'Errore nel caricamento dei dati'

# Callback per il grafico dell'engagement
@app.callback(
    Output('engagement-timeline', 'figure'),
    Input('profile-selector', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_engagement_timeline(selected_profile, n_intervals):
    if not selected_profile:
        return go.Figure()

    try:
        output_dir = Path(OUTPUT_DIR)
        report_files = list(output_dir.glob(f"{selected_profile}_report_*.json"))
        
        if not report_files:
            return go.Figure()
        
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_report, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Prepara i dati per il grafico
        engagement_data = report['raw_data']['engagement']['metrics']
        df = pd.DataFrame(engagement_data)
        
        fig = px.line(df, x='post_url', y='engagement_rate',
                     title='Engagement Rate per Post',
                     labels={'post_url': 'Post', 'engagement_rate': 'Engagement Rate'})
        
        return fig
    
    except Exception as e:
        logger.error(f"Error updating engagement timeline: {str(e)}")
        return go.Figure()

# Callback per la distribuzione del sentiment
@app.callback(
    Output('sentiment-distribution', 'figure'),
    Input('profile-selector', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_sentiment_distribution(selected_profile, n_intervals):
    if not selected_profile:
        return go.Figure()

    try:
        output_dir = Path(OUTPUT_DIR)
        report_files = list(output_dir.glob(f"{selected_profile}_report_*.json"))
        
        if not report_files:
            return go.Figure()
        
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_report, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Estrai i dati del sentiment
        sentiment_scores = [
            comment['sentiment'] for post in report['raw_data']['posts']
            for comment in post.get('comments', [])
        ]
        
        fig = px.histogram(sentiment_scores, 
                          title='Distribuzione del Sentiment nei Commenti',
                          labels={'value': 'Sentiment Score', 'count': 'Numero di Commenti'})
        
        return fig
    
    except Exception as e:
        logger.error(f"Error updating sentiment distribution: {str(e)}")
        return go.Figure()

# Callback per i top hashtag
@app.callback(
    Output('top-hashtags', 'figure'),
    Input('profile-selector', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_top_hashtags(selected_profile, n_intervals):
    if not selected_profile:
        return go.Figure()

    try:
        output_dir = Path(OUTPUT_DIR)
        report_files = list(output_dir.glob(f"{selected_profile}_report_*.json"))
        
        if not report_files:
            return go.Figure()
        
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_report, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Estrai i dati degli hashtag
        hashtags = report['raw_data']['trending_topics']['hashtag_analysis']
        df = pd.DataFrame(list(hashtags.items()), columns=['hashtag', 'count'])
        df = df.sort_values('count', ascending=True)
        
        fig = px.bar(df, x='count', y='hashtag', orientation='h',
                    title='Top Hashtag Utilizzati',
                    labels={'count': 'Numero di Utilizzi', 'hashtag': 'Hashtag'})
        
        return fig
    
    except Exception as e:
        logger.error(f"Error updating top hashtags: {str(e)}")
        return go.Figure()

# Callback per il network di interazioni
@app.callback(
    Output('interaction-network', 'figure'),
    Input('profile-selector', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_interaction_network(selected_profile, n_intervals):
    if not selected_profile:
        return go.Figure()

    try:
        output_dir = Path(OUTPUT_DIR)
        report_files = list(output_dir.glob(f"{selected_profile}_report_*.json"))
        
        if not report_files:
            return go.Figure()
        
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_report, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Estrai i dati delle interazioni
        interactions = report['raw_data']['interactions']['interactions']
        
        # Crea il grafico di rete
        nodes = []
        edges = []
        
        # Aggiungi il nodo centrale (profilo analizzato)
        nodes.append(dict(id=selected_profile, label=selected_profile, size=20))
        
        # Aggiungi i nodi e gli archi per le interazioni
        for user, data in interactions.items():
            nodes.append(dict(id=user, label=user, size=10))
            edges.append(dict(source=selected_profile, target=user, 
                            weight=data['comment_count']))
        
        # Crea il layout del grafico
        fig = go.Figure(data=[
            go.Scatter(x=[node['x'] for node in nodes],
                      y=[node['y'] for node in nodes],
                      mode='markers+text',
                      text=[node['label'] for node in nodes],
                      marker=dict(size=[node['size'] for node in nodes]))
        ])
        
        fig.update_layout(title='Network di Interazioni',
                         showlegend=False,
                         hovermode='closest')
        
        return fig
    
    except Exception as e:
        logger.error(f"Error updating interaction network: {str(e)}")
        return go.Figure()

# Callback per il sommario dell'analisi
@app.callback(
    Output('analysis-summary', 'children'),
    Input('profile-selector', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_analysis_summary(selected_profile, n_intervals):
    if not selected_profile:
        return 'Seleziona un profilo per vedere il sommario dell\'analisi'

    try:
        output_dir = Path(OUTPUT_DIR)
        report_files = list(output_dir.glob(f"{selected_profile}_report_*.json"))
        
        if not report_files:
            return 'Nessun dato disponibile per questo profilo'
        
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_report, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        return html.Div([
            html.H3('Sommario dell\'Analisi'),
            html.P(report['executive_summary'])
        ])
    
    except Exception as e:
        logger.error(f"Error updating analysis summary: {str(e)}")
        return 'Errore nel caricamento del sommario'

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050) 