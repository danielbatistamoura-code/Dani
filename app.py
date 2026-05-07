import sqlite3
import hashlib

# Conectar ao banco de dados
conn = sqlite3.connect("palmeiras_loja.db")
cursor = conn.cursor()

# Criar tabelas
cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    estoque INTEGER NOT NULL,
    time TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER,
    id_produto INTEGER,
    quantidade INTEGER,
    total REAL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id),
    FOREIGN KEY (id_produto) REFERENCES produtos(id)
)
''')
conn.commit()

# Função para hash de senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Cadastro de cliente
def cadastrar_cliente():
    nome = input("Nome: ")
    email = input("Email: ")
    senha = input("Senha: ")
    senha_hash = hash_senha(senha)
    try:
        cursor.execute('INSERT INTO clientes (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha_hash))
        conn.commit()
        print("Cliente cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("Erro: Email já cadastrado!")

# Login de cliente
def login():
    email = input("Email: ")
    senha = input("Senha: ")
    senha_hash = hash_senha(senha)
    cursor.execute('SELECT * FROM clientes WHERE email = ? AND senha = ?', (email, senha_hash))
    cliente = cursor.fetchone()
    if cliente:
        print(f"Bem-vindo(a), {cliente[1]}!")
        return cliente[0]  # Retorna o id do cliente
    else:
        print("Email ou senha incorretos!")
        return None

# Cadastro de produto
def cadastrar_produto():
    nome = input("Nome do produto: ")
    preco = float(input("Preço: "))
    estoque = int(input("Estoque: "))
    time = input("Time (ex: Palmeiras): ")
    cursor.execute('INSERT INTO produtos (nome, preco, estoque, time) VALUES (?, ?, ?, ?)', (nome, preco, estoque, time))
    conn.commit()
    print("Produto cadastrado com sucesso!")

# Pré-cadastrar produtos do Palmeiras
def produtos_palmeiras():
    produtos = [
        ("Camisa Oficial Palmeiras", 299.90, 10, "Palmeiras"),
        ("Bola Oficial Palmeiras", 149.90, 20, "Palmeiras"),
        ("Boné Palmeiras", 79.90, 15, "Palmeiras"),
        ("Cachecol Palmeiras", 49.90, 25, "Palmeiras")
    ]
    for p in produtos:
        cursor.execute('INSERT INTO produtos (nome, preco, estoque, time) VALUES (?, ?, ?, ?)', p)
    conn.commit()

# Listar produtos
def listar_produtos():
    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    print("=== Produtos Disponíveis ===")
    for p in produtos:
        print(f"ID: {p[0]}, Nome: {p[1]}, Preço: {p[2]}, Estoque: {p[3]}, Time: {p[4]}")

# Registrar venda
def registrar_venda(id_cliente):
    listar_produtos()
    id_produto = int(input("ID do produto: "))
    quantidade = int(input("Quantidade: "))
    cursor.execute('SELECT preco, estoque FROM produtos WHERE id = ?', (id_produto,))
    produto = cursor.fetchone()
    if not produto:
        print("Produto não encontrado!")
        return
    preco, estoque = produto
    if quantidade > estoque:
        print("Quantidade insuficiente em estoque!")
        return
    total = preco * quantidade
    cursor.execute('INSERT INTO vendas (id_cliente, id_produto, quantidade, total) VALUES (?, ?, ?, ?)',
                   (id_cliente, id_produto, quantidade, total))
    cursor.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (quantidade, id_produto))
    conn.commit()
    print(f"Venda registrada! Total: R${total:.2f}")

# Listar vendas de um cliente
def listar_vendas(id_cliente):
    cursor.execute('''
        SELECT v.id, p.nome, v.quantidade, v.total
        FROM vendas v
        JOIN produtos p ON v.id_produto = p.id
        WHERE v.id_cliente = ?
    ''', (id_cliente,))
    vendas = cursor.fetchall()
    print("=== Minhas Vendas ===")
    for v in vendas:
        print(f"ID: {v[0]}, Produto: {v[1]}, Quantidade: {v[2]}, Total: R${v[3]:.2f}")

# Menu do cliente
def menu_cliente(id_cliente):
    while True:
        print("\n=== Menu Cliente ===")
        print("1. Listar Produtos")
        print("2. Registrar Venda")
        print("3. Minhas Vendas")
        print("4. Cadastrar Produto (admin)")
        print("5. Sair")
        opc = input("Escolha uma opção: ")
        if opc == '1':
            listar_produtos()
        elif opc == '2':
            registrar_venda(id_cliente)
        elif opc == '3':
            listar_vendas(id_cliente)
        elif opc == '4':
            cadastrar_produto()
        elif opc == '5':
            break
        else:
            print("Opção inválida!")

# Menu principal
def menu_principal():
    produtos_palmeiras()  # Pré-cadastrar produtos do Palmeiras
    while True:
        print("\n=== Sistema Loja Palmeiras ===")
        print("1. Cadastrar Cliente")
        print("2. Login")
        print("3. Sair")
        opc = input("Escolha uma opção: ")
        if opc == '1':
            cadastrar_cliente()
        elif opc == '2':
            id_cliente = login()
            if id_cliente:
                menu_cliente(id_cliente)
        elif opc == '3':
            print("Saindo...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    menu_principal()
    conn.close()