"""
    Train Model & Generate predicts
"""
import pandas as pd
# from sklearn.metrics         import mean_squared_error, mean_absolute_error, r2_score
# from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model    import LinearRegression
from gen_data import generate_ctx

def train_comuna(nombre, ctx, train_ratio=0.4):
    """This func trains """
    curr_data = pd.DataFrame({
        "nuevos_contagios":  ctx["casos_nuevos"][nombre],
        "previos_contagios": ctx["casos_nuevos"][nombre].shift(),
        "pcrs_realizados":   ctx["pcrs_realizados"],
        "camas_ocupadas":    ctx["camas_criticas"].ocupados,
        "variacion_salidas": ctx["im_salida"][nombre],
        "paso_comuna":       ctx["paso_a_paso"][nombre]
    }).iloc[1:]

    # 1. Filtrar x fechas
    # start_date = max((max(( j.index.min() for j in i.values() )) for i in [,covd,movi,cnst]))
    # end_date   = min((min(( j.index.max() for j in i.values() )) for i in [paso,covd,movi,cnst]))

    # curr_data = curr_data.loc[start_date:end_date]

    # 2 Interpolar datos faltantes
    curr_data["nuevos_contagios"] = curr_data["nuevos_contagios"].interpolate(limit=3)
    curr_data["variacion_salidas"] = curr_data["variacion_salidas"].interpolate(limit=3)
    curr_data["paso_comuna"]      = curr_data["paso_comuna"].fillna(method='ffill')

    curr_data = curr_data.dropna()
    curr_data = (curr_data - curr_data.mean()) / curr_data.std()

    split_index = round(curr_data.shape[0] * train_ratio)
    split_x = curr_data.drop(columns="nuevos_contagios").iloc[:split_index]
    split_y = curr_data["nuevos_contagios"].iloc[:split_index]

    reg = LinearRegression(fit_intercept=False)
    reg.fit(split_x.values, split_y)

    return reg

def train_all(ctx, train_ratio=0.4):
    """a"""
    comunas = ctx["casos_nuevos"].columns

    regs = {}
    for i in comunas:
        if i in ['san pedro']:
            continue

        regs[i] = train_comuna(i, ctx, train_ratio)

    return regs


if __name__ == "__main__":
    ctxto = generate_ctx()
    modelos = train_all(ctxto)

    df = pd.DataFrame({
        "nuevos_contagios":  ctxto["casos_nuevos"]['santiago'],
        "previos_contagios": ctxto["casos_nuevos"]['santiago'].shift(),
        "pcrs_realizados":   ctxto["pcrs_realizados"],
        "camas_ocupadas":    ctxto["camas_criticas"].ocupados,
        "variacion_salidas": ctxto["im_salida"]['santiago'],
        "paso_comuna":       ctxto["paso_a_paso"]['santiago']
    }).iloc[1:]

    df["nuevos_contagios"]  = df["nuevos_contagios"].interpolate(limit=3)
    df["variacion_salidas"] = df["variacion_salidas"].interpolate(limit=3)
    df["paso_comuna"]       = df["paso_comuna"].fillna(method='ffill')

    df = df.dropna()
    df = (df - df.mean()) / df.std()

    a = round(df.shape[0] * 0.7)
    X = df.drop(columns='nuevos_contagios').iloc[:a+1]
    y = df['nuevos_contagios'].iloc[:a+1]

    line = X.iloc[0]
    print(line.values)
    print(line.values[None])
    # print(modelos['santiago'].predict(line.values[None]))
    print(modelos['santiago'].predict([line.values]))
    print("-----")
    print(modelos['santiago'].rank_)
    print(modelos['santiago'].coef_)
    print(X.columns)

