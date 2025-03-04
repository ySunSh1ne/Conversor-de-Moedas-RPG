from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dicionário global com as taxas de conversão para cada sistema/cidade.
# As taxas representam quantos "cobre base" equivale a 1 moeda do tipo correspondente.
conversion_rates = {
    "Base": {
        "Copper": 1,
        "Silver": 100,
        "Gold": 10000,
        "Platinum": 1000000
    },
    "Veil": {
        "Copper": 0.5,
        "Silver": 250,
        "Gold": 50000
        # Note que Veil não define Platina
    },
    "Millon": {
        "Copper": 0.3,
        "Silver": 300,
        "Gold": 100000
        # Millon também não define Platina
    }
}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    total_base = 0.0
    available_cities = list(conversion_rates.keys())
    
    if request.method == 'POST':
        cities = request.form.getlist('city')
        coins = request.form.getlist('coin')
        quantities = request.form.getlist('quantity')
        target = request.form.get('target')
        
        # Soma o total convertido para "cobre base" usando as taxas definidas.
        for i in range(len(cities)):
            city = cities[i]
            coin = coins[i]
            try:
                quantity = float(quantities[i])
            except (ValueError, TypeError):
                quantity = 0
            rate = conversion_rates.get(city, {}).get(coin)
            if rate is None:
                continue
            total_base += quantity * rate

        # Converter o total em cobre base para a moeda do sistema de destino.
        target_rates = conversion_rates.get(target, {})
        result = {}
        remaining = total_base
        
        # Define a ordem de conversão de acordo com as moedas disponíveis
        if "Platinum" in target_rates:
            order = ["Platinum", "Gold", "Silver", "Copper"]
        else:
            order = ["Gold", "Silver", "Copper"]
        
        for idx, coin in enumerate(order):
            # Para as moedas que não são a última, usamos divisão inteira.
            if idx < len(order) - 1:
                value = target_rates.get(coin)
                if value and value > 0:
                    count = int(remaining // value)
                    result[coin] = count
                    remaining = remaining % value
            else:
                # Última moeda: exibe o valor restante com duas casas decimais.
                result[coin] = round(remaining, 2)
        
    return render_template('index.html', result=result, total_base=round(total_base, 2), cities=available_cities)

@app.route('/add-city', methods=['GET', 'POST'])
def add_city():
    message = ""
    if request.method == 'POST':
        city_name = request.form.get('city_name')
        try:
            copper_rate = float(request.form.get('copper_rate'))
            silver_rate = float(request.form.get('silver_rate'))
            gold_rate = float(request.form.get('gold_rate'))
        except (ValueError, TypeError):
            message = "Verifique os valores numéricos."
            return render_template('add_city.html', message=message)
        
        # Platinum é opcional
        platinum_rate_input = request.form.get('platinum_rate')
        if platinum_rate_input:
            try:
                platinum_rate = float(platinum_rate_input)
            except (ValueError, TypeError):
                platinum_rate = None
        else:
            platinum_rate = None
        
        # Cria o dicionário para a nova cidade com as taxas definidas.
        new_city = {
            "Copper": copper_rate,
            "Silver": silver_rate,
            "Gold": gold_rate
        }
        if platinum_rate is not None:
            new_city["Platinum"] = platinum_rate
        
        # Adiciona ou atualiza a cidade no dicionário global.
        conversion_rates[city_name] = new_city
        message = f"Nova cidade '{city_name}' adicionada com sucesso!"
        return redirect(url_for('index'))
    
    return render_template('add_city.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
