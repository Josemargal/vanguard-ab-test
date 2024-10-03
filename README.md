# Vanguard A/B Test Project

## Descripción del Proyecto

Este proyecto consiste en el análisis de un experimento A/B realizado por Vanguard, una empresa de gestión de inversiones con sede en EE.UU. El objetivo del experimento fue evaluar si un nuevo diseño de interfaz de usuario (UI), que incluye una interfaz más moderna e intuitiva, junto con mensajes y sugerencias contextuales, mejora la experiencia de los clientes y conduce a una mayor tasa de finalización del proceso en la plataforma.

El proyecto utiliza múltiples etapas de procesamiento de datos, análisis estadístico, y visualización de los resultados. Se desarrolló un script modularizado para generar datos limpios, que posteriormente fueron importados a **Tableau** para crear visualizaciones interactivas y presentar los resultados.

## Estructura del Repositorio

- **ab_test_script.py**: Archivo con el código que incluye todo el procesamiento de datos necesario para generar los DataFrames finales.
- **Notebook (data_exploration.ipynb)**: Notebook con análisis exploratorio, visualización de los datos y pruebas de hipótesis.
- **Archivos CSV**: Datos limpios generados por el script (`data_web_final.csv`, `data_summary.csv`, `time_per_client_step.csv`, `data_demo_final.csv`).
- **Tableau File (experiment_dashboard.twbx)**: Visualización interactiva del análisis en Tableau.
- **README.md**: Documento con la descripción del proyecto, pasos para ejecución y enlaces relevantes.

## Datos

### Fuentes de Datos
El proyecto utilizó las siguientes fuentes de datos:
1. **Client Profiles (`df_final_demo.txt`)**: Información demográfica de los clientes.
2. **Digital Footprints (`df_final_web_data_pt_1.txt` y `df_final_web_data_pt_2.txt`)**: Información detallada sobre la interacción de los clientes en la web.
3. **Experiment Roster (`df_final_experiment_clients.txt`)**: Lista de clientes que participaron en el experimento A/B.

Estos datos fueron procesados y combinados para realizar el análisis.

## Análisis y KPIs

### KPIs definidos
Los **KPIs** evaluados durante el análisis fueron:
1. **Tasa de Finalización**: Porcentaje de usuarios que completaron todo el proceso.
2. **Tiempo en Cada Paso**: Duración promedio que cada cliente pasó en cada paso del proceso.
3. **Tasa de Error**: Número de veces que los usuarios regresaron a un paso anterior, indicando potenciales dificultades.

### Análisis Estadístico
Se realizaron las siguientes pruebas estadísticas:
- **Pruebas t de Student**: Comparar tiempos y métricas entre los grupos de control y prueba.
- **Pruebas Chi-cuadrado**: Evaluar la independencia entre variables categóricas.
- **Prueba Z**: Comparación de medias o proporciones entre los grupos de control y prueba.

## Visualización en Tableau

Los datos procesados fueron importados a **Tableau** para crear un **dashboard interactivo** que muestra los resultados del experimento A/B:
- **Tasas de finalización** por grupo (Control vs. Test).
- **Tiempo promedio** en cada paso, comparando ambos grupos.
- **Tasa de error** para identificar posibles cuellos de botella.
- **Análisis demográfico**: Exploración de los resultados según la edad y el género de los clientes.

El archivo de Tableau (`vanguard-ab-test.twbx`) está incluido en este repositorio para su revisión.


## Requisitos
- **Python 3.9** y las siguientes bibliotecas:
  - `pandas`
  - `seaborn`
  - `matplotlib`
  - `scipy`
  - `statsmodels`
- **Tableau** para visualizar los resultados interactivos.



 
