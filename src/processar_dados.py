"""
Sistema de Análise de Vendas e Estoque
Módulo ETL - Extract, Transform, Load
Responsável por processar dados brutos e preparar para análise
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ProcessadorDados:
    
    def __init__(self):
        self.produtos = None
        self.estoque = None
        self.vendas = None
        
    def validar_produtos(self, df):
        df = df.copy()
        
        df = df.dropna(subset=['Código', 'Descrição', 'Preço Venda'])
        df = df[df['Preço Venda'] > 0]
        df = df[df['Custo Aquisição'] > 0]
        
        df['Descrição'] = df['Descrição'].str.strip()
        df['Categoria'] = df['Categoria'].str.strip()
        df['Fornecedor'] = df['Fornecedor'].str.strip()
        
        df['Margem_Real'] = ((df['Preço Venda'] - df['Custo Aquisição']) / 
                             df['Preço Venda'] * 100).round(2)
        
        df['Lucro_Unitario'] = (df['Preço Venda'] - df['Custo Aquisição']).round(2)
        
        return df
    
    def validar_estoque(self, df):
        df = df.copy()
        
        df = df.dropna(subset=['Código Produto', 'Filial', 'Quantidade Disponível'])
        df = df[df['Quantidade Disponível'] >= 0]
        
        df['Última Entrada'] = df['Última Entrada'].fillna('Não informado')
        df['Lote'] = df['Lote'].fillna('N/A')
        
        df['Nivel_Estoque'] = pd.cut(
            df['Quantidade Disponível'] / df['Estoque Mínimo'],
            bins=[0, 0.5, 1.0, float('inf')],
            labels=['Crítico', 'Baixo', 'Adequado']
        )
        
        df['Necessidade_Reposicao'] = np.where(
            df['Quantidade Disponível'] < df['Estoque Mínimo'],
            df['Estoque Mínimo'] - df['Quantidade Disponível'],
            0
        )
        
        return df
    
    def validar_vendas(self, df):
        df = df.copy()
        
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        df = df.dropna(subset=['Data'])
        
        df = df[df['Valor Total'] > 0]
        df = df[df['Qtd'] > 0]
        
        df['Ano'] = df['Data'].dt.year
        df['Mes'] = df['Data'].dt.month
        df['Trimestre'] = df['Data'].dt.quarter
        df['Dia_Semana'] = df['Data'].dt.dayofweek
        df['Nome_Dia'] = df['Data'].dt.day_name()
        df['Semana_Ano'] = df['Data'].dt.isocalendar().week
        
        df['Preco_Com_Desconto'] = np.where(
            df['Desconto'] > 0,
            df['Preço Unit.'] - (df['Preço Unit.'] * df['Desconto'] / 100),
            df['Preço Unit.']
        )
        
        df['Periodo_Dia'] = pd.cut(
            df['Hora'].str[:2].astype(int),
            bins=[0, 12, 18, 24],
            labels=['Manhã', 'Tarde', 'Noite'],
            include_lowest=True
        )
        
        return df
    
    def enriquecer_vendas_com_produtos(self):
        if self.vendas is None or self.produtos is None:
            raise ValueError("Dados de vendas e produtos devem ser carregados primeiro")
        
        vendas_enriquecidas = self.vendas.merge(
            self.produtos[['Código', 'Custo Aquisição', 'Margem_Real', 'Fornecedor']],
            left_on='Cód. Produto',
            right_on='Código',
            how='left'
        )
        
        vendas_enriquecidas['Lucro_Venda'] = (
            (vendas_enriquecidas['Valor Total'] - 
             (vendas_enriquecidas['Custo Aquisição'] * vendas_enriquecidas['Qtd']))
        ).round(2)
        
        vendas_enriquecidas['Margem_Venda_%'] = (
            (vendas_enriquecidas['Lucro_Venda'] / vendas_enriquecidas['Valor Total']) * 100
        ).round(2)
        
        return vendas_enriquecidas
    
    def calcular_metricas_agregadas(self, vendas_enriquecidas):
        metricas = {
            'por_produto': vendas_enriquecidas.groupby('Cód. Produto').agg({
                'Qtd': 'sum',
                'Valor Total': 'sum',
                'Lucro_Venda': 'sum',
                'ID Venda': 'count'
            }).round(2),
            
            'por_filial': vendas_enriquecidas.groupby('Filial').agg({
                'Valor Total': ['sum', 'mean', 'count'],
                'Lucro_Venda': 'sum',
                'Qtd': 'sum'
            }).round(2),
            
            'por_categoria': vendas_enriquecidas.groupby('Categoria').agg({
                'Valor Total': 'sum',
                'Lucro_Venda': 'sum',
                'Qtd': 'sum'
            }).round(2),
            
            'por_periodo': vendas_enriquecidas.groupby(['Mes', 'Ano']).agg({
                'Valor Total': 'sum',
                'Lucro_Venda': 'sum',
                'ID Venda': 'count'
            }).round(2)
        }
        
        return metricas
    
    def identificar_outliers_vendas(self, vendas_enriquecidas):
        q1 = vendas_enriquecidas['Valor Total'].quantile(0.25)
        q3 = vendas_enriquecidas['Valor Total'].quantile(0.75)
        iqr = q3 - q1
        
        limite_inferior = q1 - (1.5 * iqr)
        limite_superior = q3 + (1.5 * iqr)
        
        outliers = vendas_enriquecidas[
            (vendas_enriquecidas['Valor Total'] < limite_inferior) |
            (vendas_enriquecidas['Valor Total'] > limite_superior)
        ].copy()
        
        outliers['Tipo_Outlier'] = np.where(
            outliers['Valor Total'] > limite_superior,
            'Venda Alta',
            'Venda Baixa'
        )
        
        return outliers
    
    def gerar_dataset_analise(self, output_path='data/dataset_processado.xlsx'):
        vendas_enriquecidas = self.enriquecer_vendas_com_produtos()
        metricas = self.calcular_metricas_agregadas(vendas_enriquecidas)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            vendas_enriquecidas.to_excel(writer, sheet_name='Vendas_Processadas', index=False)
            self.produtos.to_excel(writer, sheet_name='Produtos_Validados', index=False)
            self.estoque.to_excel(writer, sheet_name='Estoque_Validado', index=False)
            
            for nome, df in metricas.items():
                df.to_excel(writer, sheet_name=f'Metricas_{nome}')
        
        return output_path
    
    def executar_pipeline(self):
        print('\nExecutando pipeline ETL...\n')
        
        print('1. Carregando dados brutos...')
        df_produtos_raw = pd.read_excel('data/produtos.xlsx')
        df_estoque_raw = pd.read_excel('data/estoque_filiais.xlsx')
        df_vendas_raw = pd.read_excel('data/vendas_jan_jun_2024.xlsx')
        
        print(f'   Produtos: {len(df_produtos_raw)} registros')
        print(f'   Estoque: {len(df_estoque_raw)} registros')
        print(f'   Vendas: {len(df_vendas_raw)} registros')
        
        print('\n2. Validando e transformando produtos...')
        self.produtos = self.validar_produtos(df_produtos_raw)
        print(f'   Produtos válidos: {len(self.produtos)}')
        
        print('\n3. Validando e transformando estoque...')
        self.estoque = self.validar_estoque(df_estoque_raw)
        print(f'   Registros válidos: {len(self.estoque)}')
        
        print('\n4. Validando e transformando vendas...')
        self.vendas = self.validar_vendas(df_vendas_raw)
        print(f'   Vendas válidas: {len(self.vendas)}')
        
        print('\n5. Enriquecendo dados de vendas...')
        vendas_enriquecidas = self.enriquecer_vendas_com_produtos()
        print(f'   Vendas enriquecidas: {len(vendas_enriquecidas)} registros')
        
        print('\n6. Calculando métricas agregadas...')
        metricas = self.calcular_metricas_agregadas(vendas_enriquecidas)
        print(f'   {len(metricas)} conjuntos de métricas gerados')
        
        print('\n7. Identificando outliers...')
        outliers = self.identificar_outliers_vendas(vendas_enriquecidas)
        print(f'   {len(outliers)} vendas atípicas identificadas')
        
        print('\n8. Gerando dataset processado...')
        output_file = self.gerar_dataset_analise()
        print(f'   Salvo em: {output_file}')
        
        print('\nPipeline ETL concluído com sucesso!\n')
        
        return {
            'produtos': self.produtos,
            'estoque': self.estoque,
            'vendas': vendas_enriquecidas,
            'metricas': metricas,
            'outliers': outliers
        }

def main():
    processador = ProcessadorDados()
    resultado = processador.executar_pipeline()
    
    print('Resumo do processamento:')
    print(f'- Produtos processados: {len(resultado["produtos"])}')
    print(f'- Estoque processado: {len(resultado["estoque"])}')
    print(f'- Vendas processadas: {len(resultado["vendas"])}')
    print(f'- Outliers identificados: {len(resultado["outliers"])}')
    print()

if __name__ == '__main__':
    main()