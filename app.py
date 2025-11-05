from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)
@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/descubrete')
def descubrete():
    return render_template('descubrete.html')

@app.route('/recetas')
def recetas():
    return render_template('recetas.html')

if __name__ == '__main__':
    app.run(debug=True)