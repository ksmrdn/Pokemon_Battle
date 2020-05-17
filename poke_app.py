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
        url_poke1 = 'https://pokeapi.co/api/v2/pokemon/'+poke1_lo
        url_poke2 = 'https://pokeapi.co/api/v2/pokemon/'+poke2_lo
        req_data1 = requests.get(url_poke1)
        req_data2 = requests.get(url_poke2)
        
        if str(req_data1) == '<Response [404]>' or str(req_data2) == '<Response [404]>':
            return render_template('notFound.html')
        else:
            data1 = req_data1.json()
            data2 = req_data2.json()
            poke1_name = data1['forms'][0]['name']
            poke2_name = data2['forms'][0]['name']
            poke1_img = data1['sprites']['front_default']
            poke2_img = data2['sprites']['front_default']

            data1 = df_poke[df_poke['Name']==poke1_name.capitalize()][['HP','Attack','Defense','Sp. Atk','Sp. Def','Speed']].values.tolist()
            data2 = df_poke[df_poke['Name']==poke2_name.capitalize()][['HP','Attack','Defense','Sp. Atk','Sp. Def','Speed']].values.tolist()
           
                       
            if len(data1) == 0 or len(data2) == 0:
                return render_template('notFound.html')
            else:
                
                label = ['HP','Attack','Defense','Spec Attack','Spec Defend','Speed']
                img = io.BytesIO()

                x = np.arange(len(label))
                width = 0.5
                plt.bar(x - width/2, data1[0], width, label=poke1_name.capitalize(), color='#ff9900')
                plt.bar(x + width/2, data2[0], width, label=poke2_name.capitalize(), color='#000000')
                plt.xticks(ticks=x, labels=label)
                plt.legend()
                plt.tight_layout()
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