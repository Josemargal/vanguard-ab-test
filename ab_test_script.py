import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from scipy.stats import chi2_contingency
from scipy.stats import f_oneway
from statsmodels.stats.proportion import proportions_ztest
from scipy.stats import ttest_ind, mannwhitneyu


# Cargar los datasets
df_demo = pd.read_csv('df_final_demo.txt', delimiter=',')  # Usa el delimitador adecuado
df_web_pt1 = pd.read_csv('df_final_web_data_pt_1.txt', delimiter=',')
df_web_pt2 = pd.read_csv('df_final_web_data_pt_2.txt', delimiter=',')
df_experiment = pd.read_csv('df_final_experiment_clients.txt', delimiter=',')

# Eliminar filas con valores nulos
df_demo = df_demo.dropna(how='all', subset=df_demo.columns.difference(['client_id']))

# Sustituir los valores nulos en 'clnt_age' por la media calculada
df_demo['clnt_age'].fillna(df_demo['clnt_age'].mean(), inplace=True)

# Reemplazar los valores 'X' por 'U'
df_demo['gendr'] = df_demo['gendr'].replace('X', 'U')

# Exploración de los datos web 
# Unir los datasets pt_1 y pt_2
df_web_combined = pd.concat([df_web_pt1, df_web_pt2], axis=0, ignore_index=True)

# Convertir la columna 'date_time' a datetime
df_web_combined['date_time'] = pd.to_datetime(df_web_combined['date_time'], format='%Y-%m-%d %H:%M:%S')

# Eliminar duplicados
df_web_combined.drop_duplicates(inplace=True)

# Renombrar los pasos a un formato numerico: 'start' por 1, 'step_1' por 2, 'step_2' por 3, 'step_3' por 4, 'confirm' por 5
df_web_combined["process_step"] = df_web_combined["process_step"].replace({'start' : 1, 'step_1' : 2, 'step_2' : 3, 'step_3' : 4, 'confirm' : 5})

# Ordenar los datos por client_id, visit_id y date_time
web_data_final = df_web_combined.sort_values(by=['client_id', 'visit_id', 'date_time'])

# Añadir la hora del paso posterior
web_data_final['next_date_time'] = web_data_final.groupby(['client_id', 'visit_id'])['date_time'].shift(-1)

# Calcular la diferencia de tiempo entre el paso actual y el siguiente
web_data_final['time_diff'] = web_data_final['next_date_time'] - web_data_final['date_time']

# Convertir la diferencia de tiempo a segundos
web_data_final['time_diff_seconds'] = web_data_final['time_diff'].dt.total_seconds()

# Exploración de los datos experiment
# Eliminamos valores nulos
df_experiment.dropna(inplace=True)

# Unir los DataFrames por 'client_id'
df_merged = pd.merge(web_data_final, df_experiment, on='client_id', how='inner')

# Ordenar los datos por 'client_id', 'visit_id', 'date_time'
df_merged = df_merged.sort_values(by=['client_id', 'visit_id', 'date_time'])

# Determinar si el cliente llegó al paso 5
success_summary = df_merged.groupby('client_id')['process_step'].max().reset_index()

# Añadir una columna que indique si tuvo éxito (si el paso 5 está presente)
success_summary['success'] = success_summary['process_step'] == 5

# Calcular la media de 'time_diff_seconds' para cada 'process_step'
time_diff_sum = df_merged.groupby(['Variation', 'process_step'])['time_diff_seconds'].mean().reset_index()


time_per_client_step = df_merged.groupby(['client_id', 'process_step', 'Variation'])['time_diff_seconds'].sum().reset_index()


time_by_client = df_merged.groupby('client_id')['time_diff_seconds'].sum().reset_index()


# KPI 3: Tasa de error
df_merged['previous_step'] = df_merged.groupby(['client_id', 'visit_id', 'date_time'])['process_step'].shift(1)
df_merged['error'] = df_merged['process_step'] < df_merged['previous_step']  # True si hay un regreso


# Agrupar por client_id para contar la cantidad de errores
error_count_summary = df_merged.groupby('client_id')['error'].sum().reset_index()
error_count_summary.columns = ['client_id', 'error_count']


# Agrupar por client_id para contar la cantidad de errores por cliente y lo unimos con el summary
error_summary = df_merged.groupby(['client_id', 'Variation'])['error'].any().reset_index()
error_summary = pd.merge(error_summary, error_count_summary, on='client_id', how='left')


# Unimos los errores con la tasa de exito por cliente
data_summary = pd.merge(success_summary, time_by_client, on='client_id', how='outer').merge(error_summary, on='client_id', how='outer')


# Ordenamos columnas de data_summary
data_summary = data_summary[['client_id', 'process_step', 'success', 'time_diff_seconds', 'error', 'error_count', 'Variation']]

Q1 = data_summary['time_diff_seconds'].quantile(0.25)
Q3 = data_summary['time_diff_seconds'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
data_summary = data_summary[(data_summary['time_diff_seconds'] >= lower_bound) & (data_summary['time_diff_seconds'] <= upper_bound)]

# Función para quitar outliers usando el método IQR
def remove_outliers_iqr(df, column, group_column):
    clean_df = pd.DataFrame()
    for step in df[group_column].unique():
        # Filtrar por el paso
        step_data = df[df[group_column] == step]
        
        # Calcular Q1 (primer cuartil) y Q3 (tercer cuartil)
        Q1 = step_data[column].quantile(0.25)
        Q3 = step_data[column].quantile(0.75)
        IQR = Q3 - Q1
        
        # Definir los límites para no ser considerado un outlier
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Filtrar los datos que no son outliers
        step_clean_data = step_data[(step_data[column] >= lower_bound) & (step_data[column] <= upper_bound)]
        clean_df = pd.concat([clean_df, step_clean_data], ignore_index=True)
    
    return clean_df



# Aplicar la función para eliminar outliers en 'time_diff_seconds' por 'process_step'
time_per_client_step = remove_outliers_iqr(time_per_client_step, 'time_diff_seconds', 'process_step')


# Juntamos df_demo y df_experiment por client_id
df_combined = pd.merge(df_demo, df_experiment, on='client_id', how='left')


# Eliminar valores nulos
df_combined = df_combined.dropna()

df_merged
data_summary
time_per_client_step
df_combined

# Guardar df_merged en un archivo CSV
df_merged.to_csv('/data_web_final.csv', index=False)

# Guardar data_summary en un archivo CSV
data_summary.to_csv('/data_summary.csv', index=False)

# Guardar time_per_client_step en un archivo CSV
time_per_client_step.to_csv('/data_time_per_client_step.csv', index=False)

# Guardar df_combined en un archivo CSV
df_combined.to_csv('/data_demo_final.csv', index=False)