import pandas as pd # pyright: ignore[reportMissingModuleSource]
import os

# Pastas
DATA_DIR = "data"
REPORT_DIR = "reports"


# Garantir que a pasta de reports exista
os.makedirs(REPORT_DIR, exist_ok=True)

# --- 1. Carregar CSVs ---
alunos = pd.read_csv(os.path.join(DATA_DIR, "alunos.csv"))
disciplinas = pd.read_csv(os.path.join(DATA_DIR, "disciplinas.csv"))
notas = pd.read_csv(os.path.join(DATA_DIR, "notas.csv"))
presenca = pd.read_csv(os.path.join(DATA_DIR, "presenca.csv"))

# --- 2. ETL ALUNOS ---
# Remover duplicatas
alunos_duplicatas = alunos.duplicated().sum()
alunos.drop_duplicates(inplace=True)
# Preencher nulos
alunos.fillna("Desconhecido", inplace=True)

# --- 3. ETL DISCIPLINAS ---
disciplinas_duplicatas = disciplinas.duplicated().sum()
disciplinas.drop_duplicates(inplace=True)
disciplinas.fillna("Desconhecido", inplace=True)

# --- 4. ETL NOTAS ---
notas_duplicatas = notas.duplicated().sum()
notas.drop_duplicates(inplace=True)
notas.fillna(0, inplace=True)  # notas nulas viram 0
notas['nota'] = notas['nota'].astype(float)

# --- 5. ETL PRESENCA ---
presenca_duplicatas = presenca.duplicated().sum()
presenca.drop_duplicates(inplace=True)
presenca.fillna(0, inplace=True)
presenca['total_aulas'] = presenca['total_aulas'].astype(int)
presenca['aulas_presencas'] = presenca['aulas_presencas'].astype(int)

# --- 6. Salvar CSVs tratados ---
alunos.to_csv(os.path.join(DATA_DIR, "alunos_tratados.csv"), index=False)
disciplinas.to_csv(os.path.join(DATA_DIR, "disciplinas_tratadas.csv"), index=False)
notas.to_csv(os.path.join(DATA_DIR, "notas_tratadas.csv"), index=False)
presenca.to_csv(os.path.join(DATA_DIR, "presenca_tratada.csv"), index=False)

# --- 7. Relatório de tratamento ---
relatorio = {
    "arquivo": ["alunos", "disciplinas", "notas", "presenca"],
    "duplicatas_removidas": [alunos_duplicatas, disciplinas_duplicatas, notas_duplicatas, presenca_duplicatas],
    "valores_nulos_tratados": [
        alunos.isna().sum().sum(),
        disciplinas.isna().sum().sum(),
        notas.isna().sum().sum(),
        presenca.isna().sum().sum()
    ],
    "registros_final": [len(alunos), len(disciplinas), len(notas), len(presenca)]
}

relatorio_df = pd.DataFrame(relatorio)
relatorio_df.to_csv(os.path.join(REPORT_DIR, "relatorio_tratamento.csv"), index=False)

print("ETL concluído! CSVs tratados e relatório gerado em 'reports/relatorio_tratamento.csv'.")
