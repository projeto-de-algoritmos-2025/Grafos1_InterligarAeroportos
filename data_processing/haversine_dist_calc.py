import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
import os

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calcula a distância haversine entre dois pontos na Terra em quilômetros.
    
    Args:
        lat1, lon1: Latitude e longitude do primeiro ponto em graus
        lat2, lon2: Latitude e longitude do segundo ponto em graus
    
    Returns:
        Distância em quilômetros
    """
    # Converte graus para radianos
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Fórmula de Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Raio médio da Terra em quilômetros
    r = 6371
    return c * r

def add_distances_to_routes():
    """
    Adiciona coluna de distância ao arquivo routes_min.csv
    """
    # Caminhos dos arquivos
    airports_file = os.path.join("..", "data", "airports_min.csv")
    routes_file = os.path.join("..", "data", "routes_min.csv")
    
    # Verifica se os arquivos existem
    if not os.path.exists(airports_file):
        raise FileNotFoundError(f"Arquivo não encontrado: {airports_file}")
    if not os.path.exists(routes_file):
        raise FileNotFoundError(f"Arquivo não encontrado: {routes_file}")
    
    print("Carregando dados...")
    # Carrega os dados
    airports_df = pd.read_csv(airports_file)
    routes_df = pd.read_csv(routes_file)
    
    print(f"Aeroportos carregados: {len(airports_df)}")
    print(f"Rotas carregadas: {len(routes_df)}")
    
    # Cria dicionário para acesso rápido aos dados dos aeroportos
    airports_dict = {}
    for _, airport in airports_df.iterrows():
        airports_dict[airport['id']] = {
            'name': airport['name'],
            'lat': airport['lat'],
            'lon': airport['lon']
        }
    
    print("Calculando distâncias...")
    distances = []
    routes_with_missing_airports = 0
    
    # Calcula a distância para cada rota
    for idx, route in routes_df.iterrows():
        src_id = route['src_id']
        dst_id = route['dst_id']
        
        # Verifica se ambos os aeroportos existem nos dados
        if src_id in airports_dict and dst_id in airports_dict:
            src_airport = airports_dict[src_id]
            dst_airport = airports_dict[dst_id]
            
            # Calcula a distância
            distance = haversine_distance(
                src_airport['lat'], src_airport['lon'],
                dst_airport['lat'], dst_airport['lon']
            )
            distances.append(round(distance, 2))
        else:
            # Se algum aeroporto não for encontrado, adiciona NaN
            distances.append(np.nan)
            routes_with_missing_airports += 1
    
    # Adiciona a coluna de distância ao DataFrame
    routes_df['distance_km'] = distances
    
    print(f"Distâncias calculadas: {len(distances) - routes_with_missing_airports}")
    if routes_with_missing_airports > 0:
        print(f"Rotas com aeroportos não encontrados: {routes_with_missing_airports}")
    
    # Salva o arquivo atualizado
    routes_df.to_csv(routes_file, index=False)
    print(f"Arquivo atualizado salvo em: {routes_file}")
    
    # Estatísticas das distâncias
    valid_distances = routes_df['distance_km'].dropna()
    if len(valid_distances) > 0:
        print(f"\n=== ESTATÍSTICAS DAS DISTÂNCIAS ===")
        print(f"Distância mínima: {valid_distances.min():.2f} km")
        print(f"Distância máxima: {valid_distances.max():.2f} km")
        print(f"Distância média: {valid_distances.mean():.2f} km")
        print(f"Distância mediana: {valid_distances.median():.2f} km")
        
        # Mostra alguns exemplos
        print(f"\n=== EXEMPLOS DE ROTAS ===")
        sample_routes = routes_df.dropna().head(10)
        for _, route in sample_routes.iterrows():
            src_name = airports_dict[route['src_id']]['name']
            dst_name = airports_dict[route['dst_id']]['name']
            print(f"{src_name} → {dst_name}: {route['distance_km']:.2f} km")

if __name__ == "__main__":
    try:
        add_distances_to_routes()
    except Exception as e:
        print(f"Erro: {e}")
