from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'spbYO0JJOPUFLUikKYbKrpS5w3KUEnab5KcYDdYb'
db = sqlite3.connect('data.db', check_same_thread=False)

# Rutas
@app.route('/', methods=['GET']) # / significa la ruta raiz
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST']) 
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    password = request.form.get('password')

    usuario = db.execute("""select * from usuarios where 
        email = ? and password = ?""", (email, password,)).fetchone()
    
    if usuario is None:
        flash('Las credenciales no son válidas', 'error')
        return redirect(request.url)

    session['usuario'] = usuario

    return redirect(url_for('index'))

@app.route('/logout') 
def logout():
    session.clear()

    return redirect(url_for('login'))

@app.route('/saludo/<nombre>/<int:edad>') # Nombre
def saludar(nombre, edad):
    numeros = [1,2,3,4,5,6,7,8,9]
    return render_template('saludo.html', name=nombre, age=edad, numbers=numeros)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    #Obteniendo formulario de contacto
    if request.method == 'GET':
        return render_template('contacto.html')
    
    #Guardando la información de contacto
    nombres = request.form.get('nombres')
    email = request.form.get('email')
    celular = request.form.get('celular')
    observacion = request.form.get('observacion')

    return 'Guardando información ' + observacion
    
@app.route('/sumar')
def sumar():
    resultado = 2+2
    return 'la suma de 2+2=' + str(resultado)


@app.route('/usuarios')
def usuarios():
    if not 'usuario' in session:
        return redirect(url_for('login'))

    id = str(session['usuario'][0])
    usuario = db.execute('select * from usuarios where id = ?', (id,)).fetchone()
        
    return render_template('usuarios/editar.html', usuario=usuario)

@app.route('/productos')
def productos():
    if not 'usuario' in session:
        return redirect(url_for('login'))
    ids = str(session['usuario'][0])
    productos = db.execute('select codigo,nombre,cantidad,idUsuario,NombreCategoria from producto,categoria where idUsuario = ?  and CodigoCategoria = catCodigo', (ids,))
    productos = productos.fetchall()

    return render_template('productos/listar.html', productos=productos)

@app.route('/categorias')
def categorias():
    if not 'usuario' in session:
        return redirect(url_for('login'))
    categorias = db.execute('select * from categoria')
    categorias = categorias.fetchall()
    return render_template('categorias/lista.html', categorias = categorias)

@app.route('/categorias/crear',methods=['GET', 'POST'])
def crear_categoria():
    if request.method == 'GET':
        return render_template('categorias/crear.html')
    
    nombre = request.form.get('nombre')
    codigo = request.form.get('codigo')
    if(nombre == ""):
        flash('El campo nombres es requerido', 'error')
        return redirect(request.url)

    try:
        cursor = db.cursor()
        cursor.execute("""insert into categoria(
                CodigoCategoria,nombreCategoria
            )values (?,?)
        """, (codigo,nombre,))

        db.commit()
    except:
        flash('No se ha podido guardar la categoria', 'error')
        return redirect(url_for('categorias'))

    flash('Categoria creado correctamente', 'success')

    return redirect(url_for('categorias'))

@app.route('/usuarios/crear', methods=['GET', 'POST'])
def crear_usuarios():
    if request.method == 'GET':
        return render_template('usuarios/crear.html')
    
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    email = request.form.get('email')
    password = request.form.get('password')

    #Validando que el correo no este en uso
    usuario = db.execute('select * from usuarios where email = ?', (email,)).fetchall()

    if(nombres == ""):
        flash('El campo nombres es requerido', 'error')
        return redirect(request.url)

    if(len(usuario) > 0):
        flash('Ya existe un usuario con este email', 'error')
        return redirect(request.url)

    try:
        cursor = db.cursor()
        cursor.execute("""insert into usuarios(
                nombres,
                apellidos,
                email,
                password
            )values (?,?,?,?)
        """, (nombres, apellidos, email, password,))

        db.commit()
    except:
        flash('No se ha podido guardar el usuario', 'error')
        return redirect(url_for('usuarios'))

    flash('Usuario creado correctamente', 'success')

    return redirect(url_for('usuarios'))

