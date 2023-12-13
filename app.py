from flask import Flask
from flask import jsonify
import config as config

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Simple web for test jenkins co-work with zap.'

@app.route('/stub')
def stub():
    return 'Value of Stub: ' + str(config.STUB_VARIABLE)

if __name__ == '__main__':
    app.run()