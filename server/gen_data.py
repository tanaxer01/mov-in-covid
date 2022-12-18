"""
    Creates df for each data_products used in the proyect.
    It also filters and prepare data to be used.
"""
import os
import requests
import pandas as pd
from unidecode import unidecode

DATA_PRODUCTS = {}

def download_data():
    ''' Downloads each data product into ./data '''
    prefix = "https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto"

    datasets = {
      # DP1
      "dp1_contagios": prefix + "1/Covid-19_std.csv",
      # DP7
      "dp7_pcr": prefix + "7/PCR_std.csv",
      # DP20
      "dp20_camas": prefix + "20/NumeroVentiladores_std.csv",
      # DP51
      "dp51_difs": prefix + "51/ISCI_std.csv",
      # DP82
      "dp82_weeks": prefix + "82/ISCI_weeks.csv",
      "dp82_weekends": prefix + "82/ISCI_weekends.csv",
    }

    if not os.path.exists("./datos"):
        os.mkdir('./datos')

    for name, url in datasets.items():
        if not os.path.exists(f'./datos/{name}.csv'):
            with open(f'./datos/{name}.csv', 'w+', encoding="utf-8") as archivo:
                archivo.write( requests.get(url, timeout=10).content.decode() )

def clean_dp1()  -> pd.DataFrame():
    '''
    Prepare Dataproduct 1

    out_vars
    -------------
    cov_all: Cantidad de contagios acumulativa x comuna(columnas) y fecha(index)

    cov_new: Cantidad de contagios nuevos x comuna(columnas) y fecha(index)
    '''
    data_product1 = pd.read_csv("./datos/dp1_contagios.csv", parse_dates=["Fecha"])
    # Just RM
    filtro = (data_product1["Codigo region"] == 13) &\
        (data_product1["Comuna"] != "Desconocido Metropolitana")

    data_product1 = data_product1[filtro]

    # Remove garbage
    data_product1 = data_product1.set_index("Fecha").drop(columns=["Region", "Codigo region"])
    data_product1['Comuna'] = data_product1['Comuna'].apply(lambda x: unidecode(x).lower())

    DATA_PRODUCTS[1] = data_product1
    ######### ######### ######### ######### ######### ######### ######### ######### #########
    cov_all = data_product1.pivot_table(
        values="Casos confirmados", index="Fecha", columns="Comuna"
    ).rename(columns=lambda x: unidecode(x).lower())

    cov_new = cov_all.subtract( cov_all.shift(periods=1, fill_value=0) )
    return cov_new

def clean_df7()  -> pd.DataFrame():
    '''
    Prepare Dataproduct 7

    out_vars
    -------------
    cant_pcr: cantidad de pcr realizados por dia a nivel regional.
    '''
    data_product7 = pd.read_csv("./datos/dp7_pcr.csv", parse_dates=["fecha"])

    # Just RM
    data_product7 = data_product7[ data_product7['Codigo region'] == 13 ]
    data_product7 = data_product7\
            .set_index("fecha")\
            .drop(columns=["Region", "Codigo region", "Poblacion"])

    DATA_PRODUCTS[7] = data_product7
    ######### ######### ######### ######### ######### ######### ######### ######### #########
    cant_pcr = data_product7["numero"]

    return cant_pcr

def clean_df20() -> pd.DataFrame():
    '''
    Prepare Dataproduct 20

    out_vars
    -------------
    camas_criticas: Dataset que contiene el numero de camas criticas disp y
    ocupadas a nivel nacional.
    '''
    data_product20 = pd.read_csv("./datos/dp20_camas.csv", parse_dates=["fecha"])
    data_product20 = data_product20.set_index("fecha")

    DATA_PRODUCTS[20] = data_product20
    ######### ######### ######### ######### ######### ######### ######### ######### #########
    camas_criticas = pd.DataFrame({
        "totales": data_product20[ data_product20.Ventiladores == "total" ]["numero"],
        "disponibles": data_product20[ data_product20.Ventiladores == "disponibles" ]["numero"],
        "ocupados": data_product20[ data_product20.Ventiladores == "ocupados" ]["numero"]
    })

    return camas_criticas

