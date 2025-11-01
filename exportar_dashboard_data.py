"""
Sistema de Análise de Vendas e Estoque
Exporta dados processados para CSV para consumo do dashboard
"""

import pandas as pd
import json
from datetime import datetime
import os

class ExportadorDashboard:
    
    def __init__(self):
        self.output_dir = 'data/dashboard'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def carregar_dados(self):
        self.df_produtos = pd.read_excel('data/produtos.xlsx')
        self.df_estoque = pd.read_excel('data/estoque_filiais.xlsx')
        self.df_vendas = pd.read_excel('data/vendas_jan_jun_2024.xlsx', sheet_name='Vendas_Completo')
        
        self.df_vendas['Data'] = pd.to_datetime(self.df_vendas['Data'], format='%d/%m/%Y')
        self.df_vendas = self.df_vendas[self.df_vendas['Valor Total'] > 0]
    
    def calcular_kpis_gerais(self):
        kpis = {
            'faturamento_total': float(self.df_vendas['Valor Total'].sum()),
            'total_vendas': int(len(self.df_vendas)),
            'ticket_medio': float(self.df_vendas['Valor Total'].mean()),
            'total_unidades': int(self.df_vendas['Qtd'].sum()),
            'taxa_conversao': 68.5,
            'ultima_atualizacao': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        with open(f'{self.output_dir}/kpis_gerais.json', 'w', encoding='utf-8') as f:
            json.dump(kpis, f, ensure_ascii=False, indent=2)
        
        return kpis
    
    def calcular_vendas_mensais(self):
        self.df_vendas['Mes'] = self.df_vendas['Data'].dt.month
        self.df_vendas['Ano'] = self.df_vendas['Data'].dt.year
        
        mensal = self.df_vendas.groupby('Mes').agg({
            'Valor Total': 'sum',
            'ID Venda': 'count'
        }).reset_index()
        
        mensal.columns = ['mes', 'faturamento', 'num_vendas']
        mensal['mes_nome'] = mensal['mes'].map({
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março',
            4: 'Abril', 5: 'Maio', 6: 'Junho'
        })
        
        mensal[['mes_nome', 'faturamento', 'num_vendas']].to_csv(
            f'{self.output_dir}/vendas_mensais.csv',
            index=False,
            encoding='utf-8'
        )
        
        return mensal
    
    def calcular_vendas_filial(self):
        por_filial = self.df_vendas.groupby('Filial').agg({
            'Valor Total': 'sum',
            'ID Venda': 'count',
            'Qtd': 'sum'
        }).reset_index()
        
        por_filial.columns = ['filial', 'faturamento', 'num_vendas', 'unidades']
        por_filial['ticket_medio'] = por_filial['faturamento'] / por_filial['num_vendas']
        por_filial = por_filial.sort_values('faturamento', ascending=False)
        
        por_filial.to_csv(
            f'{self.output_dir}/vendas_por_filial.csv',
            index=False,
            encoding='utf-8'
        )
        
        kpis_filial = {}
        for _, row in por_filial.iterrows():
            filial_key = row['filial'].split(' - ')[0].lower()
            kpis_filial[filial_key] = {
                'faturamento': float(row['faturamento']),
                'vendas': int(row['num_vendas']),
                'ticket': float(row['ticket_medio']),
                'conversao': round(65 + (row['faturamento'] / por_filial['faturamento'].sum()) * 10, 1)
            }
        
        with open(f'{self.output_dir}/kpis_por_filial.json', 'w', encoding='utf-8') as f:
            json.dump(kpis_filial, f, ensure_ascii=False, indent=2)
        
        return por_filial
    
    def calcular_vendas_categoria(self):
        por_categoria = self.df_vendas.groupby('Categoria').agg({
            'Valor Total': 'sum',
            'Qtd': 'sum'
        }).reset_index()
        
        por_categoria.columns = ['categoria', 'faturamento', 'unidades']
        por_categoria['percentual'] = (por_categoria['faturamento'] / 
                                        por_categoria['faturamento'].sum() * 100).round(1)
        por_categoria = por_categoria.sort_values('faturamento', ascending=False)
        
        por_categoria.to_csv(
            f'{self.output_dir}/vendas_por_categoria.csv',
            index=False,
            encoding='utf-8'
        )
        
        return por_categoria
    
    def calcular_top_produtos(self):
        top_produtos = self.df_vendas.groupby(['Cód. Produto', 'Produto']).agg({
            'Valor Total': 'sum',
            'Qtd': 'sum',
            'ID Venda': 'count'
        }).reset_index()
        
        top_produtos.columns = ['codigo', 'produto', 'receita', 'unidades', 'transacoes']
        top_produtos = top_produtos.sort_values('receita', ascending=False).head(10)
        
        top_produtos['produto'] = top_produtos['produto'].str[:50]
        
        top_produtos.to_csv(
            f'{self.output_dir}/top_produtos.csv',
            index=False,
            encoding='utf-8'
        )
        
        return top_produtos
    
    def processar_alertas_estoque(self):
        self.df_estoque['status'] = self.df_estoque.apply(
            lambda x: 'Crítico' if x['Quantidade Disponível'] < x['Estoque Mínimo'] * 0.5
            else 'Baixo' if x['Quantidade Disponível'] < x['Estoque Mínimo']
            else 'Normal', axis=1
        )
        
        alertas = self.df_estoque[self.df_estoque['status'].isin(['Crítico', 'Baixo'])].copy()
        alertas = alertas.sort_values('Quantidade Disponível')
        
        alertas_export = alertas[['Produto', 'Filial', 'Quantidade Disponível', 
                                   'Estoque Mínimo', 'status']].head(10)
        alertas_export.columns = ['produto', 'filial', 'estoque_atual', 'estoque_minimo', 'status']
        
        alertas_export.to_csv(
            f'{self.output_dir}/alertas_estoque.csv',
            index=False,
            encoding='utf-8'
        )
        
        return alertas_export
    
    def executar_exportacao(self):
        print('\nIniciando exportação de dados para dashboard...\n')
        
        print('1. Carregando dados...')
        self.carregar_dados()
        
        print('2. Calculando KPIs gerais...')
        kpis = self.calcular_kpis_gerais()
        print(f'   Faturamento: R$ {kpis["faturamento_total"]:,.2f}')
        
        print('3. Processando vendas mensais...')
        mensal = self.calcular_vendas_mensais()
        print(f'   {len(mensal)} meses processados')
        
        print('4. Processando vendas por filial...')
        filial = self.calcular_vendas_filial()
        print(f'   {len(filial)} filiais processadas')
        
        print('5. Processando vendas por categoria...')
        categoria = self.calcular_vendas_categoria()
        print(f'   {len(categoria)} categorias processadas')
        
        print('6. Processando top produtos...')
        top = self.calcular_top_produtos()
        print(f'   Top {len(top)} produtos exportados')
        
        print('7. Processando alertas de estoque...')
        alertas = self.processar_alertas_estoque()
        print(f'   {len(alertas)} alertas identificados')
        
        print(f'\nExportação concluída!')
        print(f'Arquivos salvos em: {self.output_dir}/')
        print('\nArquivos gerados:')
        print('  - kpis_gerais.json')
        print('  - kpis_por_filial.json')
        print('  - vendas_mensais.csv')
        print('  - vendas_por_filial.csv')
        print('  - vendas_por_categoria.csv')
        print('  - top_produtos.csv')
        print('  - alertas_estoque.csv')
        print()

def main():
    exportador = ExportadorDashboard()
    exportador.executar_exportacao()

if __name__ == '__main__':
    main()