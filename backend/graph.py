import os
import pandas as pd
import networkx as nx
from collections import deque
import dash
from dash import dcc, html
import plotly.graph_objects as go

# BFS
def bfs_shortest_path(graph, source, target):
    if source not in graph or target not in graph:
        return []
    queue = deque([source])
    parents = {source: None}
    while queue:
        current = queue.popleft()
        if current == target:
            path = []
            while current is not None:
                path.append(current)
                current = parents[current]
            return list(reversed(path))
        for neighbor in graph[current]:
            if neighbor not in parents:
                parents[neighbor] = current
                queue.append(neighbor)
    return []

# plotar grafo geográfico
def plot_geo_graph(G, path=[]):
    # arestas
    edge_traces = []
    for u, v in G.edges():
        x = [G.nodes[u]['lon'], G.nodes[v]['lon']]
        y = [G.nodes[u]['lat'], G.nodes[v]['lat']]
        edge_traces.append(go.Scattergeo(
            lon=x,
            lat=y,
            mode='lines',
            line=dict(width=0.5, color='grey'),
            hoverinfo='none'
        ))
    
    # nós
    node_trace = go.Scattergeo(
        lon=[G.nodes[n]['lon'] for n in G.nodes()],
        lat=[G.nodes[n]['lat'] for n in G.nodes()],
        text=[G.nodes[n]['name'] for n in G.nodes()],
        mode='markers',
        marker=dict(size=6, color='blue'),
        hoverinfo='text'
    )
    
    # bfs tree
    path_trace = go.Scattergeo(
        lon=[G.nodes[n]['lon'] for n in path],
        lat=[G.nodes[n]['lat'] for n in path],
        mode='lines+markers',
        line=dict(width=3, color='red'),
        marker=dict(size=8, color='red'),
        hoverinfo='none'
    ) if path else None
    
    data = edge_traces + [node_trace]
    if path_trace:
        data.append(path_trace)
    
    fig = go.Figure(data=data)
    fig.update_layout(
        geo=dict(
            projection_type='natural earth',
            showland=True, landcolor='rgb(243,243,243)',
            showocean=True, oceancolor='rgb(230,245,255)',
            showcountries=True, countrycolor='rgb(204,204,204)'
        ),
        margin=dict(l=0,r=0,t=0,b=0)
    )
    return fig

# carregar dados 
# Determina o diretório do script atual e constrói o caminho correto
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(os.path.dirname(script_dir), "data")
airports_file = os.path.join(data_dir, "airports_min.csv")
routes_file = os.path.join(data_dir, "routes_min.csv")

if not os.path.exists(airports_file) or not os.path.exists(routes_file):
    raise FileNotFoundError("Certifique-se de que os arquivos CSV estão em ../data/")

airports_df = pd.read_csv(airports_file)
routes_df = pd.read_csv(routes_file)

# cria grafo
G = nx.Graph()
for _, row in airports_df.iterrows():
    G.add_node(row['id'], name=row['name'], lat=row['lat'], lon=row['lon'])
for _, row in routes_df.iterrows():
    if row['src_id'] in G.nodes and row['dst_id'] in G.nodes:
        G.add_edge(row['src_id'], row['dst_id'])

# cria app Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Grafo de Aeroportos no Mapa Mundial"),
    html.Div([
        html.Label("Origem:"),
        dcc.Dropdown(
            id="source",
            options=[{"label": G.nodes[n]['name'], "value": n} for n in G.nodes],
            placeholder="Selecione aeroporto de origem"
        ),
    ], style={"width": "48%", "display": "inline-block"}),
    html.Div([
        html.Label("Destino:"),
        dcc.Dropdown(
            id="target",
            options=[{"label": G.nodes[n]['name'], "value": n} for n in G.nodes],
            placeholder="Selecione aeroporto de destino"
        ),
    ], style={"width": "48%", "display": "inline-block"}),
    dcc.Graph(id="graph"),
    html.Div(id="path_output", style={"margin-top": "20px", "font-size": "18px"})
])

# callback 
@app.callback(
    [dash.Output("graph", "figure"),
     dash.Output("path_output", "children")],
    [dash.Input("source", "value"),
     dash.Input("target", "value")]
)
def update_graph(source, target):
    path = bfs_shortest_path(G, source, target) if source and target else []
    path_text = " → ".join([G.nodes[n]['name'] for n in path]) if path else "Selecione dois aeroportos ou não há caminho."
    fig = plot_geo_graph(G, path)
    return fig, path_text

# roda app
if __name__ == "__main__":
    app.run(debug=True)
