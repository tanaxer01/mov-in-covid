import pandas as pd
import os
import requests
from unidecode import unidecode

def download_data():
    datasets = {
      # DP1
      "dp1_contagios": "https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto1/Covid-19_std.csv",
      # DP7
      "dp7_pcr": "https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto7/PCR_std.csv",
      # DP20
      "dp20_camas": "https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto20/NumeroVentiladores_std.csv",
      # DP51
      "dp51_difs": "https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto51/ISCI_std.csv",
      # DP82
      "dp82_weeks": "https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto82/ISCI_weeks.csv",
      "dp82_weekends": "https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto82/ISCI_weekends.csv",
    }

    if not os.path.exists("./datos"):
        os.mkdir('./datos')

    for name, url in datasets.items():
        if not os.path.exists(f'./datos/{name}.csv'):
            with open(f'./datos/{name}.csv', 'w+') as archivo:
                archivo.write( requests.get(url).content.decode() )

def clean_dp1():
    DataProduct1 = pd.read_csv("./datos/dp1_contagios.csv", parse_dates=["Fecha"])
    # Just RM
    filtro = (DataProduct1["Codigo region"] == 13) & (DataProduct1["Comuna"] != "Desconocido Metropolitana")
    DataProduct1 = DataProduct1[filtro]

    # Remove garbage
    DataProduct1 = DataProduct1.set_index("Fecha").drop(columns=["Region", "Codigo region"])
    DataProduct1['Comuna'] = DataProduct1['Comuna'].apply(lambda x: unidecode(x).lower())

    ######### ######### ######### ######### ######### ######### ######### ######### #########

    ## cov_all: Cantidad de contagios acumulativa x comuna(columnas) y fecha(index)
    cov_all = DataProduct1.pivot_table(values="Casos confirmados", index="Fecha", columns="Comuna").rename(columns=lambda x: unidecode(x).lower())  
    ## cov_new: Cantidad de contagios nuevos x comuna(columnas) y fecha(index)
    cov_new = cov_all.subtract( cov_all.shift(periods=1, fill_value=0) )

    return cov_new

def clean_df7():
    DataProduct7 = pd.read_csv("./datos/dp7_pcr.csv", parse_dates=["fecha"])

    # Just RM
    DataProduct7 = DataProduct7[ DataProduct7['Codigo region'] == 13 ]
    DataProduct7 = DataProduct7.set_index("fecha").drop(columns=["Region", "Codigo region", "Poblacion"])

    ######### ######### ######### ######### ######### ######### ######### ######### #########

    # cant_pcr: cantidad de pcr realizados por dia a nivel regional.
    cant_pcr = DataProduct7["numero"]
    return cant_pcr

def clean_df20():
    DataProduct20 = pd.read_csv("./datos/dp20_camas.csv", parse_dates=["fecha"])
    DataProduct20 = DataProduct20.set_index("fecha")

    ######### ######### ######### ######### ######### ######### ######### ######### #########

    # camas_criticas: Dataset que contiene el numero de camas criticas disp y ocupadas a nivel nacional.
    camas_criticas = pd.DataFrame({ 
        "totales": DataProduct20[ DataProduct20.Ventiladores == "total" ]["numero"],
        "disponibles": DataProduct20[ DataProduct20.Ventiladores == "disponibles" ]["numero"],
        "ocupados": DataProduct20[ DataProduct20.Ventiladores == "ocupados" ]["numero"]
    })
            
    return camas_criticas

def clean_df51():
    DataProduct51 = pd.read_csv("./datos/dp51_difs.csv", parse_dates=["Fecha"])
    DataProduct51 = DataProduct51[ DataProduct51['Codigo region'] == 13 ].drop(columns=['Region', 'Codigo region', 'Cartodb id'])

    parse_diff = lambda x: (100 + sum([ int(i)  for i in x[1:-2].replace('%','').split(",") ])/2)/ 100

    DataProduct51['Comuna'] = DataProduct51['Comuna'].apply(lambda x: unidecode(x).lower()) 

    DataProduct51['Salida']  = DataProduct51['Dif salida'].map(parse_diff)
    DataProduct51['Entrada'] = DataProduct51['Dif entrada'].map(parse_diff)

    ######### ######### ######### ######### ######### ######### ######### ######### #########

    # IM_salida: Valor promedio de la variación porcentual de salida entre las manzanas censales de cada comuna.
    IM_salida = DataProduct51.groupby(['Fecha', 'Comuna'], as_index=False)["Salida"].mean()
    IM_salida = IM_salida.pivot_table(values="Salida", columns="Comuna", index="Fecha")
    # IM_entrada: Valor promedio de la variación porcentual de entrada entre las manzanas censales de cada comuna.
    IM_entrada = DataProduct51.groupby(['Fecha', 'Comuna'], as_index=False)["Entrada"].mean()
    IM_entrada = IM_entrada.pivot_table(values="Entrada", columns="Comuna", index="Fecha")

    return IM_entrada

def clean_df82():
    DataProduct82a = pd.read_csv('./datos/dp82_weeks.csv', parse_dates=["fecha_inicio"])
    DataProduct82b = pd.read_csv('./datos/dp82_weekends.csv', parse_dates=["fecha_inicio"])

    DataProduct82 = pd.concat([DataProduct82a, DataProduct82b]).sort_values("fecha_inicio")

    DataProduct82 = DataProduct82[ DataProduct82['region'] == 13 ].drop(columns=['region'])
    DataProduct82["paso"] = DataProduct82["paso"].fillna(method="ffill")
    DataProduct82["nom_comuna"] = DataProduct82["nom_comuna"].apply(lambda x: unidecode(x).lower())

    # ######### ######### ######### ######### ######### ######### ######### ######### #########

    # paso_a_paso: Etapas del paso a paso de cada comuna por dia.
    paso_a_paso = DataProduct82.pivot_table(values='paso', index='fecha_inicio', columns='nom_comuna')

    # var_salidas: Variación del IM de salida de cada comuna por dia.
    var_salidas = DataProduct82.pivot_table(values="var_salidas", index="fecha_inicio", columns="nom_comuna")
    return var_salidas, paso_a_paso

def generate_ctx():
    im, cuarentenas = clean_df82()

    return {
            'casos_nuevos':     clean_dp1(),
            'pcrs_realizados':  clean_df7(),
            'camas_criticas':   clean_df20(),
            'IM_entrada_prom':  clean_df51(),
            'IM_salida_comuna': im,
            'paso_a_paso':      cuarentenas
    }
