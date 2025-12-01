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
            session["usuario_email"] = usuario[2]  
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


@app.route('/perfil')
def perfil():
    if 'usuario_id' not in session:
        return redirect('/login')

    return render_template(
        'perfil.html',
        usuario_nombre=session.get('usuario_nombre'),
        usuario_email=session.get('usuario_email')
    )

@app.route('/banco')
def banco():
    return render_template('banco.html')

@app.route('/guia')
def guia():
    return render_template('guia.html')

@app.route('/imc')
def imc():
    return render_template('calimc.html')

@app.route('/tmb')
def tmb():
    return render_template('caltmb.html')

@app.route('/gct')
def gct():
    return render_template('calgct.html')

@app.route('/pci')
def pci():
    return render_template('calpci.html')

@app.route('/mac')
def mac():
    return render_template('calmac.html')

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
    return render_template('videos.html')

@app.route('/edu')
def articulo():
    return render_template('articulos.html')

@app.route('/mealpreap')
def mealpreap():
    return render_template('mealpreap.html')

@app.route('/principiantes')
def principiantes():
    return render_template('principiantes.html')

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
