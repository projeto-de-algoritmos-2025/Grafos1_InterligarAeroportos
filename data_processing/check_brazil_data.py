import pandas as pd

# Carrega e verifica os dados processados
routes = pd.read_csv('../data/routes_min.csv')
airports = pd.read_csv('../data/airports_min.csv')

print("=== DADOS PROCESSADOS PARA O BRASIL ===")
print(f"✓ Total de aeroportos brasileiros: {len(airports)}")
print(f"✓ Total de rotas entre aeroportos brasileiros: {len(routes)}")

# Verifica se já tem distâncias calculadas
if 'distance_km' in routes.columns:
    rotas_com_distancia = routes['distance_km'].notna().sum()
    rotas_sem_distancia = routes['distance_km'].isna().sum()
    print(f"✓ Rotas com distância calculada: {rotas_com_distancia}")
    print(f"✓ Rotas sem distância: {rotas_sem_distancia}")
    
    if rotas_com_distancia > 0:
        print(f"\n=== ESTATÍSTICAS DAS DISTÂNCIAS (KM) ===")
        distances = routes['distance_km'].dropna()
        print(f"Menor distância: {distances.min():.2f} km")
        print(f"Maior distância: {distances.max():.2f} km")
        print(f"Distância média: {distances.mean():.2f} km")
        print(f"Distância mediana: {distances.median():.2f} km")
else:
    print("⚠️  Coluna distance_km não encontrada - distâncias não foram calculadas")

print(f"\n=== EXEMPLOS DE AEROPORTOS BRASILEIROS ===")
print(airports.head())

print(f"\n=== EXEMPLOS DE ROTAS BRASILEIRAS ===")
print(routes.head())