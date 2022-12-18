from flask import Flask
from flask_restful import Resource, Api, request
from get_data import *
from gen_model import *

app = Flask(__name__)
api = Api(app)
regs = ''

class DataFromDay(Resource):
    def get(self):
        args = request.args
        if (args['fecha'] == ''):
            return 400

        comunas = ctx['casos_nuevos'].keys()
        fecha = args['fecha']
        results = []

        for nombre in comunas:
            if (nombre == 'san pedro'):
                continue

            curr_data = pd.DataFrame({
                "previos_contagios": (ctx['casos_nuevos'])[nombre].shift(),
                "pcrs_realizados":   ctx['pcrs_realizados'],
                "camas_ocupadas":    ctx['camas_criticas'].ocupados,
                "variacion_salidas": (ctx['im_salida'])[nombre],
                "paso_comuna":       (ctx['paso_a_paso'])[nombre]
            })

            curr_data["variacion_salidas"] = curr_data["variacion_salidas"].interpolate(limit=3)
            curr_data["paso_comuna"]      = curr_data["paso_comuna"].fillna(method='ffill')

            curr_data = curr_data.dropna()
            #curr_data = (curr_data - curr_data.mean()) / curr_data.std()
            
            to_predict = curr_data.loc[fecha : fecha]
            value_comuna = (regs[nombre].predict(to_predict)[0]) #* curr_data.mean()[0] ) + curr_data.std()[0]
            #print(value_comuna)
            results.append({nombre: value_comuna})

        return results
        

api.add_resource(DataFromDay, '/datafromday')

if __name__ == '__main__':
    download_data()
    ctx = generate_ctx()
    regs = train_all(ctx)
    
    
    app.run(debug=True)
