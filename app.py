from flask import Flask, render_template, url_for, request, redirect

USUARIOS_REGISTRADO:[]

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

@app.route('/videos')
def videos():
    return render_template('videos.html')

#Hay que poner las alergias y eso debe ser guardada en base de datos, para el lunes en un diccionario de datos,articulos con etiquetas
#Buscar una o dos dietas de moda y poner mitos y verdades, guia sobre macronutrientes, importancia de la hidratacion y fibra
#un plan d ejercicio descargable 1 o dos y gratuitos
#Banco de recetas saludables
#Diferentes tipos de calculadoras corporal,basal,gasto calorico, en base a los datos ingresados acceso a todos
if __name__ == '__main__':
    app.run(debug=True)