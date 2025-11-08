from flask import Flask, render_template,request, redirect, url_for, flash

app = Flask(__name__)

USERS = {
    'nombre' : 'anette',
    'apellido' : 'leonardo',
    'email' : 'anette@gmail',
    'password' :'anet123'
},{
    'nombre' : 'jazmin',
    'apellido' :'regis',
    'email' : 'jaz@gmail.com',
    'password' : 'jaz123'
}

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/registro')
def registro():
    error = None
    if request.method == "POST":
        nombre = request.form.get('nombre') 
        apellido = request.form.get('apellido')
        email = request.form.get('email') 
        peso = request.form.get('peso')
        estatura = request.form.get('estatura')
        edad = request.form.get('edad')
        preferencia = request.form.get('preferencia')
        sexo = request.form.get('sexo')
        fisica = request.form.get('fisica')
        objetivo = request.form.get('objetivo')
        cocina = request.form.get('cocina')
        password = request.form.get('password') 
        confirmPassword = request.form.get('confirmaContraseña') 
        if not all([nombre, apellido, email, peso, estatura, edad, preferencia, sexo, fisica, objetivo, cocina, password, confirmPassword]):
            error = 'Todos los campos son obligatorios.'
        if error is None:
                    error = f'El correo electrónico "{email}" ya está registrado.'
        if error is None and password != confirmPassword:
            error = "La contraseña no coincide" 
        if error is not None:
            flash(error, 'danger')
            return redirect(url_for('inicio.html')) 
        else:
            new_user = {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'peso': peso,
                'estatura' : estatura,
                'edad' : edad,
                'preferecia' : preferencia,
                'sexo' : sexo,
                'fisica' : fisica,
                'objetivo' : objetivo,
                'cocina' : cocina,
                'password': password 
                
            }
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))

    return render_template('registro.html', no_menu=True)

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