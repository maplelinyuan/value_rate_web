from flask import Flask, Markup, make_response
from flask_restful import Api, Resource
from flask import render_template, request, session, url_for, redirect, flash
import logging
from logging.handlers import TimedRotatingFileHandler
import configs
from flask_pymongo import PyMongo

app = Flask(__name__)
app.debug = True
app.config.from_object(configs)

app.config.update(
    MONGO_URI='mongodb://localhost:27019/market_value',
    MONGO_USERNAME='',
    MONGO_PASSWORD=''
)
mongo = PyMongo(app)

app_2 = Flask('dongqiudi')
app_2.debug = True
app_2.config.from_object(configs)
app_2.config.update(
    MONGO_URI='mongodb://localhost:27019/player_analysis',
    MONGO_USERNAME='',
    MONGO_PASSWORD=''
)
mongo_2 = PyMongo(app_2)

@app.route('/')
def index():
    return Markup('<div>Hello %s</div>') % '<em>Flask</em>'

@app.route('/dongqiudi/')
def dongqiudi():
    matchs = mongo_2.db.dongqiudi_player.find({'score': 'VS', 'support_direction': {'$ne': ''}, "match_day": {"$gt": "2018-11-15"}})
    return render_template('dongqiudi.html', matchs=matchs)

@app.route('/matchs/')
def matchs():
    qi_shu = mongo.db.new_realtime_matchs.find().sort([('qi_shu', -1)])[0]['qi_shu']
    # qi_shu = 181004
    matchs = mongo.db.new_realtime_matchs.find({'qi_shu': qi_shu}).sort([('match_time', 1)])
    return render_template('matchs.html', matchs=matchs)

@app.route('/shili_matchs/')
def shili_matchs():
    qi_shu = mongo.db.shili_realtime_matchs.find().sort([('qi_shu', -1)])[0]['qi_shu']
    # qi_shu = 180903
    matchs = mongo.db.shili_realtime_matchs.find({'qi_shu': qi_shu}).sort([('match_time', 1)])
    return render_template('shili_matchs.html', matchs=matchs)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=400):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

@app.errorhandler(InvalidUsage)
def invalid_usage(error):
    response = make_response(error.message)
    response.status_code = error.status_code
    return response

@app.route('/exception')
def exception():
    app.logger.debug('Enter exception method')
    app.logger.error('403 error happened')
    raise InvalidUsage('No privilege to access the resource', status_code=403)

# 日志部分
server_log = TimedRotatingFileHandler('server.log', 'D')
server_log.setLevel(logging.DEBUG)
server_log.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s'
))
error_log = TimedRotatingFileHandler('error.log', 'D')
error_log.setLevel(logging.ERROR)
error_log.setFormatter(logging.Formatter(
    '%(asctime)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(server_log)
app.logger.addHandler(error_log)
# 日志部分结束

if __name__ == '__main__':
    app.run()
