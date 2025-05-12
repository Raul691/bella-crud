import mysql.connector 
from mysql.connector import Error
def criar_conexao():
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='farmacia_db',
            auth_plugin='mysql_native_password'
        )
        return conexao
    except Error as erro:
        print(f"Erro ao conectar ao MySQL: {erro}")
        return None

def criar_banco_dados():
    try:
        # Create connection with MySQL server
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            auth_plugin='mysql_native_password'  # Add this line
        )
        
        if conexao.is_connected():
            cursor = conexao.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS farmacia_db")
            cursor.execute("USE farmacia_db")
            
            # Create products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    preco DECIMAL(10,2) NOT NULL,
                    codigo VARCHAR(50) NOT NULL UNIQUE,
                    categoria VARCHAR(50) NOT NULL,
                    quantidade INT NOT NULL,
                    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conexao.commit()
            print("Banco de dados e tabelas criados com sucesso!")
            return conexao
            
    except Error as e:
        print(f"Erro ao criar banco de dados: {e}")
        return None
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()

