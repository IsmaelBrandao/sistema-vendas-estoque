"""
Sistema de Análise de Vendas e Estoque
Arquivo: analise_vendas.py

Este é o código PRINCIPAL do sistema.
Lê as planilhas, limpa os dados, calcula KPIs e gera insights.

Autor: Seu Nome
Data: 2024
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURAÇÕES
# ============================================================
print("\n" + "=" * 70)
print(" SISTEMA DE ANÁLISE DE VENDAS E ESTOQUE")
print("=" * 70)
print(f"Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("=" * 70 + "\n")

# ============================================================
# ETAPA 1: CARREGAR OS DADOS
# ============================================================
print("📂 [ETAPA 1/5] CARREGANDO DADOS DAS PLANILHAS...")
print("-" * 70)

try:
    # Carregar produtos
    print("   Lendo: data/produtos.xlsx")
    df_produtos = pd.read_excel('data/produtos.xlsx', sheet_name='Cadastro_Produtos')
    print(f"    {len(df_produtos)} produtos carregados")
    
    # Carregar estoque
    print("   Lendo: data/estoque_filiais.xlsx")
    df_estoque = pd.read_excel('data/estoque_filiais.xlsx', sheet_name='Posicao_Estoque')
    print(f"    {len(df_estoque)} registros de estoque carregados")
    
    # Carregar vendas
    print("   Lendo: data/vendas_jan_jun_2024.xlsx")
    df_vendas = pd.read_excel('data/vendas_jan_jun_2024.xlsx', sheet_name='Vendas_Completo')
    print(f"    {len(df_vendas)} vendas carregadas")
    
except FileNotFoundError as e:
    print(f"\n ERRO: Arquivo não encontrado!")
    print(f"   {e}")
    print("\n💡 Certifique-se de ter executado 'setup_planilhas.py' primeiro")
    exit(1)

print("\n Todos os dados carregados com sucesso!\n")

# ============================================================
# ETAPA 2: LIMPEZA E VALIDAÇÃO DOS DADOS
# ============================================================
print(" [ETAPA 2/5] LIMPEZA E VALIDAÇÃO DOS DADOS...")
print("-" * 70)

# ----- LIMPAR PRODUTOS -----
print("\n Limpando dados de PRODUTOS:")
produtos_antes = len(df_produtos)

# Remover espaços extras
df_produtos['Descrição'] = df_produtos['Descrição'].str.strip()
df_produtos['Categoria'] = df_produtos['Categoria'].str.strip()

# Validar preços
df_produtos = df_produtos[df_produtos['Preço Venda'] > 0]
df_produtos = df_produtos[df_produtos['Custo Aquisição'] > 0]

# Calcular margem real
df_produtos['Margem Lucro (%)'] = ((df_produtos['Preço Venda'] - df_produtos['Custo Aquisição']) / df_produtos['Preço Venda'] * 100).round(2)

print(f"   • Produtos válidos: {len(df_produtos)}/{produtos_antes}")
print(f"   • Campos limpos: Descrição, Categoria")
print(f"   • Margem de lucro calculada")

# ----- LIMPAR ESTOQUE -----
print("\n Limpando dados de ESTOQUE:")
estoque_antes = len(df_estoque)

# Preencher valores vazios
df_estoque['Última Entrada'] = df_estoque['Última Entrada'].fillna('Sem registro')
df_estoque['Lote'] = df_estoque['Lote'].fillna('N/A')

# Criar coluna de status do estoque
df_estoque['Status Estoque'] = df_estoque.apply(
    lambda row: 'CRÍTICO' if row['Quantidade Disponível'] < row['Estoque Mínimo'] * 0.5
    else 'BAIXO' if row['Quantidade Disponível'] < row['Estoque Mínimo']
    else 'NORMAL', axis=1
)

# Calcular percentual do estoque mínimo
df_estoque['% do Mínimo'] = ((df_estoque['Quantidade Disponível'] / df_estoque['Estoque Mínimo']) * 100).round(1)

print(f"   • Registros válidos: {len(df_estoque)}/{estoque_antes}")
print(f"   • Campos vazios preenchidos: Última Entrada, Lote")
print(f"   • Status de estoque calculado")

# ----- LIMPAR VENDAS -----
print("\n Limpando dados de VENDAS:")
vendas_antes = len(df_vendas)

# Converter data para formato correto
df_vendas['Data'] = pd.to_datetime(df_vendas['Data'], format='%d/%m/%Y', errors='coerce')

# Remover vendas com data inválida
df_vendas = df_vendas.dropna(subset=['Data'])

# Extrair informações da data
df_vendas['Ano'] = df_vendas['Data'].dt.year
df_vendas['Mês'] = df_vendas['Data'].dt.month
df_vendas['Mês Nome'] = df_vendas['Data'].dt.strftime('%B')
df_vendas['Dia Semana'] = df_vendas['Data'].dt.day_name()

# Preencher CPF vazio
df_vendas['CPF Cliente'] = df_vendas['CPF Cliente'].fillna('Não informado')

# Remover vendas com valor zerado ou negativo
df_vendas = df_vendas[df_vendas['Valor Total'] > 0]

# Calcular ticket por categoria
df_vendas['Ticket Categoria'] = df_vendas.groupby('Categoria')['Valor Total'].transform('mean')

print(f"   • Vendas válidas: {len(df_vendas)}/{vendas_antes}")
print(f"   • Vendas removidas (inválidas): {vendas_antes - len(df_vendas)}")
print(f"   • Datas convertidas e validadas")
print(f"   • Campos calculados: Mês, Ano, Dia da Semana")

print("\n Limpeza concluída!\n")

# ============================================================
# ETAPA 3: ANÁLISE DE VENDAS - KPIs PRINCIPAIS
# ============================================================
print(" [ETAPA 3/5] CALCULANDO KPIs DE VENDAS...")
print("-" * 70)

# KPIs Gerais
total_vendas = len(df_vendas)
faturamento_total = df_vendas['Valor Total'].sum()
ticket_medio = df_vendas['Valor Total'].mean()
total_unidades = df_vendas['Qtd'].sum()
desconto_total = df_vendas['Desconto'].sum()

print(f"\n KPIs GERAIS (Jan-Jun 2024):")
print(f"   • Total de Vendas: {total_vendas:,} transações")
print(f"   • Faturamento Total: R$ {faturamento_total:,.2f}")
print(f"   • Ticket Médio: R$ {ticket_medio:.2f}")
print(f"   • Unidades Vendidas: {total_unidades:,}")
print(f"   • Total em Descontos: R$ {desconto_total:,.2f}")
print(f"   • % Desconto sobre Vendas: {(desconto_total/faturamento_total*100):.2f}%")

# ----- ANÁLISE POR FILIAL -----
print(f"\n🏪 PERFORMANCE POR FILIAL:")
vendas_filial = df_vendas.groupby('Filial').agg({
    'ID Venda': 'count',
    'Valor Total': ['sum', 'mean'],
    'Qtd': 'sum',
    'Desconto': 'sum'
}).round(2)

vendas_filial.columns = ['Qtd_Vendas', 'Faturamento', 'Ticket_Medio', 'Unidades', 'Descontos']
vendas_filial['% do Total'] = (vendas_filial['Faturamento'] / faturamento_total * 100).round(2)
vendas_filial = vendas_filial.sort_values('Faturamento', ascending=False)

for filial in vendas_filial.index:
    print(f"\n   📍 {filial}:")
    print(f"      • Faturamento: R$ {vendas_filial.loc[filial, 'Faturamento']:,.2f} ({vendas_filial.loc[filial, '% do Total']:.1f}%)")
    print(f"      • Vendas: {int(vendas_filial.loc[filial, 'Qtd_Vendas'])} transações")
    print(f"      • Ticket Médio: R$ {vendas_filial.loc[filial, 'Ticket_Medio']:.2f}")
    print(f"      • Unidades: {int(vendas_filial.loc[filial, 'Unidades'])}")

# ----- ANÁLISE POR CATEGORIA -----
print(f"\n🎯 VENDAS POR CATEGORIA:")
vendas_categoria = df_vendas.groupby('Categoria').agg({
    'Valor Total': 'sum',
    'Qtd': 'sum',
    'ID Venda': 'count'
}).round(2)

vendas_categoria.columns = ['Faturamento', 'Unidades', 'Transações']
vendas_categoria['% Faturamento'] = (vendas_categoria['Faturamento'] / faturamento_total * 100).round(2)
vendas_categoria = vendas_categoria.sort_values('Faturamento', ascending=False)

for categoria in vendas_categoria.index:
    print(f"   • {categoria}: R$ {vendas_categoria.loc[categoria, 'Faturamento']:,.2f} ({vendas_categoria.loc[categoria, '% Faturamento']:.1f}%) - {int(vendas_categoria.loc[categoria, 'Unidades'])} unidades")

# ----- TOP 10 PRODUTOS MAIS VENDIDOS -----
print(f"\n🏆 TOP 10 PRODUTOS MAIS VENDIDOS:")
top_produtos = df_vendas.groupby(['Cód. Produto', 'Produto']).agg({
    'Valor Total': 'sum',
    'Qtd': 'sum',
    'ID Venda': 'count'
}).round(2)

top_produtos.columns = ['Receita', 'Unidades', 'Transações']
top_produtos = top_produtos.sort_values('Receita', ascending=False).head(10)

for i, (cod, nome) in enumerate(top_produtos.index, 1):
    receita = top_produtos.loc[(cod, nome), 'Receita']
    unidades = int(top_produtos.loc[(cod, nome), 'Unidades'])
    print(f"   {i}. {nome[:45]}...")
    print(f"      → R$ {receita:,.2f} | {unidades} unidades vendidas")

# ----- ANÁLISE TEMPORAL -----
print(f"\n📈 EVOLUÇÃO MENSAL:")
vendas_mes = df_vendas.groupby('Mês').agg({
    'Valor Total': 'sum',
    'ID Venda': 'count'
}).round(2)

meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho'}

for mes in sorted(vendas_mes.index):
    valor = vendas_mes.loc[mes, 'Valor Total']
    qtd = int(vendas_mes.loc[mes, 'ID Venda'])
    print(f"   • {meses[mes]}: R$ {valor:,.2f} ({qtd} vendas)")

print("\n✅ Análise de vendas concluída!\n")

# ============================================================
# ETAPA 4: ANÁLISE DE ESTOQUE - ALERTAS
# ============================================================
print("📦 [ETAPA 4/5] ANÁLISE DE ESTOQUE E ALERTAS...")
print("-" * 70)

# Estoque total
estoque_total = df_estoque['Quantidade Disponível'].sum()
print(f"\n📊 VISÃO GERAL DO ESTOQUE:")
print(f"   • Estoque Total: {estoque_total:,} unidades")
print(f"   • Produtos em estoque: {df_estoque['Código Produto'].nunique()}")
print(f"   • Filiais: {df_estoque['Filial'].nunique()}")

# Análise por status
status_counts = df_estoque['Status Estoque'].value_counts()
print(f"\n⚠️  STATUS DO ESTOQUE:")
for status in ['CRÍTICO', 'BAIXO', 'NORMAL']:
    if status in status_counts.index:
        qtd = status_counts[status]
        perc = (qtd / len(df_estoque) * 100)
        emoji = '🔴' if status == 'CRÍTICO' else '🟡' if status == 'BAIXO' else '🟢'
        print(f"   {emoji} {status}: {qtd} itens ({perc:.1f}%)")

# Produtos em situação crítica
criticos = df_estoque[df_estoque['Status Estoque'] == 'CRÍTICO'].sort_values('% do Mínimo')

if len(criticos) > 0:
    print(f"\n🚨 ALERTA: {len(criticos)} PRODUTOS EM SITUAÇÃO CRÍTICA:")
    for _, item in criticos.head(10).iterrows():
        print(f"   • {item['Produto'][:45]}...")
        print(f"     Filial: {item['Filial']} | Estoque: {int(item['Quantidade Disponível'])} | Mínimo: {int(item['Estoque Mínimo'])} | {item['% do Mínimo']:.0f}% do mínimo")

# Produtos com estoque baixo
baixos = df_estoque[df_estoque['Status Estoque'] == 'BAIXO'].sort_values('% do Mínimo')

if len(baixos) > 0:
    print(f"\n⚡ ATENÇÃO: {len(baixos)} PRODUTOS COM ESTOQUE BAIXO:")
    for _, item in baixos.head(5).iterrows():
        print(f"   • {item['Produto'][:45]}...")
        print(f"     Filial: {item['Filial']} | Estoque: {int(item['Quantidade Disponível'])} | Mínimo: {int(item['Estoque Mínimo'])}")

# Estoque por filial
print(f"\n🏪 ESTOQUE POR FILIAL:")
estoque_filial = df_estoque.groupby('Filial').agg({
    'Quantidade Disponível': 'sum',
    'Código Produto': 'count'
})
estoque_filial.columns = ['Total_Unidades', 'SKUs']

for filial in estoque_filial.index:
    total = int(estoque_filial.loc[filial, 'Total_Unidades'])
    skus = int(estoque_filial.loc[filial, 'SKUs'])
    alertas = len(df_estoque[(df_estoque['Filial'] == filial) & (df_estoque['Status Estoque'].isin(['CRÍTICO', 'BAIXO']))])
    print(f"   • {filial}: {total:,} unidades | {skus} SKUs | {alertas} alertas")

print("\n Análise de estoque concluída!\n")

# ============================================================
# ETAPA 5: INSIGHTS E RECOMENDAÇÕES
# ============================================================
print(" [ETAPA 5/5] GERANDO INSIGHTS E RECOMENDAÇÕES...")
print("-" * 70)

print("\n INSIGHTS ESTRATÉGICOS:\n")

# Insight 1: Filial com melhor performance
melhor_filial = vendas_filial.index[0]
print(f" FILIAL DESTAQUE: {melhor_filial}")
print(f"    → Responsável por {vendas_filial.loc[melhor_filial, '% do Total']:.1f}% do faturamento total")
print(f"    → Ticket médio de R$ {vendas_filial.loc[melhor_filial, 'Ticket_Medio']:.2f}")

# Insight 2: Categoria mais lucrativa
melhor_categoria = vendas_categoria.index[0]
print(f"\n CATEGORIA LÍDER: {melhor_categoria}")
print(f"    → {vendas_categoria.loc[melhor_categoria, '% Faturamento']:.1f}% do faturamento")
print(f"    → {int(vendas_categoria.loc[melhor_categoria, 'Unidades'])} unidades vendidas")

# Insight 3: Produto mais vendido
produto_top = top_produtos.index[0]
print(f"\n PRODUTO CAMPEÃO: {produto_top[1][:50]}")
print(f"    → Receita: R$ {top_produtos.loc[produto_top, 'Receita']:,.2f}")
print(f"    → {int(top_produtos.loc[produto_top, 'Unidades'])} unidades vendidas")

# Insight 4: Taxa de crescimento
crescimento = ((vendas_mes.loc[6, 'Valor Total'] - vendas_mes.loc[1, 'Valor Total']) / vendas_mes.loc[1, 'Valor Total'] * 100)
print(f"\n CRESCIMENTO: {crescimento:+.1f}% (Jan vs Jun)")
if crescimento > 0:
    print(f"    → Tendência positiva de crescimento")
else:
    print(f"    → Necessário revisar estratégia comercial")

# Insight 5: Gestão de estoque
total_alertas = len(criticos) + len(baixos)
print(f"\n GESTÃO DE ESTOQUE: {total_alertas} produtos precisam de reposição urgente")
print(f"    → {len(criticos)} em estado crítico")
print(f"    → {len(baixos)} com estoque baixo")

print("\n RECOMENDAÇÕES:\n")
print("   ✓ Priorizar reposição dos produtos em situação crítica")
print("   ✓ Replicar estratégias da filial líder para outras unidades")
print("   ✓ Investir em marketing para categorias de alta margem")
print("   ✓ Analisar sazonalidade para melhor gestão de compras")
print("   ✓ Implementar promoções estratégicas nos produtos com estoque alto")

print("\n" + "=" * 70)
print("ANÁLISE COMPLETA FINALIZADA COM SUCESSO!")
print("=" * 70)
print(f"\nPróximo passo: Execute 'gerar_relatorios.py' para criar relatórios Excel")
print("=" * 70 + "\n")