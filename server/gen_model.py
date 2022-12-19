import os
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model    import LinearRegression
from sklearn.neural_network  import MLPRegressor
from gen_data import generate_ctx

DEBUG = os.getenv('DEBUG') is not None

def create_dataframe(comuna, ctx):
    '''
    Crea el dataset necesario para entrenar un modelo de la comuna especificada.
    out vars
    ------------
    all_data: Dataset generado.
    '''
    todas_comunas = list( ctx['casos_nuevos'].drop(columns=[comuna, 'san pedro']) )

    movi = {"movi-"+i:  ctx["im_salida"][i].shift(periods=1)  for i in todas_comunas + [comuna]}
    # inim = {"inim-"+i:  ctx["im_entrada_prom"][i].shift(periods=1)  for i in todas_comunas + [comuna]}
    paso = {"paso-"+i:  ctx["paso_a_paso"][i].shift(periods=1) for i in todas_comunas + [comuna]}
    covd = {"covd-"+i : ctx["casos_nuevos"][i].shift() for i in todas_comunas }
    cnst = {
        "pcrs_realizados": ctx["pcrs_realizados"],
        "camas_criticas":  ctx["camas_criticas"].ocupados,
        "covd-"+comuna:  ctx["casos_nuevos"][comuna]
    }

    all_data = pd.DataFrame({**movi, **paso, **covd, **cnst}).iloc[20:]

    start_date = max((max(( j.index.min() for j in i.values() )) for i in [paso,covd,movi,cnst]))
    end_date   = min((min(( j.index.max() for j in i.values() )) for i in [paso,covd,movi,cnst]))

    all_data = all_data[start_date:end_date].interpolate(limit=3).dropna()
    all_data = (all_data - all_data.mean())/all_data.std()

    return all_data

def split_data(comuna, data_comuna, test_size=0.6):
    ''' 
    Divide los datos entre info de los datos de
    entrenamiento y los datos disponibles para
    utilizar. 
    out vars
    ------------
    (x_train, y_train): Datos de entrenamiento.
    (x_test, y_test):   Datos para predicciones y
    valores reales de estos.
    '''
    x_val = data_comuna.drop(columns=["covd-"+comuna])
    y_val = data_comuna['covd-'+comuna]

    x_train, x_test, y_train, y_test = train_test_split(
        x_val, y_val, test_size=test_size,random_state=42
    )

    return (x_train, y_train), (x_test, y_test) 

def train_model(reg, x_train, y_train, x_test, y_test):
    '''
    Entrena el modelo indicado y calcula el cross val score
    si DEBUG == 1
    out vars
    --------
    reg: Modelo entrenado
    '''
    reg = LinearRegression(fit_intercept=False)
    reg.fit(x_train.values, y_train)

    if DEBUG:
        scores = cross_val_score(reg, x_test, y_test, cv=10)
        print(f"cross_val: {scores.mean():.3f} accuracy with a std of {scores.std():.3f}")

    return reg

if __name__ == "__main__":
    # CSV -> Pandas
    contexto = generate_ctx()

    nombres_comunas = list( contexto['casos_nuevos'].drop(columns=['san pedro']) )
    # Gen df para entrenar cada modelo.
    df_comunas = { i:create_dataframe(i, contexto) for i in nombres_comunas }
    # Split entre train y test data.
    splits_comunas  = { i: split_data(i, j) for i, j in df_comunas.items() }
    # Entrenamiento de los modelos
    modelos_comunas = {
        c : train_model(MLPRegressor(random_state=1, max_iter=500),*i, *j) for c, (i, j) in splits_comunas.items() 
        # c:train_model(LinearRegression(),*i, *j) for c, (i, j) in splits_comunas.items() 
    }

    # Ej. 1 - Predict de todos los datos
    print(len(modelos_comunas['santiago'].predict(splits_comunas['santiago'][1][0])))

    # Ej. 2 - Predict de una fila
    print(len(modelos_comunas['santiago'].predict([ splits_comunas['santiago'][1][0].iloc[0].values ])))

