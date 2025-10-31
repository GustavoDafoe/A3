import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
from sklearn.cluster import KMeans # type: ignore

# --- 1. Carregar CSVs tratados ---
DATA_DIR = "data"

alunos = pd.read_csv(f"{DATA_DIR}/alunos_tratados.csv")
disciplinas = pd.read_csv(f"{DATA_DIR}/disciplinas_tratadas.csv")
notas = pd.read_csv(f"{DATA_DIR}/notas_tratadas.csv")
presenca = pd.read_csv(f"{DATA_DIR}/presenca_tratada.csv")

# --- 2. Configurações da página ---
st.set_page_config(page_title="Dashboard Escolar", layout="wide")
st.title("Dashboard Escolar - Notas e Presença")

# --- 3. Filtros ---
turma_selecionada = st.selectbox("Selecione a Turma", alunos['turma'].unique())
alunos_turma = alunos[alunos['turma'] == turma_selecionada]

disciplina_selecionada = st.selectbox("Selecione a Disciplina", disciplinas['nome'].unique())
disciplina_id = disciplinas[disciplinas['nome'] == disciplina_selecionada]['id'].values[0]

# --- 4. Filtrar notas e presença ---
notas_filtradas = notas[(notas['aluno_id'].isin(alunos_turma['id'])) & (notas['disciplina_id'] == disciplina_id)]
presenca_filtrada = presenca[(presenca['aluno_id'].isin(alunos_turma['id'])) & (presenca['disciplina_id'] == disciplina_id)]

# Juntar com nomes dos alunos
notas_filtradas = notas_filtradas.merge(alunos_turma, left_on='aluno_id', right_on='id')
presenca_filtrada = presenca_filtrada.merge(alunos_turma, left_on='aluno_id', right_on='id')

# --- 5. Gráfico de Notas ---
fig_notas = px.bar(
    notas_filtradas,
    x='nome',
    y='nota',
    title=f"Notas da disciplina {disciplina_selecionada} - Turma {turma_selecionada}",
    labels={'nota':'Nota', 'nome':'Aluno'}
)
st.plotly_chart(fig_notas, use_container_width=True)

# --- 6. Gráfico de Presença ---
presenca_filtrada['percentual_presenca'] = presenca_filtrada['aulas_presencas'] / presenca_filtrada['total_aulas'] * 100
fig_presenca = px.bar(
    presenca_filtrada,
    x='nome',
    y='percentual_presenca',
    title=f"Percentual de Presença - Disciplina {disciplina_selecionada} - Turma {turma_selecionada}",
    labels={'percentual_presenca':'% Presença', 'nome':'Aluno'}
)
st.plotly_chart(fig_presenca, use_container_width=True)

# --- 7. Clustering alunos por Nota x Presença ---
df_cluster = notas_filtradas[['aluno_id','nota']].merge(
    presenca_filtrada[['aluno_id','percentual_presenca']], on='aluno_id'
)
X = df_cluster[['nota','percentual_presenca']]

# Ajusta n_clusters para no máximo o número de alunos
n_clusters = min(3, len(X))
if n_clusters > 0:
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df_cluster['cluster'] = kmeans.fit_predict(X)  # agora adiciona direto no df_cluster

    df_cluster = df_cluster.merge(alunos_turma, left_on='aluno_id', right_on='id')
    fig_cluster = px.scatter(
        df_cluster,
        x='nota',
        y='percentual_presenca',
        color='cluster',  # Plotly agora encontra a coluna
        hover_data=['nome'],
        title=f"Clustering de Alunos - Turma {turma_selecionada} (Nota x Presença)"
    )
    st.plotly_chart(fig_cluster, use_container_width=True)
else:
    st.write("Não há dados suficientes para realizar clustering.")

# --- 8. Estatísticas rápidas ---
st.subheader("Estatísticas Rápidas")
st.write(f"Nota média da disciplina: {notas_filtradas['nota'].mean():.2f}")
st.write(f"Presença média da disciplina: {presenca_filtrada['percentual_presenca'].mean():.2f}%")
st.write(f"Número de alunos na turma: {len(alunos_turma)}")
