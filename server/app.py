from flask import Flask
from flask_restful import Resource, Api
from get_data import *
from gen_model import *

app = Flask(__name__)
api = Api(app)
regs = ''

class DataFromDay(Resource):
    def get(self):
        X_test[['previos_contagios', 'pcrs_realizados', 'camas_ocupadas','variacion_salida', 'paso_comuna']]
        reg.predict()
        return {'hello': 'world'}
        

api.add_resource(DataFromDay, '/')

if __name__ == '__main__':
    download_data()
    ctx = generate_ctx()
    regs = train_all(ctx)
    
    
    app.run(debug=True)
