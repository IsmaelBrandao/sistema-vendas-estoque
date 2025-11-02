# 📊 Sistema de Análise de Vendas e Estoque

Sistema de Business Intelligence desenvolvido para análise de dados de vendas e gestão de estoque em ambiente multi-filial, com foco em automação de processos e visualização de KPIs estratégicos.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.1.0-green.svg)](https://pandas.pydata.org/)
[![Dashboard](https://img.shields.io/badge/Dashboard-Online-brightgreen)](https://ismaelbrandao.github.io/sistema-vendas-estoque)

[🚀 Ver Dashboard Online](https://ismaelbrandao.github.io/sistema-vendas-estoque)

---

## 🎯 Objetivo do Projeto

Desenvolver uma solução completa de análise de dados que simula o ambiente de uma empresa real com múltiplas filiais, abrangendo desde a extração e tratamento de dados até a geração de insights acionáveis através de dashboards interativos e relatórios automatizados.

O sistema foi projetado para resolver problemas reais de gestão empresarial: identificar produtos com baixo giro de estoque, analisar performance de vendas por região, calcular rentabilidade por categoria e automatizar a geração de relatórios gerenciais.

### Funcionalidades Principais

**Análise de Dados**
- Processamento de vendas de 6 meses (1.800+ transações)
- Análise de performance por filial e categoria
- Identificação de produtos mais vendidos
- Cálculo de métricas de lucratividade

**Gestão de Estoque**
- Monitoramento de estoque em 4 filiais
- Alertas automáticos de reposição
- Classificação por nível crítico
- Controle de estoque mínimo

**Dashboard Interativo**
- Visualizações com gráficos dinâmicos
- Filtros por filial com atualização em tempo real
- Interface responsiva
- Atualização automática dos dados

**Relatórios Automatizados**
- Relatório de vendas por produto
- Relatório de performance por filial
- Relatório de estoque crítico
- Evolução mensal de vendas

---

## 🧠 Lógica e Arquitetura

### Pipeline de Dados (ETL)

O sistema segue uma arquitetura de pipeline de dados em três camadas:

**1. Extract (Extração)**
- Leitura de múltiplas planilhas Excel de diferentes fontes (ERP, WMS, PDV)
- Validação de integridade dos dados na origem
- Tratamento de encodings e formatações inconsistentes

**2. Transform (Transformação)**
- Limpeza de dados sujos (valores nulos, duplicatas, outliers)
- Normalização de campos de texto e datas
- Cálculos de métricas derivadas (margem de lucro, ticket médio, ROI)
- Enriquecimento de dados através de joins entre datasets
- Agregações temporais (diária, semanal, mensal)
- Classificação de criticidade de estoque

**3. Load (Carga)**
- Exportação para múltiplos formatos (Excel, CSV, JSON)
- Serialização otimizada para consumo do dashboard
- Versionamento de datasets processados

### Módulos Principais

**`processar_dados.py`** - Motor ETL
- Implementa pipeline completo de transformação
- Valida consistência entre produtos, vendas e estoque
- Calcula métricas agregadas por dimensões de análise
- Identifica padrões e anomalias estatísticas

**`analise_vendas.py`** - Análise Exploratória
- Cálculo de KPIs de negócio (faturamento, conversão, churn)
- Análise de sazonalidade e tendências temporais
- Segmentação por filial, categoria e período
- Geração de insights e recomendações estratégicas

**`gerar_relatorios.py`** - Automação de Relatórios
- Geração programática de relatórios Excel formatados
- Criação de múltiplas abas com diferentes visões
- Aplicação de regras de negócio para classificação
- Export pronto para distribuição gerencial

**`exportar_dashboard_data.py`** - Serialização para Web
- Conversão de DataFrames para formato consumível via JavaScript
- Otimização de payload (JSON para métricas, CSV para séries)
- Cálculo de agregações específicas para visualizações

---

## 🛠️ Stack Tecnológico

### Backend (Python)

**Pandas** - Manipulação e análise de dados
- DataFrames para operações vetorizadas eficientes
- GroupBy para agregações multidimensionais
- Merge/Join para relacionamento entre datasets
- Métodos de limpeza e transformação de dados

**NumPy** - Computação numérica
- Arrays para cálculos matemáticos otimizados
- Operações estatísticas (média, desvio padrão, quartis)
- Detecção de outliers usando IQR

**OpenPyXL** - Processamento de Excel
- Leitura de arquivos XLSX com múltiplas abas
- Escrita com formatação condicional
- Preservação de fórmulas nativas do Excel

### Frontend (Dashboard)

**HTML5/CSS3** - Estrutura e estilo
- Semantic HTML para acessibilidade
- CSS Grid e Flexbox para layout responsivo
- CSS Variables para tematização
- Animações e transições para melhor UX

**JavaScript (ES6+)** - Lógica de aplicação
- Fetch API para carregamento assíncrono de dados
- Promises para gerenciamento de requisições
- Manipulação dinâmica do DOM
- Event handlers para interatividade

**Chart.js** - Visualizações de dados
- Gráficos de linha para séries temporais
- Gráficos de barra para comparações
- Gráficos de pizza para distribuições percentuais
- Configuração de tooltips, legendas e escalas

**PapaParse** - Parser de CSV
- Leitura assíncrona de arquivos CSV
- Conversão automática de tipos de dados
- Tratamento de delimitadores e encodings

---

## 📊 Visualizações e KPIs

### Métricas Calculadas

**Faturamento Total**
```python
faturamento = df['Valor Total'].sum()
```

**Ticket Médio**
```python
ticket_medio = df['Valor Total'].mean()
```

**Taxa de Conversão** (estimada com base em visitas)
```python
conversao = (vendas_concluidas / total_visitas) * 100
```

**Margem de Lucro**
```python
margem = ((preco_venda - custo) / preco_venda) * 100
```

**Giro de Estoque**
```python
giro = unidades_vendidas / estoque_medio
```

### Gráficos Implementados

**Evolução Mensal (Line Chart)**
- Série temporal de faturamento
- Identificação de tendências e sazonalidade
- Baseline para comparação YoY

**Performance por Filial (Bar Chart)**
- Comparação de faturamento entre regiões
- Ranking de performance
- Identificação de filiais com potencial de crescimento

**Distribuição por Categoria (Doughnut Chart)**
- Percentual de participação de cada categoria
- Análise de mix de produtos
- Identificação de categorias core

**Top Produtos (Horizontal Bar Chart)**
- Ranking de produtos por receita
- Curva ABC (Pareto)
- Produtos estratégicos para estoque

---

## 🎨 Features do Dashboard

### Interatividade
- Filtros dinâmicos por filial com atualização em tempo real
- Tooltips informativos em todos os gráficos
- Hover effects para melhor experiência visual
- Tabela de alertas com classificação por criticidade

### Responsividade
- Layout adaptativo para desktop, tablet e mobile
- Grid system com breakpoints customizados
- Imagens e gráficos escaláveis

### Performance
- Carregamento assíncrono de dados
- Lazy loading de visualizações
- Caching de requisições bem-sucedidas
- Feedback visual durante processamento

---

## 💡 Insights Gerados

O sistema identifica automaticamente:

- Produtos com estoque abaixo do nível crítico que precisam de reposição urgente
- Filiais com performance acima/abaixo da média para replicação de boas práticas
- Categorias de produtos com maior margem de contribuição
- Tendências de crescimento ou queda nas vendas
- Oportunidades de cross-selling baseadas em correlação de vendas
- Sazonalidades que impactam planejamento de compras

---

## 🎓 Competências Demonstradas

- Pipeline ETL completo com Python
- Análise exploratória e estatística de dados
- Automação de processos e relatórios
- Visualização de dados e storytelling
- Desenvolvimento web (HTML/CSS/JavaScript)
- Integração frontend-backend via APIs REST simuladas
- Versionamento de código com Git
- Documentação técnica

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um Fork do projeto
2. Criar uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abrir um Pull Request

---

## 📬 Contato

**Ismael Brandão**

[![LinkedIn](https://img.shields.io/badge/-LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ismael-brandao-906167300)
[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github)](https://github.com/IsmaelBrandao)
[![Email](https://img.shields.io/badge/-Email-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:ismaelbrandao334@gmail.com)

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">

**[⭐ Star este projeto](https://github.com/IsmaelBrandao/sistema-vendas-estoque)** se ele foi útil para você!

Desenvolvido com 💜 por Ismael Brandão

</div>
