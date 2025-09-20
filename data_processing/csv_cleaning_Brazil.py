import csv
import os

def process_airports_data():
    """
    Processa o arquivo airports.dat e cria airports_min.csv com apenas aeroportos do Brasil
    Formato airports.dat: Airport ID,Name,City,Country,IATA,ICAO,Latitude,Longitude,Altitude,Timezone,DST,Tz database time zone,Type,Source
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, '..', 'data', 'airports.dat')
    output_file = os.path.join(base_dir, '..', 'data', 'airports_min.csv')
    
    airports_processed = 0
    airports_skipped = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Escrever cabeçalho
            writer.writerow(['id', 'name', 'lat', 'lon'])
            
            for row in reader:
                if len(row) >= 8:
                    airport_id = row[0]
                    name = row[1]
                    country = row[3]
                    latitude = row[6]
                    longitude = row[7]
                    
                    # Filtrar apenas aeroportos do Brasil
                    if country.strip().upper() != 'BRAZIL':
                        airports_skipped += 1
                        continue
                    
                    # Verificar se lat/lon são válidos
                    try:
                        float(latitude)
                        float(longitude)
                        writer.writerow([airport_id, name, latitude, longitude])
                        airports_processed += 1
                    except ValueError:
                        print(f"Coordenadas inválidas para aeroporto {airport_id}: lat={latitude}, lon={longitude}")
                        airports_skipped += 1
                        continue
    
    except FileNotFoundError:
        print(f"Arquivo {input_file} não encontrado!")
        return 0, set()
    except Exception as e:
        print(f"Erro ao processar airports.dat: {e}")
        return 0, set()
    
    print(f"Processados {airports_processed} aeroportos do Brasil em airports_min.csv")
    print(f"Ignorados {airports_skipped} aeroportos de outros países")
    
    # Retorna também os IDs dos aeroportos brasileiros para usar no filtro de rotas
    brazilian_airport_ids = set()
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            brazilian_airport_ids = {row['id'] for row in reader}
    except Exception as e:
        print(f"Erro ao ler IDs dos aeroportos brasileiros: {e}")
    
    return airports_processed, brazilian_airport_ids

def process_routes_data(brazilian_airport_ids):
    """
    Processa o arquivo routes.dat e cria routes_min.csv com apenas rotas entre aeroportos brasileiros
    Formato routes.dat: Airline,Airline ID,Source airport,Source airport ID,Destination airport,Destination airport ID,Codeshare,Stops,Equipment
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, '..', 'data', 'routes.dat')
    output_file = os.path.join(base_dir, '..', 'data', 'routes_min.csv')
    
    routes_processed = 0
    invalid_routes = 0
    non_brazilian_routes = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Escrever cabeçalho
            writer.writerow(['src_id', 'dst_id'])
            
            unique_routes = set()
            for row in reader:
                if len(row) >= 6:  # Garantir que temos dados suficientes
                    src_airport_id = row[3]  # Source airport ID
                    dst_airport_id = row[5]  # Destination airport ID
                    
                    # Verificar se os IDs são válidos (não são \N e são numéricos)
                    if (src_airport_id != '\\N' and dst_airport_id != '\\N' and 
                        src_airport_id.isdigit() and dst_airport_id.isdigit()):
                        
                        # Verificar se ambos os aeroportos são brasileiros
                        if (src_airport_id in brazilian_airport_ids and 
                            dst_airport_id in brazilian_airport_ids):
                            
                            route_key = (src_airport_id, dst_airport_id)
                            if route_key not in unique_routes:
                                writer.writerow([src_airport_id, dst_airport_id])
                                unique_routes.add(route_key)
                                routes_processed += 1
                        else:
                            non_brazilian_routes += 1
                    else:
                        invalid_routes += 1
    
    except FileNotFoundError:
        print(f"Arquivo {input_file} não encontrado!")
        return 0
    except Exception as e:
        print(f"Erro ao processar routes.dat: {e}")
        return 0
    
    print(f"Processadas {routes_processed} rotas entre aeroportos brasileiros em routes_min.csv")
    print(f"Ignoradas {invalid_routes} rotas com IDs inválidos")
    print(f"Ignoradas {non_brazilian_routes} rotas que não são inteiramente brasileiras")
    return routes_processed

def main():
    """
    Função principal que executa o processamento dos dados filtrados para o Brasil
    """
    print("Iniciando processamento dos dados de aeroportos e rotas do Brasil...")
    print("=" * 70)
    
    # Processar aeroportos brasileiros
    print("1. Processando dados de aeroportos brasileiros...")
    airports_count, brazilian_airport_ids = process_airports_data()
    
    if airports_count == 0:
        print("❌ Erro: Nenhum aeroporto brasileiro foi processado!")
        return
    
    print(f"✓ {len(brazilian_airport_ids)} IDs de aeroportos brasileiros identificados")
    
    # Processar rotas entre aeroportos brasileiros
    print("\n2. Processando rotas entre aeroportos brasileiros...")
    routes_count = process_routes_data(brazilian_airport_ids)
    
    print("\n" + "=" * 70)
    print("RESUMO DO PROCESSAMENTO (APENAS BRASIL):")
    print(f"✓ Aeroportos brasileiros processados: {airports_count}")
    print(f"✓ Rotas entre aeroportos brasileiros: {routes_count}")
    print("\nArquivos gerados:")
    print("- ../data/airports_min.csv (aeroportos do Brasil: id, name, lat, lon)")
    print("- ../data/routes_min.csv (rotas domésticas brasileiras: src_id, dst_id)")

if __name__ == "__main__":
    main()