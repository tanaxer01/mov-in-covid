"""
    This module provides the necesary functions for taining a model
"""
from sklearn.linear_model    import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
# from sklearn.neural_network  import MLPRegressor
from gen_data import DATA_PRODUCTS, generate_ctx

def train_model(x_vals, y_vals, test_size = 0.6, reg = LinearRegression()):
    '''Usa el predictor indicado en reg y entrena el modelo '''
    x_train, x_test, y_train, y_test = train_test_split(
        x_vals, y_vals, test_size=test_size, random_state=42
    )
    reg.fit(x_train, y_train)

    print( cross_val_score(reg, x_test, y_test, cv=10))

    return reg


ctx = generate_ctx()
print(ctx)
print(DATA_PRODUCTS.keys())
