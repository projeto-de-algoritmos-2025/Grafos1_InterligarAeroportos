import os
import sys

def main():
    try:
        # Add backend directory to Python path
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        sys.path.insert(0, backend_path)
        
        # Import and run the graph application
        from graph import app, G
        
        print("� Inicializando aplicação de visualização de aeroportos brasileiros...")
        print("=" * 70)
        print("📊 Carregando módulo de visualização de grafos...")
        print(f"✅ Aplicação carregada com sucesso!")
        print(f"📍 {len(G.nodes())} aeroportos brasileiros carregados")
        print(f"🛣️  {len(G.edges())} rotas domésticas carregadas")
        print()
        print("🌐 Iniciando servidor web...")
        print("📱 Acesse: http://localhost:8050")
        print("🔄 Para parar a aplicação: Ctrl+C")
        print("=" * 70)
        
        # Run the Dash app (sem debug para evitar duplicação de output)
        app.run(debug=False, host='localhost', port=8050)
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        print("💡 Verifique se o arquivo backend/graph.py existe e está correto")
        sys.exit(1)
        
    except FileNotFoundError as e:
        print(f"❌ Arquivo de dados não encontrado: {e}")
        print("💡 Execute primeiro o script data_processing/csv_cleaning_Brazil.py")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print("💡 Verifique se todas as dependências estão instaladas:")
        print("   pip install pandas networkx dash plotly")
        sys.exit(1)

if __name__ == "__main__":
    main()
