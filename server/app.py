from flask import Flask
from flask_restful import Resource, Api, request
from flask_cors import CORS
from gen_data import *
from gen_model import *

app = Flask(__name__)
api = Api(app)
CORS(app)
nombres_comunas = ''
splits_comunas = ''


class DataFromDay(Resource):
    def get(self):
        args = request.args
        if (args['fecha'] == ''):
            return 400

        results = []
        for c in nombres_comunas:
            if (c == "san pedro"):
               continue
            results.append({ c: modelos_comunas[c].predict([ splits_comunas[c][1][0].loc[args['fecha']].values ]).tolist()[0] })
        return results, {'Access-Control-Allow-Origin': '*'}
        
class Dates(Resource):
    def get(self):
        all_dates = splits_comunas['santiago'][1][0].index
        dates = all_dates.strftime("%Y-%m-%d").tolist()
        return dates, {'Access-Control-Allow-Origin': '*'}

class AllData(Resource):
    def get(self):
        args = request.args
        if (args['comuna'] == ''):
            return 400

        # Array of results: Dates
        all_dates = splits_comunas['santiago'][1][0].index
        dates = all_dates.strftime("%Y-%m-%d").tolist()

        # Array of results: Values
        values = modelos_comunas[args['comuna']].predict(splits_comunas[args['comuna']][1][0])

        results = {}
        for i in range(len(values)):
            results[dates[i]] = values[i]
        
        return results, {'Access-Control-Allow-Origin': '*'}

class Comunas(Resource):
    def get(self):
        return nombres_comunas, {'Access-Control-Allow-Origin': '*'}

api.add_resource(DataFromDay, '/datafromday')
api.add_resource(AllData, '/alldata')
api.add_resource(Dates, '/predictdates')
api.add_resource(Comunas, '/comunas')

if __name__ == '__main__':
    download_data()

    ctx = generate_ctx()
    contexto = generate_ctx()

    nombres_comunas = list( contexto['casos_nuevos'].drop(columns=['san pedro']) )
    df_comunas = { i:create_dataframe(i, contexto) for i in nombres_comunas }
    splits_comunas  = { i: split_data(i, j) for i, j in df_comunas.items() }
    modelos_comunas = {
        c : train_model(MLPRegressor(random_state=1, max_iter=500),*i, *j) for c, (i, j) in splits_comunas.items() 
    }

    app.run(debug=True)
