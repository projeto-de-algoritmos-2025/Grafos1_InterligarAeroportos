import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from math import radians, cos, sin, asin, sqrt, atan2, degrees
import networkx as nx
from typing import List, Tuple, Dict
import os

class AirportMapVisualizer:
    def __init__(self, airports_file: str, routes_file: str):
        """
        Inicializa o visualizador de mapas de aeroportos
        
        Args:
            airports_file: Caminho para o arquivo airports_min.csv
            routes_file: Caminho para o arquivo routes_min.csv
        """
        self.airports_df = pd.read_csv(airports_file)
        self.routes_df = pd.read_csv(routes_file)
        self.graph = nx.Graph()
        self._build_graph()
        
    def _build_graph(self):
        """Constrói o grafo NetworkX a partir dos dados"""
        # Adicionar nós (aeroportos)
        for _, airport in self.airports_df.iterrows():
            self.graph.add_node(
                airport['id'],
                name=airport['name'],
                lat=airport['lat'],
                lon=airport['lon']
            )
        
        # Adicionar arestas (rotas)
        for _, route in self.routes_df.iterrows():
            if route['src_id'] in self.graph.nodes and route['dst_id'] in self.graph.nodes:
                self.graph.add_edge(
                    route['src_id'],
                    route['dst_id']
                )
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcula a distância haversine entre dois pontos na Terra
        
        Args:
            lat1, lon1: Latitude e longitude do primeiro ponto
            lat2, lon2: Latitude e longitude do segundo ponto
            
        Returns:
            Distância em quilômetros
        """
        # Converter para radianos
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Fórmula haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Raio da Terra em km
        r = 6371
        return c * r
    
    def great_circle_path(self, lat1: float, lon1: float, lat2: float, lon2: float, num_points: int = 100) -> Tuple[List[float], List[float]]:
        """
        Calcula pontos ao longo do círculo máximo entre dois pontos
        para criar rotas curvadas que seguem a curvatura da Terra
        
        Args:
            lat1, lon1: Latitude e longitude do ponto inicial
            lat2, lon2: Latitude e longitude do ponto final
            num_points: Número de pontos intermediários
            
        Returns:
            Tupla com listas de latitudes e longitudes
        """
        # Converter para radianos
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Calcular distância angular
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # Gerar pontos intermediários
        lats, lons = [], []
        for i in range(num_points + 1):
            f = i / num_points
            
            A = sin((1-f) * c) / sin(c) if sin(c) != 0 else 1-f
            B = sin(f * c) / sin(c) if sin(c) != 0 else f
            
            x = A * cos(lat1) * cos(lon1) + B * cos(lat2) * cos(lon2)
            y = A * cos(lat1) * sin(lon1) + B * cos(lat2) * sin(lon2)
            z = A * sin(lat1) + B * sin(lat2)
            
            lat = atan2(z, sqrt(x**2 + y**2))
            lon = atan2(y, x)
            
            lats.append(degrees(lat))
            lons.append(degrees(lon))
        
        return lats, lons
    
    def get_top_airports(self, n: int = 50) -> pd.DataFrame:
        """
        Retorna os N aeroportos com mais conexões
        
        Args:
            n: Número de aeroportos para retornar
            
        Returns:
            DataFrame com os top aeroportos
        """
        # Contar conexões por aeroporto
        airport_connections = {}
        for airport_id in self.graph.nodes():
            airport_connections[airport_id] = len(list(self.graph.neighbors(airport_id)))
        
        # Ordenar por número de conexões
        top_airports_ids = sorted(airport_connections.keys(), 
                                key=lambda x: airport_connections[x], 
                                reverse=True)[:n]
        
        return self.airports_df[self.airports_df['id'].isin(top_airports_ids)]
    
    def create_full_map(self):
        """
        Cria um mapa interativo com todos os aeroportos e todas as rotas.
        """
        fig = go.Figure()

        print(f"Adicionando {len(self.routes_df)} rotas ao mapa...")
        # Adiciona todas as rotas
        for idx, route in self.routes_df.iterrows():
            src_airport = self.airports_df[self.airports_df['id'] == route['src_id']]
            dst_airport = self.airports_df[self.airports_df['id'] == route['dst_id']]
            if src_airport.empty or dst_airport.empty:
                continue
            src_airport = src_airport.iloc[0]
            dst_airport = dst_airport.iloc[0]
            lats, lons = self.great_circle_path(
                src_airport['lat'], src_airport['lon'],
                dst_airport['lat'], dst_airport['lon'],
                num_points=30
            )
            fig.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                mode='lines',
                line=dict(width=0.5, color='rgba(255, 0, 0, 0.2)'),
                showlegend=False,
                hovertemplate=f'<b>Rota:</b> {src_airport["name"]} → {dst_airport["name"]}<br>' +
                             f'<b>Distância:</b> {self.haversine_distance(src_airport["lat"], src_airport["lon"], dst_airport["lat"], dst_airport["lon"]):.0f} km<extra></extra>'
            ))

        # Adiciona todos os aeroportos
        airport_connections = [len(list(self.graph.neighbors(aid))) for aid in self.airports_df['id']]
        airport_sizes = [max(3, min(12, 3 + (c / 50) * 9)) for c in airport_connections]

        fig.add_trace(go.Scattergeo(
            lon=self.airports_df['lon'],
            lat=self.airports_df['lat'],
            mode='markers',
            marker=dict(
                size=airport_sizes,
                color=airport_connections,
                colorscale='Viridis',
                colorbar=dict(title=dict(text="Conexões")),
                line=dict(width=0.5, color='white'),
                sizemode='diameter'
            ),
            text=self.airports_df['name'],
            customdata=list(zip(self.airports_df['id'], airport_connections)),
            hovertemplate='<b>%{text}</b><br>' +
                         'ID: %{customdata[0]}<br>' +
                         'Lat: %{lat:.2f}<br>' +
                         'Lon: %{lon:.2f}<br>' +
                         'Conexões: %{customdata[1]}<extra></extra>',
            name='Aeroportos'
        ))

        fig.update_layout(
            title={
                'text': 'Mapa Mundial de Todos os Aeroportos e Rotas',
                'x': 0.5,
                'font': {'size': 20}
            },
            geo=dict(
                projection_type='natural earth',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                coastlinecolor='rgb(204, 204, 204)',
                showocean=True,
                oceancolor='rgb(230, 245, 255)',
                showlakes=True,
                lakecolor='rgb(230, 245, 255)',
                showrivers=True,
                rivercolor='rgb(230, 245, 255)',
                showcountries=True,
                countrycolor='rgb(204, 204, 204)',
                resolution=50
            ),
            width=1400,
            height=800,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        return fig
    
    def create_route_analysis_map(self, hub_airports: List[str] = None):
        """
        Cria um mapa focado nos principais hubs aéreos
        
        Args:
            hub_airports: Lista de códigos IATA dos aeroportos hub
        """
        if hub_airports is None:
            # Alguns dos principais hubs mundiais
            hub_airports = ['ATL', 'LAX', 'LHR', 'DXB', 'NRT', 'CDG', 'FRA', 'AMS', 'SIN', 'JFK']
        
        # Encontrar aeroportos hub no dataset
        hub_data = []
        for _, airport in self.airports_df.iterrows():
            airport_name = str(airport['name']).upper()
            for hub in hub_airports:
                if hub in airport_name:
                    connections = len(list(self.graph.neighbors(airport['id'])))
                    hub_data.append({
                        'id': airport['id'],
                        'name': airport['name'],
                        'lat': airport['lat'],
                        'lon': airport['lon'],
                        'connections': connections
                    })
                    break
        
        if not hub_data:
            print("Nenhum aeroporto hub encontrado. Usando os 10 aeroportos com mais conexões.")
            hub_data = self.get_top_airports(10).to_dict('records')
            for item in hub_data:
                item['connections'] = len(list(self.graph.neighbors(item['id'])))
        
        fig = go.Figure()
        
        # Adicionar rotas dos hubs
        for hub in hub_data:
            hub_routes = self.routes_df[
                (self.routes_df['src_id'] == hub['id']) |
                (self.routes_df['dst_id'] == hub['id'])
            ].head(50)  # Limitar a 50 rotas por hub
            
            for _, route in hub_routes.iterrows():
                if route['src_id'] == hub['id']:
                    dst_airport = self.airports_df[self.airports_df['id'] == route['dst_id']]
                else:
                    dst_airport = self.airports_df[self.airports_df['id'] == route['src_id']]
                
                if not dst_airport.empty:
                    dst_airport = dst_airport.iloc[0]
                    
                    lats, lons = self.great_circle_path(
                        hub['lat'], hub['lon'],
                        dst_airport['lat'], dst_airport['lon'],
                        num_points=30
                    )
                    
                    fig.add_trace(go.Scattergeo(
                        lon=lons,
                        lat=lats,
                        mode='lines',
                        line=dict(width=1, color='rgba(0, 100, 255, 0.4)'),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
        
        # Adicionar aeroportos hub
        hub_df = pd.DataFrame(hub_data)
        fig.add_trace(go.Scattergeo(
            lon=hub_df['lon'],
            lat=hub_df['lat'],
            mode='markers',
            marker=dict(
                size=[15 + (c/100)*10 for c in hub_df['connections']],
                color='red',
                line=dict(width=2, color='white'),
                symbol='diamond'
            ),
            text=hub_df['name'],
            customdata=hub_df['connections'],
            hovertemplate='<b>%{text}</b><br>' +
                         'Conexões: %{customdata}<br>' +
                         'Lat: %{lat:.2f}<br>' +
                         'Lon: %{lon:.2f}<extra></extra>',
            name='Aeroportos Hub'
        ))
        
        fig.update_layout(
            title={
                'text': 'Principais Hubs Aéreos Mundiais',
                'x': 0.5,
                'font': {'size': 20}
            },
            geo=dict(
                projection_type='orthographic',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                coastlinecolor='rgb(204, 204, 204)',
                showocean=True,
                oceancolor='rgb(230, 245, 255)'
            ),
            width=1200,
            height=800
        )
        
        return fig
    
    def get_network_statistics(self):
        """Retorna estatísticas da rede de aeroportos"""
        stats = {
            'total_airports': len(self.graph.nodes()),
            'total_routes': len(self.graph.edges()),
            'avg_connections': np.mean([len(list(self.graph.neighbors(node))) for node in self.graph.nodes()]),
            'max_connections': max([len(list(self.graph.neighbors(node))) for node in self.graph.nodes()]),
            'connected_components': nx.number_connected_components(self.graph),
            'diameter': nx.diameter(self.graph) if nx.is_connected(self.graph) else 'N/A (grafo não conectado)'
        }
        return stats

def main():
    """Função principal para demonstrar o uso da classe"""
    # Caminhos dos arquivos
    airports_file = os.path.join('..', 'data', 'airports_min.csv')
    routes_file = os.path.join('..', 'data', 'routes_min.csv')
    
    # Verificar se os arquivos existem
    if not os.path.exists(airports_file) or not os.path.exists(routes_file):
        print("Erro: Arquivos de dados não encontrados!")
        print(f"Procurando por: {airports_file} e {routes_file}")
        return
    
    # Criar visualizador
    print("Carregando dados...")
    visualizer = AirportMapVisualizer(airports_file, routes_file)
    
    # Mostrar estatísticas
    stats = visualizer.get_network_statistics()
    print("\n=== ESTATÍSTICAS DA REDE ===")
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    # Criar mapa interativo completo
    print("\nCriando mapa interativo completo...")
    fig = visualizer.create_full_map()
    # Salvar mapa como HTML
    print("Salvando mapa...")
    fig.write_html("airport_full_map.html")
    print("\n✅ Mapa criado com sucesso!")
    print("📁 Arquivo gerado:")
    print("  - airport_full_map.html (Mapa completo)")
    print("\nAbra o arquivo HTML no seu navegador para visualizar o mapa interativo!")
    # Mostrar mapa no navegador (opcional)
    try:
        fig.show()
    except Exception as e:
        print(f"Nota: Não foi possível abrir automaticamente no navegador: {e}")

if __name__ == "__main__":
    main()