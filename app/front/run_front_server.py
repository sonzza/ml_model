import json

from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from requests.exceptions import ConnectionError
from wtforms import IntegerField, SelectField, StringField
from wtforms.validators import DataRequired

import urllib.request
import json


class ClientDataForm(FlaskForm):
    totsp = StringField('Общая площадь в метрах', validators=[DataRequired()])
    livesp = StringField('Жилая площадь в метрах', validators=[DataRequired()])
    kitsp = StringField('Площадь кухни в метрах', validators=[DataRequired()])
    dist = StringField('До центра в км', validators=[DataRequired()])
    metrdist = StringField('До метро в минутах', validators=[DataRequired()])
    walk = StringField('до метро пешком? да - 1, нет - 0', validators=[DataRequired()])
    brick = StringField('Дом построен из: \n 1 – кирпичный, монолит ж/б, 0 – другой', validators=[DataRequired()])
    floor = StringField('1 – этаж кроме первого и последнего, 0 – иначе', validators=[DataRequired()])
    code = StringField('линия метро (от 1 до 8):\
            1.  Калужско-Рижская \
            2. Серпуховско-Тимирязевская \
            3. Замоскворецкая \
            4. Таганско-Краснопресненская  \
            5. Люблинская \
            6. Таганско-Краснопресненская \
            7. Калиниская \
            8. Арбатско-Покровская линии', validators=[DataRequired()])


app = Flask(__name__, template_folder='templates')
app.config.update(
    CSRF_ENABLED=True,
    SECRET_KEY='you-will-never-guess',
)


def get_prediction(totsp, livesp, kitsp, dist, metrdist, walk, brick, floor, code):
    body = {"totsp": totsp,
            'livesp': livesp,
            'kitsp': kitsp,
            'dist': dist,
            'metrdist': metrdist,
            'walk': walk,
            'brick': brick,
            'floor': floor,
            'code': code
            }

    myurl = "http://127.0.0.1:8180/predict"
    req = urllib.request.Request(myurl)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(body)
    jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes
    req.add_header('Content-Length', len(jsondataasbytes))
    response = urllib.request.urlopen(req, jsondataasbytes)
    return json.loads(response.read())['predictions']


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/predicted/<response>')
def predicted(response):
    response = json.loads(response)
    print(response)
    return render_template('predicted.html', response=response)


@app.route('/predict_form', methods=['GET', 'POST'])
def predict_form():
    form = ClientDataForm()
    data = dict()
    if request.method == 'POST':
        data['totsp'] = request.form.get('totsp')
        data['livesp'] = request.form.get('livesp')
        data['kitsp'] = request.form.get('kitsp')
        data['dist'] = request.form.get('dist')
        data['metrdist'] = request.form.get('metrdist')
        data['walk'] = request.form.get('walk')
        data['brick'] = request.form.get('brick')
        data['floor'] = request.form.get('floor')
        data['code'] = request.form.get('code')


        try:
            response = str(get_prediction(data['totsp'],
                                          data['livesp'],
                                          data['kitsp'],
                                          data['dist'],
                                          data['metrdist'],
                                          data['walk'],
                                          data['brick'],
                                          data['floor'],
                                          data['code']
                                          ))
            print(response)
        except ConnectionError:
            response = json.dumps({"error": "ConnectionError"})
        return redirect(url_for('predicted', response=response))
    return render_template('form.html', form=form)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8181, debug=True)
