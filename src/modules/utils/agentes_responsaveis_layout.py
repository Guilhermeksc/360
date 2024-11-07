from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QComboBox, QGroupBox
from PyQt6.QtCore import Qt
import sqlite3
import pandas as pd

def create_combo_box(current_text, items, fixed_width, fixed_height):
    combo_box = QComboBox()
    combo_box.addItems(items)
    combo_box.setFixedWidth(fixed_width)
    combo_box.setFixedHeight(fixed_height)
    combo_box.setCurrentText(current_text)
    
    # Aplica o estilo para o fundo branco e cursor de mão ao passar o mouse
    combo_box.setStyleSheet("""
        QComboBox {
            padding: 5px;
        }
        QComboBox:hover {
            background-color: #181928; 
        }
        QComboBox QAbstractItemView { 
            background-color: #181928; 
        }
    """)
    
    # Define o cursor de mão para o combo box e sua lista de opções
    combo_box.setCursor(Qt.CursorShape.PointingHandCursor)
    combo_box.view().setCursor(Qt.CursorShape.PointingHandCursor)
    
    return combo_box


def carregar_agentes_responsaveis(database_path, combo_mapping):
    try:
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='controle_agentes_responsaveis'")
            if cursor.fetchone() is None:
                raise Exception("A tabela 'controle_agentes_responsaveis' não existe no banco de dados.")

            for funcao_like, combo_widget in combo_mapping.items():
                carregar_dados_combo(conn, funcao_like, combo_widget)

    except Exception as e:
        print(f"Erro ao carregar Ordenadores de Despesas: {e}")

def carregar_dados_combo(conn, funcao_like, combo_widget):
    if "NOT LIKE" in funcao_like:
        sql_query = """
            SELECT nome, posto, funcao FROM controle_agentes_responsaveis
            WHERE funcao NOT LIKE 'Ordenador de Despesa%' AND
                funcao NOT LIKE 'Agente Fiscal%' AND
                funcao NOT LIKE 'Gerente de Crédito%' AND
                funcao NOT LIKE 'Operador%'
        """
    else:
        sql_query = f"SELECT nome, posto, funcao FROM controle_agentes_responsaveis WHERE funcao LIKE '{funcao_like}'"
    
    agentes_df = pd.read_sql_query(sql_query, conn)
    combo_widget.clear()
    for _, row in agentes_df.iterrows():
        texto_display = f"{row['nome']}\n{row['posto']}\n{row['funcao']}"
        combo_widget.addItem(texto_display, userData=row.to_dict())