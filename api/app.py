import sys

# To include the pragcc module in the python path
sys.path.extend(['.', '..'])

from flask import Flask
from apis import api

app = Flask(__name__)
api.init_app(app)

app.run(debug=True,host='0.0.0.0',port=5000)