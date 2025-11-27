from flask import Flask, render_template, request, redirect, url_for, flash, session, get_flashed_messages

app = Flask(__name__)
app.secret_key = 'UNA_LLAVE_MUY_LARGA_Y_SECRETA_J_A'
API="https://www.themealdb.com/api/json/v1/1/search.php?s="

import requests

from flask_mysqldb import MySQL

from werkzeug.security import generate_password_hash,check_password_hash

import re

app.config['MYSQL_HOST']='localhost'

app.config['MYSQL_USER']='root'

app.config['MYSQL_PASSWORD']=''

app.config['MYSQL_DB']='usuarios'

mysql= MySQL(app)

def crear_tabla():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario(
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100),
            correo VARCHAR(255) UNIQUE NOT NULL, 
            password VARCHAR(255) NOT NULL)''')
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error creando la tabla: {e}")
        
def obtener_usuario_por_email(correo):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, nombre, correo, password FROM usuario WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()
        cursor.close()
        return usuario
    except Exception as e:
        print(f"Error al buscar usuario: {e}")
        return None


def registrar_usuario(nombre, apellido, email, password_hash): 
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO usuario (nombre, apellido, correo, password) VALUES (%s, %s, %s, %s)",
            (nombre, apellido, email, password_hash) 
        )
        mysql.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error al registrar usuario: {e}") 
        flash('El correo electrónico ya está registrado o hay un error en la base de datos.', 'danger')
        return False

@app.route('/')
def inicio():
    return render_template('inicio.html')


@app.route('/registro', methods=['GET','POST'])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido") 
        email = request.form.get("email") 
        password = request.form.get("password")
        if not nombre or not apellido or not email or not password:
            flash('Por favor, rellena todos los campos requeridos.', 'danger')
            return redirect(url_for("registro"))
        password_hash = generate_password_hash(password)
        if registrar_usuario(nombre, apellido, email, password_hash): 
            flash('Registro exitoso. ¡Inicia sesión!', 'success')
            return redirect(url_for("login"))
        else:
            return redirect(url_for("registro"))
    return render_template('registro.html')
    
@app.route('/login', methods=['GET','POST'])
def login():
    if 'usuario_nombre' in session:
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        correo = request.form.get("correo") 
        password = request.form.get("password")

        if not correo or not password:
            flash("Ingresa correo y contraseña.", "warning")
            return redirect(url_for('login'))

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, nombre, correo, password FROM usuario WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()
        cursor.close()

        if usuario is None:
            flash("El usuario no ha sido encontrado.", "danger")
            return redirect(url_for("login"))

        stored_password_hash = usuario[3]

        if check_password_hash(stored_password_hash, password):
            session["usuario_id"] = usuario[0]
            session["usuario_nombre"] = usuario[1]
            session["usuario_email"] = usuario[2]   # ← AQUÍ LO AGREGAS
            flash(f"¡Bienvenido, {usuario[1]}!", "success")
            return redirect(url_for("inicio"))
        else:
            flash("Contraseña incorrecta.", "danger")
            return redirect(url_for("login"))

    return render_template('login.html')



@app.route('/close')
def close():
    session.pop('usuario_id', None)
    session.pop('usuario_nombre', None)
    session.pop('usuario_email', None)
    session.pop('calculo_imc', None)
    session.pop('calculo_clasificacion', None)
    session.pop('calculo_tmb', None)
    session.pop('calculo_get', None)
    session.pop('calculo_pci', None)
    session.pop('macro_prot', None)
    session.pop('macro_carbs', None)
    session.pop('macro_grasas', None)
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for('inicio'))

@app.route('/descubrete', methods=['GET','POST'])
def descubrete():
    if 'usuario_id' not in session:
        flash('Inicia sesion para poder acceder', 'warning')
        return redirect(url_for('login'))
    usuario_nombre = session.get('usuario_nombre') 
    if request.method == 'POST':
        try:
            peso = float(request.form['peso'])
            estatura_metro = float(request.form['estatura'])
            edad = int(request.form['edad'])
            genero = request.form['genero']
            actividad = float(request.form['actividad'])
            imc = peso / (estatura_metro ** 2)
            estatura_cm = estatura_metro * 100
            if imc < 18.5:
                clasificacion = "Bajo peso"
            elif imc < 25:
                clasificacion = "Normal"
            elif imc < 30:
                clasificacion = "Sobrepeso"
            else:
                clasificacion = "Obesidad"
            if genero == "masculino":
                tmb = (10 * peso) + (6.25 * estatura_cm) - (5 * edad) + 5
            else:
                tmb = (10 * peso) + (6.25 * estatura_cm) - (5 * edad) - 161
            get = tmb * actividad
            session['calculo_imc'] = round(imc, 2)
            session['calculo_clasificacion'] = clasificacion
            session['calculo_tmb'] = round(tmb, 2)
            session['calculo_get'] = round(get, 2)
            estatura_pulgadas = estatura_metro * 39.37
            if genero == "masculino":
                pci = 50 + 2.3 * (estatura_pulgadas - 60)
            else:
                pci = 45.5 + 2.3 * (estatura_pulgadas - 60)
            session['calculo_pci'] = round(pci, 2)
            proteinas = get * 0.25 / 4
            carbs = get * 0.50 / 4
            grasas = get * 0.25 / 9
            session['macro_prot'] = round(proteinas, 1)
            session['macro_carbs'] = round(carbs, 1)
            session['macro_grasas'] = round(grasas, 1)
            return redirect(url_for('resultado'))
        except ValueError:
            flash('Ingresar números válidos para peso, estatura y actividad.', 'danger')
            return redirect(url_for('descubrete'))
    return render_template('descubrete.html', usuario=usuario_nombre)

@app.route('/resultado')
def resultado():
    if 'calculo_imc' not in session:
        flash('No se encontraron resultados. Por favor, realiza un nuevo cálculo.', 'warning')
        return redirect(url_for('descubrete'))

    usuario_nombre = session.get('usuario_nombre') 
    
    imc = session.get('calculo_imc')
    clasificacion = session.get('calculo_clasificacion')
    tmb = session.get('calculo_tmb')
    get = session.get('calculo_get')

    pci = session.get('calculo_pci')
    prot = session.get('macro_prot')
    carbs = session.get('macro_carbs')
    grasas = session.get('macro_grasas')

    return render_template(
        'resultado.html',
        imc=imc,
        clasificacion=clasificacion,
        tmb=tmb,
        get=get,
        usuario=usuario_nombre,
        pci=pci,
        prot=prot,
        carbs=carbs,
        grasas=grasas
    )

@app.route('/perfil')
def perfil():
    if 'usuario_id' not in session:
        return redirect('/login')

    return render_template(
        'perfil.html',
        usuario_nombre=session.get('usuario_nombre'),
        usuario_email=session.get('usuario_email')
    )


@app.route('/guia')
def guia():
    return render_template('guia.html')

@app.route('/importancia')
def importancia():
    return render_template('importancia.html')

@app.route('/mito')
def mito():
    return render_template('mito.html')

@app.route('/etiqueta')
def etiqueta():
    return render_template('etiqueta.html')

@app.route('/videos')
def videos():
    if 'usuario_id' not in session:
        flash('Inicia sesion para poder acceder', 'warning')
        return redirect(url_for('login'))
    usuario_nombre = session.get('usuario_nombre') 
    return render_template('videos.html')

@app.route('/edu')
def articulo():
    return render_template('articulos.html')

@app.route('/recetas')
def recetas():
    if 'usuario_id' not in session: 
        flash('Inicia sesion para poder acceder', 'warning')
        return redirect(url_for('login'))
    usuario_nombre = session.get('usuario_nombre') 
    return render_template('recetas.html', meal=None, messages= get_flashed_messages(with_categories=True))

@app.route('/search', methods=['POST'])
def search_api_comida():
    comida_name=request.form.get('query','').strip().lower()
    if not comida_name:
        flash('Por favor,ingresa un nombre de comida o receta','error')
        return redirect(url_for('recetas'))
    try:
        resp = requests.get(f"{API}{comida_name}")
        if resp.status_code == 200:   
            comida_data = resp.json()
            meals= comida_data.get('meals')            
            if meals:
                return render_template('recetas.html',meal = meals[0], search_query=comida_name)
            else:
                flash(f'Receta "{comida_name}" no encontrada','error')
                return redirect(url_for('recetas'))
        else:
            flash(f'Error al buscar la receta: código de estado {resp.status_code}','error')
            return redirect(url_for('recetas'))   
    except requests.exceptions.RequestException as e:
        flash('Error al buscar la receta: problema de conexión.','error')
    return redirect (url_for('recetas'))

if __name__ == '__main__':
    with app.app_context():
        crear_tabla()
    app.run(debug=True)
#Poner que cuando inicie sesion se vea todo y cuando no este registrado no me muestre la calculadora ni el plan nutrietico, solo el registro y los articulos de ayuda.
#Hay que poner las alergias y eso debe ser guardada en base de datos, para el lunes en un diccionario de datos,articulos con etiquetas
#Buscar una o dos dietas de moda y poner mitos y verdades, guia sobre macronutrientes, importancia de la hidratacion y fibra
#un plan d ejercicio descargable 1 o dos y gratuitos
#Banco de recetas saludables
#Diferentes tipos de calculadoras corporal,basal,gasto calorico, en base a los datos ingresados acceso a todos
