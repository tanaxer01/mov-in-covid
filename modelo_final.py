"""
    This module provides the necesary functions for training a model
"""

import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model    import LinearRegression
# from sklearn.neural_network  import MLPRegressor
from gen_data import generate_ctx


def train_model(regr, x_vals, y_vals, test_size = 0.6):
    '''Trains a given regresion model with input data.'''
    x_train, x_test, y_train, y_test = train_test_split(
        x_vals, y_vals, test_size=test_size, random_state=42
    )
    regr.fit(x_train, y_train)

    scores = cross_val_score(regr, x_test, y_test, cv=10)
    print(f"cross_val: {scores.mean():.3f} accuracy with a std of {scores.std():.3f}")

    return regr


if __name__ == "__main__":
    ctx  = generate_ctx()

    comunas = [
        "maria pinto",
        "la granja",
        "recoleta",
        "quinta normal",
        "cerrillos",
        "cerro navia",
        "lo prado",
        "pedro aguirre cerda"
    ]

    movi = { "movi-"+i:  ctx["im_salida"][i].shift(periods=20)  for i in comunas + ["santiago"] }
    paso = { "paso-"+i:  ctx["paso_a_paso"][i].shift(periods=4) for i in comunas + ["santiago"] }
    covd = { "covd-"+i : ctx["casos_nuevos"][i].shift() for i in comunas }
    cnst = {
        "pcrs_realizados": ctx["pcrs_realizados"],
        "covid-santiago":  ctx["casos_nuevos"].santiago
    }

    all_data = pd.DataFrame({**movi, **paso, **covd, **cnst}).iloc[20:]

    start_date = max((max(( j.index.min() for j in i.values() )) for i in [paso,covd,movi,cnst]))
    end_date   = min((min(( j.index.max() for j in i.values() )) for i in [paso,covd,movi,cnst]))

    all_data = all_data[start_date:end_date].interpolate(limit=3)

    all_data = all_data.dropna()
    all_data = (all_data - all_data.mean())/all_data.std()

    X = all_data.drop(columns=["covid-santiago"])
    y = all_data["covid-santiago"]

    reg = train_model(LinearRegression(), X, y)
