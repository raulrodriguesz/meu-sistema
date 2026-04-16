from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '123456'

# =========================
# BANCO
# =========================

def criar_banco():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT,
        setor TEXT,
        tipo TEXT
    )
    ''')

    conn.commit()
    conn.close()


def criar_admin():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE usuario='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha, setor, tipo) VALUES (?, ?, ?, ?)",
            ("admin", generate_password_hash("1234"), "admin", "admin")
        )
        conn.commit()

    conn.close()


def criar_usuario_braz():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE usuario='braz'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha, setor, tipo) VALUES (?, ?, ?, ?)",
            ("braz", generate_password_hash("braz2026"), "todos", "user")
        )
        conn.commit()

    conn.close()


# EXECUTA AO INICIAR
criar_banco()
criar_admin()
criar_usuario_braz()

# =========================
# LOGIN
# =========================

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE usuario=?", (usuario,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], senha):
            session['usuario'] = user[1]
            session['setor'] = user[3]
            session['tipo'] = user[4]
            return redirect(url_for('home'))
        else:
            return render_template('erro_login.html', mensagem="Usuário ou senha inválidos")

    return render_template('login.html')


# =========================
# CONTROLE DE ACESSO
# =========================

def verificar_acesso(setor):
    if 'usuario' not in session:
        return False

    if session.get('tipo') == 'admin':
        return True

    if session.get('setor') == 'todos':
        return True

    return session.get('setor') == setor


# =========================
# HOME
# =========================

@app.route('/home')
def home():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')


# =========================
# VENDAS
# =========================

@app.route('/vendas')
def vendas():
    if not verificar_acesso('vendas'):
        return render_template('erro.html', mensagem="Sem acesso a Vendas")
    return render_template('vendas.html')


@app.route('/vendas1')
def vendas1():
    if not verificar_acesso('vendas'):
        return render_template('erro.html', mensagem="Sem acesso a Vendas")
    return render_template('vendas1.html')


# =========================
# OFICINA
# =========================

@app.route('/oficina')
def oficina():
    if not verificar_acesso('oficina'):
        return render_template('erro.html', mensagem="Sem acesso a Oficina")
    return render_template('oficina.html')


@app.route('/oficina1')
def oficina1():
    if not verificar_acesso('oficina'):
        return render_template('erro.html', mensagem="Sem acesso a Oficina")
    return render_template('oficina1.html')


@app.route('/oficina2')
def oficina2():
    if not verificar_acesso('oficina'):
        return render_template('erro.html', mensagem="Sem acesso a Oficina")
    return render_template('oficina2.html')


# =========================
# PEÇAS
# =========================

@app.route('/pecas')
def pecas():
    if not verificar_acesso('pecas'):
        return render_template('erro.html', mensagem="Sem acesso a Peças")
    return render_template('pecas.html')


# =========================
# USUÁRIOS (ADMIN)
# =========================

@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if session.get('tipo') != 'admin':
        return render_template('erro.html', mensagem="Apenas admin pode acessar")

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            cursor.execute(
                "INSERT INTO usuarios (usuario, senha, setor, tipo) VALUES (?, ?, ?, ?)",
                (
                    request.form['usuario'],
                    generate_password_hash(request.form['senha']),
                    request.form['setor'],
                    request.form['tipo']
                )
            )
            conn.commit()
        except:
            return render_template('erro.html', mensagem="Usuário já existe")

    cursor.execute("SELECT id, usuario, setor, tipo FROM usuarios")
    lista = cursor.fetchall()

    conn.close()

    return render_template('usuarios.html', usuarios=lista)


# =========================
# EXCLUIR USUÁRIO
# =========================

@app.route('/excluir_usuario/<int:id>')
def excluir_usuario(id):
    if session.get('tipo') != 'admin':
        return render_template('erro.html', mensagem="Acesso negado")

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('usuarios'))


# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# =========================
# RUN
# =========================

if __name__ == '__main__':
    app.run(debug=True)