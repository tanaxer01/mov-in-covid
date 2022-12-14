from sklearn.metrics         import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model    import LinearRegression
from gen_data import generate_ctx
import pandas as pd

def train_comuna(nombre, ctx, train_ratio=0.4):
    curr_data = pd.DataFrame({
        "nuevos_contagios":  ctx.casos_nuevos[nombre],
        "previos_contagios": ctx.casos_nuevos[nombre].shift(),
        "pcrs_realizados":   ctx.pcrs_realizados,
        "camas_ocupadas":    ctx.camas_criticas.ocupados,
        "variacion_salidas": ctx.IM_salida_comuna[nombre],
        "paso_comuna":       ctx.paso_a_paso[nombre]
    }).iloc[1:]

    # 1. Filtrar x fechas
    start_date, end_date = max([ i.index.min() for i in datasets.values() ]), min([ i.index.max() for i in datasets.values() ])
    curr_data = curr_data.loc[start_date:end_date]
    # 2 Interpolar datos faltantes
    curr_data["nuevos_contagios"] = curr_data["nuevos_contagios"].interpolate(limit=3)
    curr_data["variacion_salida"] = curr_data["variacion_salida"].interpolate(limit=3)
    curr_data["paso_comuna"]      = curr_data["paso_comuna"].fillna(method='ffill')

    curr_data = curr_data.dropna()
    curr_data = (curr_data - curr_data.mean()) / curr_data.std()

    split_index = round(curr_data.shape[0] * train_ratio)

    reg = LinearRegression(fit_intercept=False)
    reg.fit(curr_data.drop(columns="nuevos_contagios").iloc[:split_index] , curr_data["nuevos_contagios"].iloc[:split_index])

    return reg

def train_all(train_ratio=0.4):
    ctx = generate_ctx()
    comunas = ctx.casos_nuevos.Comuna.drop_duplicates()
    regs = {}
    for i in comunas:
        if i in ['san pedrop']:
            continue

        regs[i] = train_comuna(i, train_ratio)

    return regs
