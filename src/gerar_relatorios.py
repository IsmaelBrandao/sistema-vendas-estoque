"""
Sistema de Análise de Vendas e Estoque
Módulo de geração de relatórios automatizados em Excel
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

class GeradorRelatorios:
    
    def __init__(self):
        self.data_processamento = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.path_reports = 'reports'
        
        if not os.path.exists(self.path_reports):
            os.makedirs(self.path_reports)
    
    def carregar_dados(self):
        self.df_produtos = pd.read_excel('data/produtos.xlsx')
        self.df_estoque = pd.read_excel('data/estoque_filiais.xlsx')
        self.df_vendas = pd.read_excel('data/vendas_jan_jun_2024.xlsx', sheet_name='Vendas_Completo')
        
        self.df_vendas['Data'] = pd.to_datetime(self.df_vendas['Data'], format='%d/%m/%Y')
        self.df_vendas = self.df_vendas[self.df_vendas['Valor Total'] > 0]
    
    def processar_vendas(self):
        vendas_processadas = self.df_vendas.groupby(['Cód. Produto', 'Produto', 'Categoria']).agg({
            'Qtd': 'sum',
            'Valor Total': 'sum',
            'ID Venda': 'count',
            'Desconto': 'sum'
        }).reset_index()
        
        vendas_processadas.columns = ['Código', 'Produto', 'Categoria', 'Unidades_Vendidas', 
                                       'Receita_Total', 'Num_Transacoes', 'Total_Descontos']
        
        vendas_processadas['Ticket_Medio'] = (vendas_processadas['Receita_Total'] / 
                                               vendas_processadas['Num_Transacoes']).round(2)
        
        vendas_processadas = vendas_processadas.sort_values('Receita_Total', ascending=False)
        
        return vendas_processadas
    
    def processar_estoque(self):
        self.df_estoque['Status'] = self.df_estoque.apply(
            lambda x: 'Crítico' if x['Quantidade Disponível'] < x['Estoque Mínimo'] * 0.5
            else 'Baixo' if x['Quantidade Disponível'] < x['Estoque Mínimo']
            else 'Normal', axis=1
        )
        
        self.df_estoque['Diferenca_Minimo'] = (self.df_estoque['Quantidade Disponível'] - 
                                                self.df_estoque['Estoque Mínimo'])
        
        estoque_critico = self.df_estoque[self.df_estoque['Status'].isin(['Crítico', 'Baixo'])].copy()
        estoque_critico = estoque_critico.sort_values('Diferenca_Minimo')
        
        return estoque_critico
    
    def calcular_kpis_filial(self):
        kpis = self.df_vendas.groupby('Filial').agg({
            'Valor Total': ['sum', 'mean', 'count'],
            'Qtd': 'sum',
            'Desconto': 'sum'
        }).round(2)
        
        kpis.columns = ['Faturamento', 'Ticket_Medio', 'Num_Vendas', 'Unidades', 'Descontos']
        kpis['Perc_Desconto'] = ((kpis['Descontos'] / kpis['Faturamento']) * 100).round(2)
        kpis = kpis.sort_values('Faturamento', ascending=False)
        
        return kpis.reset_index()
    
    def calcular_performance_mensal(self):
        self.df_vendas['Mes'] = self.df_vendas['Data'].dt.to_period('M')
        
        mensal = self.df_vendas.groupby('Mes').agg({
            'Valor Total': 'sum',
            'ID Venda': 'count',
            'Qtd': 'sum'
        }).reset_index()
        
        mensal.columns = ['Mes', 'Faturamento', 'Num_Vendas', 'Unidades']
        mensal['Mes'] = mensal['Mes'].astype(str)
        
        mensal['Crescimento_%'] = mensal['Faturamento'].pct_change() * 100
        mensal['Crescimento_%'] = mensal['Crescimento_%'].round(2)
        
        return mensal
    
    def gerar_relatorio_completo(self):
        nome_arquivo = f'{self.path_reports}/relatorio_vendas_estoque_{self.data_processamento}.xlsx'
        
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
            
            vendas_proc = self.processar_vendas()
            vendas_proc.to_excel(writer, sheet_name='Vendas_Produtos', index=False)
            
            estoque_crit = self.processar_estoque()
            estoque_crit.to_excel(writer, sheet_name='Alertas_Estoque', index=False)
            
            kpis_filial = self.calcular_kpis_filial()
            kpis_filial.to_excel(writer, sheet_name='Performance_Filiais', index=False)
            
            perf_mensal = self.calcular_performance_mensal()
            perf_mensal.to_excel(writer, sheet_name='Evolucao_Mensal', index=False)
            
            faturamento_total = self.df_vendas['Valor Total'].sum()
            total_vendas = len(self.df_vendas)
            ticket_medio = self.df_vendas['Valor Total'].mean()
            total_unidades = self.df_vendas['Qtd'].sum()
            
            resumo = pd.DataFrame({
                'Indicador': ['Faturamento Total', 'Total de Vendas', 'Ticket Médio', 
                              'Unidades Vendidas', 'Data Processamento'],
                'Valor': [f'R$ {faturamento_total:,.2f}', total_vendas, 
                          f'R$ {ticket_medio:.2f}', total_unidades, 
                          datetime.now().strftime('%d/%m/%Y %H:%M')]
            })
            resumo.to_excel(writer, sheet_name='Resumo_Executivo', index=False)
        
        return nome_arquivo
    
    def gerar_relatorio_estoque_detalhado(self):
        nome_arquivo = f'{self.path_reports}/relatorio_estoque_detalhado_{self.data_processamento}.xlsx'
        
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
            
            estoque_completo = self.df_estoque.copy()
            estoque_completo['Perc_Estoque_Minimo'] = (
                (estoque_completo['Quantidade Disponível'] / estoque_completo['Estoque Mínimo']) * 100
            ).round(1)
            estoque_completo.to_excel(writer, sheet_name='Estoque_Completo', index=False)
            
            por_filial = self.df_estoque.groupby('Filial').agg({
                'Quantidade Disponível': 'sum',
                'Código Produto': 'count'
            }).reset_index()
            por_filial.columns = ['Filial', 'Total_Unidades', 'Num_SKUs']
            por_filial.to_excel(writer, sheet_name='Estoque_Por_Filial', index=False)
            
            criticos = self.df_estoque[self.df_estoque['Quantidade Disponível'] < 
                                       self.df_estoque['Estoque Mínimo']].copy()
            criticos = criticos.sort_values('Quantidade Disponível')
            criticos.to_excel(writer, sheet_name='Reposicao_Urgente', index=False)
        
        return nome_arquivo

def main():
    print('\nIniciando geração de relatórios...\n')
    
    gerador = GeradorRelatorios()
    
    print('Carregando dados...')
    gerador.carregar_dados()
    
    print('Processando vendas e estoque...')
    relatorio_principal = gerador.gerar_relatorio_completo()
    print(f'Gerado: {relatorio_principal}')
    
    print('Gerando relatório detalhado de estoque...')
    relatorio_estoque = gerador.gerar_relatorio_estoque_detalhado()
    print(f'Gerado: {relatorio_estoque}')
    
    print('\nRelatórios gerados com sucesso!')
    print(f'Verifique a pasta: {gerador.path_reports}/\n')

if __name__ == '__main__':
    main()