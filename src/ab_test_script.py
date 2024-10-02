import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from scipy.stats import chi2_contingency
from scipy.stats import f_oneway
from statsmodels.stats.proportion import proportions_ztest
from scipy.stats import ttest_ind, mannwhitneyu


# Function to load data
def load_data():
    df_demo = pd.read_csv('../data/raw/df_final_demo.txt', delimiter=',')
    df_web_pt1 = pd.read_csv('../data/raw/df_final_web_data_pt_1.txt', delimiter=',')
    df_web_pt2 = pd.read_csv('../data/raw/df_final_web_data_pt_2.txt', delimiter=',')
    df_experiment = pd.read_csv('../data/raw/df_final_experiment_clients.txt', delimiter=',')
    return df_demo, df_web_pt1, df_web_pt2, df_experiment

# Function to clean and process demographic data
def clean_demo_data(df_demo):
    df_demo = df_demo.dropna(how='all', subset=df_demo.columns.difference(['client_id']))
    df_demo['clnt_age'].fillna(round(df_demo['clnt_age'].mean()), inplace=True)
    df_demo['gendr'].replace('X', 'U', inplace=True)
    return df_demo

# Function to merge web data
def merge_web_data(df_web_pt1, df_web_pt2):
    df_web_combined = pd.concat([df_web_pt1, df_web_pt2], axis=0, ignore_index=True)
    return df_web_combined

# Exploración de los datos web 
def clean_web_data(df_web_combined):
    df_web_combined['date_time'] = pd.to_datetime(df_web_combined['date_time'], format='%Y-%m-%d %H:%M:%S')
    df_web_combined.drop_duplicates(inplace=True)
    df_web_combined["process_step"] = df_web_combined["process_step"].replace({'start' : 1, 'step_1' : 2, 'step_2' : 3, 'step_3' : 4, 'confirm' : 5})
    web_data_final = df_web_combined.sort_values(by=['client_id', 'visit_id', 'date_time'])
    return web_data_final

# Function to calculate time per step
def calculate_time_per_step(web_data_final):
    
    web_data_final['next_date_time'] = web_data_final.groupby(['client_id', 'visit_id'])['date_time'].shift(-1)
    web_data_final['time_diff_seconds'] = (web_data_final['next_date_time'] - web_data_final['date_time']).dt.total_seconds()
    return web_data_final


# Exploración de los datos experiment
def clean_experiment_data(df_experiment):
    df_experiment.dropna(inplace=True)
    return df_experiment

# Function to merge all datasets
def merge_all_data(df_demo, web_data_final, df_experiment):
    df_combined = pd.merge(df_demo, df_experiment, on='client_id', how='left')
    df_combined = df_combined.dropna()
    df_merged = pd.merge(web_data_final, df_experiment, on='client_id', how='inner')
    df_merged = df_merged.sort_values(by=['client_id', 'visit_id', 'date_time'])
    return df_combined, df_merged

# Function to create time summary per client step
def summarize_time_per_client_step(df_merged):
    time_per_client_step = df_merged.groupby(['client_id', 'process_step', 'Variation'])['time_diff_seconds'].sum().reset_index()
    return time_per_client_step

def summarize_success(df_merged):
    success_summary = df_merged.groupby('client_id')['process_step'].max().reset_index()
    success_summary['success'] = success_summary['process_step'] == 5
    return success_summary


def summarize_time_by_client(df_merged):
    time_by_client = df_merged.groupby('client_id')['time_diff_seconds'].sum().reset_index()
    return time_by_client


def summarize_error(df_merged):
    df_merged['previous_step'] = df_merged.groupby(['client_id', 'visit_id'])['process_step'].shift(1)
    df_merged['error'] = df_merged['process_step'] < df_merged['previous_step']  # True si hay un regreso
    error_count_summary = df_merged.groupby('client_id')['error'].sum().reset_index()
    error_count_summary.columns = ['client_id', 'error_count']
    error_summary = df_merged.groupby(['client_id', 'Variation'])['error'].any().reset_index()
    return error_summary, error_count_summary

