import flet as ft
from datetime import datetime
from db_config import criar_conexao, criar_banco_dados

class Produto:
    def __init__(self, id=None, nome="", preco=0.0, codigo="", categoria="", quantidade=0, data_cadastro=None):
        self.id = id
        self.nome = nome
        self.preco = preco
        self.codigo = codigo
        self.categoria = categoria
        self.quantidade = quantidade
        self.data_cadastro = data_cadastro or datetime.now()

    def __str__(self):
        return f'Nome: {self.nome} | Preço: R${self.preco:.2f} | Código: {self.codigo} | Categoria: {self.categoria} | Quantidade: {self.quantidade}'

def main(page: ft.Page):
    page.title = 'Sistema de Gestão de Estoque - Farmácia'
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # Criar banco de dados e tabelas
    criar_banco_dados()

    # Campos do formulário
    campo_nome = ft.TextField(label='Nome do produto', width=300)
    campo_codigo = ft.TextField(label='Código do produto', width=300)
    campo_categoria = ft.TextField(label='Categoria do produto', width=300)
    campo_quantidade = ft.TextField(label='Quantidade', width=300)
    campo_preco = ft.TextField(label='Preço', width=300)

    # Campos de busca
    campo_busca = ft.TextField(label='Buscar produto', width=300)
    resultado_busca = ft.Column(scroll=ft.ScrollMode.AUTO)

    # Lista de produtos
    lista_produtos = ft.Column(scroll=ft.ScrollMode.AUTO)

    def carregar_produtos():
        conexao = None
        cursor = None
        try:
            conexao = criar_conexao()
            if conexao:
                cursor = conexao.cursor(dictionary=True)
                cursor.execute("SELECT * FROM produtos")
                produtos = cursor.fetchall()
                return [Produto(**produto) for produto in produtos]
            return []
        except Exception as e:
            print(f"Erro ao carregar produtos: {e}")
            return []
        finally:
            try:
                cursor.close()
            except:
                pass
            try:
                if conexao is not None and conexao.is_connected():
                    conexao.close()
            except:
                pass

    def cadastrar_produto(e):
        conexao = None
        cursor = None
        try:
            conexao = criar_conexao()
            if conexao:
                cursor = conexao.cursor()
                sql = """INSERT INTO produtos (nome, preco, codigo, categoria, quantidade)
                        VALUES (%s, %s, %s, %s, %s)"""
                valores = (
                    campo_nome.value,
                    float(campo_preco.value),
                    campo_codigo.value,
                    campo_categoria.value,
                    int(campo_quantidade.value)
                )
                cursor.execute(sql, valores)
                conexao.commit()
                page.snack_bar = ft.SnackBar(content=ft.Text("Produto cadastrado com sucesso!"))
                page.snack_bar.open = True
                page.update()
                limpar_campos()
                atualizar_lista_produtos()
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text("Erro ao conectar ao banco de dados!"))
                page.snack_bar.open = True
                page.update()
        except Exception as erro:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Erro ao cadastrar: {str(erro)}"))
            page.snack_bar.open = True
            page.update()
        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None and conexao.is_connected():
                conexao.close()

    def limpar_campos():
        campo_nome.value = ""
        campo_codigo.value = ""
        campo_categoria.value = ""
        campo_quantidade.value = ""
        campo_preco.value = ""
        page.update()

    def atualizar_lista_produtos():
        lista_produtos.controls.clear()
        produtos = carregar_produtos()
        for produto in produtos:
            lista_produtos.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(str(produto)),
                            ft.Row([
                                ft.ElevatedButton("Adicionar", on_click=lambda e, p=produto: atualizar_estoque(e, p, True)),
                                ft.ElevatedButton("Remover", on_click=lambda e, p=produto: atualizar_estoque(e, p, False)),
                            ])
                        ]),
                        padding=10
                    )
                )
            )
        page.update()

    def atualizar_estoque(e, produto, adicionar):
        conexao = None
        cursor = None
        try:
            quantidade = int(campo_quantidade.value)
            conexao = criar_conexao()
            if conexao:
                cursor = conexao.cursor()
                if adicionar:
                    sql = "UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s"
                else:
                    if produto.quantidade >= quantidade:
                        sql = "UPDATE produtos SET quantidade = quantidade - %s WHERE id = %s"
                    else:
                        page.show_snack_bar(ft.SnackBar(content=ft.Text("Quantidade insuficiente em estoque!")))
                        return
                
                cursor.execute(sql, (quantidade, produto.id))
                conexao.commit()
                atualizar_lista_produtos()
                verificar_estoque_baixo()
                campo_quantidade.value = ""
                page.update()
        except Exception as erro:
            page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Erro ao atualizar estoque: {str(erro)}")))
        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None and conexao.is_connected():
                conexao.close()

    def buscar_produto(e):
        conexao = None
        cursor = None
        termo = campo_busca.value.lower()
        resultado_busca.controls.clear()
        
        try:
            conexao = criar_conexao()
            if conexao:
                cursor = conexao.cursor(dictionary=True)
                sql = """SELECT * FROM produtos 
                        WHERE LOWER(nome) LIKE %s 
                        OR LOWER(codigo) LIKE %s 
                        OR LOWER(categoria) LIKE %s"""
                termo_busca = f"%{termo}%"
                cursor.execute(sql, (termo_busca, termo_busca, termo_busca))
                produtos = cursor.fetchall()
                
                for produto in produtos:
                    p = Produto(**produto)
                    resultado_busca.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Text(str(p)),
                                padding=10
                            )
                        )
                    )
                page.update()
        except Exception as erro:
            print(f"Erro na busca: {erro}")
        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None and conexao.is_connected():
                conexao.close()

    def verificar_estoque_baixo():
        conexao = None
        cursor = None
        try:
            conexao = criar_conexao()
            if conexao:
                cursor = conexao.cursor(dictionary=True)
                cursor.execute("SELECT * FROM produtos WHERE quantidade < 10")
                produtos_baixo = cursor.fetchall()
                
                for produto in produtos_baixo:
                    p = Produto(**produto)
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"ALERTA: Estoque baixo de {p.nome}! Restam apenas {p.quantidade} unidades.")
                    )
                    page.snack_bar.open = True
                    page.update()
        except Exception as erro:
            print(f"Erro ao verificar estoque baixo: {erro}")
        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None and conexao.is_connected():
                conexao.close()

    # Abas do sistema
    tela_cadastro = ft.Container(
        content=ft.Column([
            ft.Text("Cadastro de Produtos", size=20, weight=ft.FontWeight.BOLD),
            campo_nome,
            campo_codigo,
            campo_categoria,
            campo_quantidade,
            campo_preco,
            ft.ElevatedButton("Cadastrar", on_click=cadastrar_produto)
        ])
    )

    tela_consulta = ft.Container(
        content=ft.Column([
            ft.Text("Consulta de Produtos", size=20, weight=ft.FontWeight.BOLD),
            campo_busca,
            ft.ElevatedButton("Buscar", on_click=buscar_produto),
            resultado_busca
        ])
    )

    tela_estoque = ft.Container(
        content=ft.Column([
            ft.Text("Gestão de Estoque", size=20, weight=ft.FontWeight.BOLD),
            lista_produtos
        ])
    )

    # Navegação por abas
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Cadastro",
                content=tela_cadastro
            ),
            ft.Tab(
                text="Consulta",
                content=tela_consulta
            ),
            ft.Tab(
                text="Estoque",
                content=tela_estoque
            ),
        ],
        expand=1
    )

    # Carregar produtos iniciais
    atualizar_lista_produtos()

    page.add(tabs)

ft.app(target=main)