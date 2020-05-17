import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, abort, send_from_directory, url_for, redirect, jsonify
import requests
import json
import joblib
import base64
import io

app = Flask(__name__)

df_poke = pd.read_csv("datasets/pokemon.csv")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result', methods = ['POST','GET'])
def result():
    if request.method == 'POST':
        poke1 = request.form['pokemon1']
        poke2 = request.form['pokemon2']
        poke1_lo = poke1.lower()
        poke2_lo = poke2.lower()
        
        new1 = []
        for sp in poke1_lo:
            if sp.isspace():
                print('True')
                splitting = poke1_lo.split(' ')
                print(splitting)
                for x in splitting:
                    y = x.capitalize()
                    new1.append(y)
                    if len(new1) == 2:
                        poke1_lo = new1[0] + ' ' + new1[1]
                    elif len(new1) == 3:
                        poke1_lo = new1[0] + ' ' + new1[1] + ' ' + new1[2]
                data1 = df_poke[df_poke['Name'] == poke1_lo][['HP','Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']].values.tolist()
                poke1_name = poke1_lo
                poke1_img = 'https://vignette.wikia.nocookie.net/pokemon-fano/images/6/6f/Poke_Ball.png/revision/latest/scale-to-width-down/340?cb=20140520015336'
                break
            else:
                url_poke1 = 'https://pokeapi.co/api/v2/pokemon/'+poke1_lo
                req_data1 = requests.get(url_poke1)
                if str(req_data1) == '<Response [404]>':
                    return render_template('notFound.html')
                else:
                    data1 = req_data1.json()
                    poke1_name = data1['forms'][0]['name']
                    poke1_img = data1['sprites']['front_default']
                    data1 = df_poke[df_poke['Name']==poke1_name.capitalize()][['HP','Attack','Defense','Sp. Atk','Sp. Def','Speed']].values.tolist()

        new2 = []
        for sp in poke2_lo:
            if sp.isspace():
                print('True')
                splitting = poke2_lo.split(' ')
                print(splitting)
                for x in splitting:
                    y = x.capitalize()
                    new2.append(y)
                    if len(new2) == 2:
                        poke2_lo = new2[0] + ' ' + new2[1]
                    elif len(new2) == 3:
                        poke2_lo = new2[0] + ' ' + new2[1] + ' ' + new[2]
                data2 = df_poke[df_poke['Name'] == poke2_lo][['HP','Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']].values.tolist()
                poke2_name = poke2_lo
                poke2_img = 'https://vignette.wikia.nocookie.net/pokemon-fano/images/6/6f/Poke_Ball.png/revision/latest/scale-to-width-down/340?cb=20140520015336'
                break
            else:
                url_poke2 = 'https://pokeapi.co/api/v2/pokemon/'+poke2_lo
                req_data2 = requests.get(url_poke2)
                if str(req_data2) == '<Response [404]>':
                    return render_template('notFound.html')
                else:
                    data2 = req_data2.json()
                    poke2_name = data2['forms'][0]['name']
                    poke2_img = data2['sprites']['front_default']
                    data2 = df_poke[df_poke['Name']==poke2_name.capitalize()][['HP','Attack','Defense','Sp. Atk','Sp. Def','Speed']].values.tolist()

                    if len(data1) == 0 or len(data2) == 0:
                        return render_template('notFound.html')
                    else:
                        label = ['HP','Attack','Defense','Spec Attack','Spec Defend','Speed']
                        x = np.arange(len(label))
                        width = 0.3

                        plt.bar(x - width/2, data1[0], width, label=poke1_name.capitalize(), color='#ff9900')
                        plt.bar(x + width/2, data2[0], width, label=poke2_name.capitalize(), color='#000000')
                        plt.xticks(ticks=x, labels=label)
                        plt.legend()
                        plt.tight_layout()
                        
                        img = io.BytesIO()
                        plt.savefig(img, format='png', transparent=True)
                        plt.close()
                        img.seek(0)
                        pict_url = base64.b64encode(img.getvalue()).decode()
                        pict = f'data:image/png;base64,{pict_url}'

                        test_data = data1[0]
                        test_data.extend(data2[0])
                        pred = model.predict([test_data])[0]
                        print(data1[0])
                        print(pred)
                        if pred == 1:
                            who_win = poke2_name.capitalize()
                            pred_proba = round(model.predict_proba([test_data])[0][pred]*100, 2)
                            print(f'{poke2_name} Probability Win is {pred_proba:.2f} %')
                        elif pred == 0:
                            who_win = poke1_name.capitalize()
                            pred_proba = round(model.predict_proba([test_data])[0][pred]*100, 2)
                            print(f'{poke1_name} Probability Win is {pred_proba:.2f} %')
                        take_result = {'poke1_nama': poke1_name.capitalize(), 'poke2_nama': poke2_name.capitalize(),
                        'poke1_url': poke1_img, 'poke2_url': poke2_img, 'winner': who_win, 'probability': pred_proba}

                        return render_template('result.html', hasil = take_result, gambar = pict)
    else:
        return redirect(url_for('home'))

@app.route('/filetemp/<path:path>')                           
def filetemp(path):
    return send_from_directory('./templates/image', path)

@app.errorhandler(404)
def error(error):
    return render_template('error.html')

if __name__ == '__main__':
    model = joblib.load('model_gbc')
    app.run(debug=True, port=2050)