def create_data_summary(success_summary, time_by_client, error_summary, error_count_summary):
    error_summary = pd.merge(error_summary, error_count_summary, on='client_id', how='left')
    data_summary = pd.merge(success_summary, time_by_client, on='client_id', how='outer').merge(error_summary, on='client_id', how='outer')
    data_summary = data_summary[['client_id', 'process_step', 'success', 'time_diff_seconds', 'error', 'error_count', 'Variation']]
    return data_summary

def remove_outliers_iqr(df, column, group_column=None):
    """
    Esta función elimina los valores atípicos de un DataFrame utilizando el rango intercuartil (IQR).
    Si se proporciona una columna de agrupación, el IQR se calculará por cada grupo.
    
    Parámetros:
    - df: pd.DataFrame. El DataFrame del cual eliminar los valores atípicos.
    - column: str. El nombre de la columna en la cual calcular y eliminar los outliers.
    - group_column: str, opcional. El nombre de la columna utilizada para agrupar los datos (por defecto None).
    
    Retorno:
    - pd.DataFrame. El DataFrame sin los valores atípicos.
    """
    if group_column:
        clean_df = pd.DataFrame()
        for group in df[group_column].unique():
            # Filtrar por el grupo
            group_data = df[df[group_column] == group]

            # Calcular Q1 (primer cuartil) y Q3 (tercer cuartil) para el grupo
            Q1 = group_data[column].quantile(0.25)
            Q3 = group_data[column].quantile(0.75)
            IQR = Q3 - Q1

            # Definir los límites para no ser considerado un outlier
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # Filtrar los datos que no son outliers
            group_clean_data = group_data[(group_data[column] >= lower_bound) & (group_data[column] <= upper_bound)]
            clean_df = pd.concat([clean_df, group_clean_data], ignore_index=True)
        return clean_df
    else:
        # Calcular Q1 y Q3 para la columna sin agrupamiento
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1

        # Definir los límites para no ser considerado un outlier
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Filtrar los datos que no son outliers
        return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

# Function to save DataFrames to CSV
def save_dataframes(df_merged, data_summary, time_per_client_step, df_combined):
    df_merged.to_csv('../data/cleaned/data_web_final.csv', index=False)
    data_summary.to_csv('../data/cleaned/data_summary.csv', index=False)
    time_per_client_step.to_csv('../data/cleaned/data_time_per_client_step.csv', index=False)
    df_combined.to_csv('../data/cleaned/data_demo_final.csv', index=False)

def main():
    # Cargar los datos
    df_demo, df_web_pt1, df_web_pt2, df_experiment = load_data()

    # Limpiar y procesar los datos demográficos
    df_demo_cleaned = clean_demo_data(df_demo)

    # Combinar los datos web de las dos partes
    df_web_combined = merge_web_data(df_web_pt1, df_web_pt2)

    # Limpiar y procesar los datos web
    df_web_cleaned = clean_web_data(df_web_combined)

    # Calcular el tiempo transcurrido entre cada paso del proceso
    web_data_final = calculate_time_per_step(df_web_cleaned)

    # Limpiar y procesar los datos experimentales
    df_experiment_cleaned = clean_experiment_data(df_experiment)

    # Union de todos los DataFrames
    df_combined, df_merged = merge_all_data(df_demo_cleaned, web_data_final, df_experiment_cleaned)

    # Crear resúmenes de los datos
    time_per_client_step = summarize_time_per_client_step(df_merged)
    success_summary = summarize_success(df_merged)
    time_by_client = summarize_time_by_client(df_merged)
    error_summary, error_count_summary = summarize_error(df_merged)
    data_summary = create_data_summary(success_summary, time_by_client, error_summary, error_count_summary)

    # Eliminar valores atípicos
    data_summary = remove_outliers_iqr(data_summary, 'time_diff_seconds')
    time_per_client_step = remove_outliers_iqr(time_per_client_step, 'time_diff_seconds', 'process_step')
  
    # Guardar los DataFrames limpios y resúmenes en archivos CSV
    save_dataframes(df_merged, data_summary, time_per_client_step, df_combined)