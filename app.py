from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)

app.secret_key = 'UNA_LLAVE_MUY_LARGA_Y_SECRETA_J_A'

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        session['usuario'] = nombre
        session['logged_in'] = True
        flash(f'¡Registro exitoso, {nombre}! Bienvenido a VitaPlena.', 'success')
        return redirect(url_for('descubrete'))
    return render_template('registro.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        nombre = "Usuario" 
        session['usuario'] = nombre
        session['logged_in'] = True
        flash(f'¡Hola de nuevo, {nombre}! Sesión iniciada.', 'info')
        return redirect(url_for('descubrete')) 
    return render_template('login.html')


@app.route('/close')
def close():
    session.pop('usuario', None)
    session.pop('logged_in', None)
    flash('Tu sesion ha sido cerrada exitosamente.', 'info')
    return redirect(url_for('inicio'))


@app.route('/descubrete', methods=['GET', 'POST'])
def descubrete():
    if not session.get('logged_in'):
        flash('Inicia sesion para poder acceder', 'warning')
        return redirect(url_for('login')) 
    usuario = session.get('usuario') 
    if request.method == 'POST':
        try:
            peso = float(request.form['peso'])
            estatura = float(request.form['estatura'])
            edad = int(request.form['edad'])
            genero = request.form['genero']
            actividad = float(request.form['actividad'])
            imc = peso / (estatura ** 2) 
            if imc < 18.5:
                clasificacion = "Bajo peso"
            elif imc < 25:
                clasificacion = "Normal"
            elif imc < 30:
                clasificacion = "Sobrepeso"
            else:
                clasificacion = "Obesidad"
            if genero == "masculino":
                tmb = (10 * peso) + (6.25 * (estatura * 100)) - (5 * edad) + 5
            else:
                tmb = (10 * peso) + (6.25 * (estatura * 100)) - (5 * edad) - 161
            get = tmb * actividad
            return render_template(
                'resultado.html',
                imc=round(imc, 2),
                clasificacion=clasificacion,
                tmb=round(tmb, 2),
                get=round(get, 2),
                usuario=usuario
            )
        except ValueError:
            flash('Ingresar números válidos para peso, estatura y actividad.', 'danger')
            return redirect(url_for('descubrete'))
    return render_template('descubrete.html', usuario=usuario)



@app.route('/resultado', methods=['GET', 'POST'])
def resultado():
    return render_template('resultado.html')

@app.route('/perfil')
def perfil():
    return render_template('perfil.html')

@app.route('/recetas')
def recetas():
    return render_template('recetas.html')

@app.route('/videos')
def videos():
    return render_template('videos.html')

if __name__ == '__main__':
    app.run(debug=True)

#Hay que poner las alergias y eso debe ser guardada en base de datos, para el lunes en un diccionario de datos,articulos con etiquetas
#Buscar una o dos dietas de moda y poner mitos y verdades, guia sobre macronutrientes, importancia de la hidratacion y fibra
#un plan d ejercicio descargable 1 o dos y gratuitos
#Banco de recetas saludables
#Diferentes tipos de calculadoras corporal,basal,gasto calorico, en base a los datos ingresados acceso a todos