def clean_df51() -> (pd.DataFrame, pd.DataFrame):
    '''
    Prepare Dataproduct 51

    out_vars
    -------------
    im_salida: Valor promedio de la variación porcentual de salida entre las manzanas
    censales de cada comuna.

    im_entrada: Valor promedio de la variación porcentual de entrada entre las manzanas
    censales de cada comuna.
    '''
    def parse_diff(target_diff):
        diff_arr = [ int(i) for i in target_diff[1:-2].replace('%','').split(",") ]
        return (100 + sum(diff_arr)/2)/ 100

    data_product51 = pd.read_csv("./datos/dp51_difs.csv", parse_dates=["Fecha"])
    # Just RM
    data_product51 = data_product51[ data_product51['Codigo region'] == 13 ] \
            .drop(columns=['Region', 'Codigo region', 'Cartodb id'])

    # Remove garbage
    data_product51['Comuna'] = data_product51['Comuna'].apply(lambda x: unidecode(x).lower())

    data_product51['Salida']  = data_product51['Dif salida'].map(parse_diff)
    data_product51['Entrada'] = data_product51['Dif entrada'].map(parse_diff)

    DATA_PRODUCTS[51] = data_product51
    ######### ######### ######### ######### ######### ######### ######### ######### #########

    im_prom_salida = data_product51.groupby(['Fecha', 'Comuna'], as_index=False)["Salida"].mean()
    im_prom_salida = im_prom_salida.pivot_table(values="Salida", columns="Comuna", index="Fecha")

    im_prom_entrada = data_product51.groupby(['Fecha', 'Comuna'], as_index=False)["Entrada"].mean()
    im_prom_entrada = im_prom_entrada.pivot_table(values="Entrada", columns="Comuna", index="Fecha")

    return im_prom_entrada, im_prom_salida

def clean_df82() -> (pd.DataFrame, pd.DataFrame):
    '''
    Prepare Dataproduct 82

    out_vars
    -------------
    paso_a_paso: Etapas del paso a paso de cada comuna por dia.

    var_salidas: Variación del IM de salida de cada comuna por dia.
    '''
    data_product82a = pd.read_csv('./datos/dp82_weeks.csv', parse_dates=["fecha_inicio"])
    data_product82b = pd.read_csv('./datos/dp82_weekends.csv', parse_dates=["fecha_inicio"])

    data_product82 = pd.concat([data_product82a, data_product82b]).sort_values("fecha_inicio")

    data_product82 = data_product82[ data_product82['region'] == 13 ].drop(columns=['region'])
    data_product82["paso"] = data_product82["paso"].fillna(method="ffill")
    data_product82["nom_comuna"] = data_product82["nom_comuna"] \
        .apply(lambda x: unidecode(x).lower())

    DATA_PRODUCTS[82] = data_product82
    # ######### ######### ######### ######### ######### ######### ######### ######### #########
    paso_a_paso = data_product82.pivot_table(
        values='paso', index='fecha_inicio', columns='nom_comuna'
    )

    var_salidas = data_product82.pivot_table(
        values="var_salidas", index="fecha_inicio", columns="nom_comuna"
    )
    return var_salidas, paso_a_paso

def generate_ctx() -> dict:
    '''
    Prepare Dataproduct 82

    out_vars
    -------------
    paso_a_paso: Etapas del paso a paso de cada comuna por dia.

    var_salidas: Variación del IM de salida de cada comuna por dia.
    '''
    download_data()

    entrada_prom, _     = clean_df51()
    salida, cuarentenas = clean_df82()

    return {
            'casos_nuevos':     clean_dp1(),
            'pcrs_realizados':  clean_df7(),
            'camas_criticas':   clean_df20(),
            'im_entrada_prom':  entrada_prom,
            'im_salida':        salida,
            'paso_a_paso':      cuarentenas
    }
