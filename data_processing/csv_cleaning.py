import csv
import os

def process_airports_data():
    """
    Processa o arquivo airports.dat e cria airports_min.csv com apenas id, name, lat, lon
    """
    input_file = os.path.join('..', 'data', 'airports.dat')
    output_file = os.path.join('..', 'data', 'airports_min.csv')
    
    airports_processed = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Escrever cabeçalho
            writer.writerow(['id', 'name', 'lat', 'lon'])
            
            for row in reader:
                if len(row) >= 8:  # Garantir que temos dados suficientes
                    airport_id = row[0]
                    name = row[1]
                    latitude = row[6]
                    longitude = row[7]
                    
                    # Verificar se lat/lon são válidos
                    try:
                        float(latitude)
                        float(longitude)
                        writer.writerow([airport_id, name, latitude, longitude])
                        airports_processed += 1
                    except ValueError:
                        print(f"Coordenadas inválidas para aeroporto {airport_id}: lat={latitude}, lon={longitude}")
                        continue
    
    except FileNotFoundError:
        print(f"Arquivo {input_file} não encontrado!")
        return 0
    except Exception as e:
        print(f"Erro ao processar airports.dat: {e}")
        return 0
    
    print(f"Processados {airports_processed} aeroportos em airports_min.csv")
    return airports_processed

def process_routes_data():
    """
    Processa o arquivo routes.dat e cria routes_min.csv com apenas src_id, dst_id, airline
    """
    input_file = os.path.join('..', 'data', 'routes.dat')
    output_file = os.path.join('..', 'data', 'routes_min.csv')
    
    routes_processed = 0
    invalid_routes = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Escrever cabeçalho
            writer.writerow(['src_id', 'dst_id', 'airline'])
            
            for row in reader:
                if len(row) >= 6:  # Garantir que temos dados suficientes
                    airline = row[0]
                    src_airport_id = row[3]  # Source airport ID
                    dst_airport_id = row[5]  # Destination airport ID
                    
                    # Verificar se os IDs são válidos (não são \N e são numéricos)
                    if (src_airport_id != '\\N' and dst_airport_id != '\\N' and 
                        src_airport_id.isdigit() and dst_airport_id.isdigit()):
                        writer.writerow([src_airport_id, dst_airport_id, airline])
                        routes_processed += 1
                    else:
                        invalid_routes += 1
    
    except FileNotFoundError:
        print(f"Arquivo {input_file} não encontrado!")
        return 0
    except Exception as e:
        print(f"Erro ao processar routes.dat: {e}")
        return 0
    
    print(f"Processadas {routes_processed} rotas válidas em routes_min.csv")
    print(f"Ignoradas {invalid_routes} rotas com IDs inválidos")
    return routes_processed

def main():
    """
    Função principal que executa o processamento dos dados
    """
    print("Iniciando processamento dos dados de aeroportos e rotas...")
    print("=" * 60)
    
    # Processar aeroportos
    print("1. Processando dados de aeroportos...")
    airports_count = process_airports_data()
    
    print("\n2. Processando dados de rotas...")
    routes_count = process_routes_data()
    
    print("\n" + "=" * 60)
    print("RESUMO DO PROCESSAMENTO:")
    print(f"✓ Aeroportos processados: {airports_count}")
    print(f"✓ Rotas processadas: {routes_count}")
    print("\nArquivos gerados:")
    print("- ../data/airports_min.csv (id, name, lat, lon)")
    print("- ../data/routes_min.csv (src_id, dst_id, airline)")

if __name__ == "__main__":
    main()