#!/usr/bin/env python
# coding: utf-8

from flask import Flask, render_template, request
import csv

app = Flask(__name__, static_url_path='/static')

# Read in element data from CSV file
element_data = {}
compounds = []

with open('molecular_weights.csv','r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header row
    for row in reader:
        symbol = row[0]
        weight = row[1]
        if symbol and weight:  # Check if symbol and weight are not empty
            element_data[symbol] = float(weight)
        compounds.append(row[2])  # Get the third column (formula)


def calculate_results(MC, MI, elements, ratio_CA_EDTA):
    EDTA_MW = element_data['EDTA']
    CA_MW = element_data['Citric_acid']
    EDTA = MC * MI * EDTA_MW
    CA = MC * MI * ratio_CA_EDTA * CA_MW

    results = []
    for symbol, mf in elements:
        if symbol in element_data:
            mw = element_data[symbol]
            amount = MC * mf * mw
            compound = compounds[list(element_data.keys()).index(symbol)]
            results.append((symbol, compound, '{:.5f}'.format(amount)))
        else:
            results.append((symbol, 'Unknown Compound', '0.00000'))

    return '{:.5f}'.format(EDTA), '{:.5f}'.format(CA), results


@app.route('/')
def index():
    return render_template('index.html', compounds=compounds)


@app.route('/calculate', methods=['POST'])
def calculate():
    MC = float(request.form['mc'])
    MI = int(request.form['mi'])
    ratio_EDTA_CA = float(request.form['ratio_ca_edta'])
    elements = []

    # Retrieve the submitted form data
    form_data = request.form.to_dict()

    # Extract the element symbols and molar fractions from the form data
    for key, value in form_data.items():
        if key.startswith('symbol_'):
            index = key.split('_')[1]
            symbol = value
            mf_key = f'mf_{index}'
            if mf_key in form_data:
                mf = float(form_data[mf_key])
                elements.append((symbol, mf))

    EDTA, CA, results = calculate_results(MC, MI, elements, ratio_EDTA_CA)

    return render_template('results.html', EDTA=EDTA, CA=CA, results=results)

app.static_folder = 'static'

if __name__ == '__main__':
    app.run(debug=True)