@app.route('/usuarios/crearProducto', methods=['GET','POST'])
def crear_producto():
    if request.method == 'GET':
        categorias = db.execute('select * from categoria')
        categorias = categorias.fetchall()
        return render_template('usuarios/crearProducto.html', categorias = categorias)
    
    nombre = request.form.get('nombre')
    cantidad = request.form.get('cantidad')
    codigo = request.form.get('codigo')
    id = str(session['usuario'][0])
    categoria = request.form.get('categoria')



    
    if(nombre == ""):
        flash('El campo nombre es requerido', 'error')
        return redirect(request.url)

    try:
        cursor = db.cursor()
        cursor.execute("""insert into producto(
                codigo,
                nombre,
                cantidad,
                IdUsuario,
                catCodigo
            )values (?,?,?,?,?)
        """, (codigo, nombre, cantidad, id+"",categoria,))

        db.commit()
    except:
        flash('No se ha podido guardar el producto', 'error')
        return redirect(url_for('productos'))

    flash('Producto creado correctamente', 'success')
    return redirect(url_for('productos'))


@app.route('/categorias/editar/<int:id>', methods=['GET', 'POST'])
def editar_categoria(id):
    if request.method == 'GET':
        categoria = db.execute('select * from categoria where CodigoCategoria = ?', (id,)).fetchone()
        return render_template('categorias/editar.html', categoria = categoria)
    
    nombre = request.form.get('nombre')

    try:
        cursor = db.cursor()
        cursor.execute("""update categoria set nombreCategoria = ?
        where codigoCategoria = ? 
        """, (nombre, id,))

        db.commit()

    except:
        flash('No se ha podido editar la categoria', 'error')
        return redirect(url_for('categorias'))

    flash('Categoria editado correctamente', 'success')

    return redirect(url_for('categorias'))

@app.route('/usuarios/editar', methods=['GET', 'POST'])
def editar_usuario():
    if request.method == 'GET':
        id = str(session['usuario'][0])
        usuario = db.execute('select * from usuarios where id = ?', (id,)).fetchone()
        return render_template('usuarios/editar.html', usuario=usuario)

    id2 = str(session['usuario'][0])
    usuario = db.execute('select * from usuarios where id = ?', (id2,)).fetchone()
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    email = request.form.get('email')
    password = request.form.get('password')

    if password == '':
        password = usuario[4]
    
    try:
        cursor = db.cursor()
        cursor.execute("""update usuarios set nombres = ?,
            apellidos = ?, email = ?, password = ? where id = ? 
        """, (nombres, apellidos, email, password,id2,))

        db.commit()
    except:
        flash('No se ha podido editar el usuario', 'error')
        return redirect(url_for('usuario'))

    flash('Usuario editado correctamente', 'success')

    return redirect(url_for('index'))


@app.route('/usuarios/eliminar/<int:id>', methods= ['GET'])
def eliminar_usuario(id):
    if request.method == 'GET':
        try:
            cursor = db.cursor()
            cursor.execute("""delete from usuarios where id = ? 
            """, (id,))
            db.commit()
        except:
            flash('No se ha podido eliminar el usuario', 'error')
            return redirect(url_for('usuario'))

        flash('Usuario eliminado correctamente', 'success')

        return redirect(url_for('usuarios'))

@app.route('/productos/eliminar/<string:id>', methods=['GET'])
def eliminar_producto(id):
    if request.method == 'GET':
        try:
            cursor = db.cursor()
            cursor.execute("""delete from producto  where codigo = ? 
            """, (id,))

            db.commit()
        except:
            flash('No se ha podido eliminar el producto', 'error')
            return redirect(url_for('productos'))

        flash('Producto eliminado correctamente', 'success')

        return redirect(url_for('productos'))


@app.route('/productos/editar/<string:id>', methods=['GET','POST'])
def editar_producto(id):
    if request.method == 'GET':
        producto = db.execute('select * from producto where codigo = ?', (id,)).fetchone()
        
        return render_template('productos/editar.html', producto=producto)

    cantidad = request.form.get('cantidad')
    nombre = request.form.get('nombre')

    try:
        cursor = db.cursor()
        cursor.execute("""update producto set nombre = ?,
            cantidad = ? where codigo = ? 
        """, (nombre, cantidad, id,))

        db.commit()
    except:
        flash('No se ha podido editar el producto', 'error')
        return redirect(url_for('productos'))

    flash('Producto editado correctamente', 'success')

    return redirect(url_for('productos'))

@app.route('/resources/<filename>')
def uploaded_file(filename):
       filename = 'http://127.0.0.1:5000/resources/' + filename
       return render_template('template.html', filename = filename)
app.run(debug=True)