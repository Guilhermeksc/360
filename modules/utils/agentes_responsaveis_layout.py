from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QComboBox, QGroupBox
import sqlite3
import pandas as pd

def create_agentes_responsaveis_layout(database_path, max_width=300):
    """Cria o layout para os agentes responsáveis e o organiza em um QGroupBox estilizado."""
    group_box = QGroupBox("Agentes Responsáveis")
    group_box.setMaximumWidth(max_width)  # Define a largura máxima
    group_box.setStyleSheet("""
        QGroupBox {
            border: 1px solid #3C3C5A;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            color: white;
            margin-top: 13px;
        }
        QGroupBox:title {
            subcontrol-origin: margin;
        }
    """)

    # Frame para organizar os agentes responsáveis
    frame_agentes = QFrame()
    agente_responsavel_layout = QVBoxLayout(frame_agentes)

    # Criação dos ComboBox com ajuste de altura
    ordenador_combo = create_combo_box('', [], 270, 58)
    agente_fiscal_combo = create_combo_box('', [], 270, 58)
    gerente_credito_combo = create_combo_box('', [], 270, 58)
    responsavel_demanda_combo = create_combo_box('', [], 270, 58)
    operador_dispensa_combo = create_combo_box('', [], 270, 58)

    # Adicionando labels e ComboBox diretamente ao layout
    labels_combos = [
        ("Ordenador de Despesa:", ordenador_combo),
        ("Agente Fiscal:", agente_fiscal_combo),
        ("Gerente de Crédito:", gerente_credito_combo),
        ("Responsável pela Demanda:", responsavel_demanda_combo),
        ("Operador da Contratação:", operador_dispensa_combo)
    ]

    for label_text, combo_box in labels_combos:
        # Cria um layout vertical para a label e o ComboBox
        h_layout = QVBoxLayout()
        h_layout.setSpacing(0)  # Ajusta o espaçamento entre label e ComboBox
        h_layout.setContentsMargins(0, 0, 0, 0)  # Margens para o layout

        # Cria e estiliza a label
        label = QLabel(label_text)
        label.setStyleSheet("color: #8AB4F7; font-size: 16px")
        h_layout.addWidget(label)
        h_layout.addWidget(combo_box)
        # Adiciona o layout ao layout principal
        agente_responsavel_layout.addLayout(h_layout)

    # Carrega os agentes responsáveis para popular os ComboBoxes
    carregar_agentes_responsaveis(database_path, {
        "Ordenador de Despesa%": ordenador_combo,
        "Agente Fiscal%": agente_fiscal_combo,
        "Gerente de Crédito%": gerente_credito_combo,
        "Operador%": operador_dispensa_combo,
        "NOT LIKE": responsavel_demanda_combo
    })

    # Adiciona o frame de agentes ao layout do group_box
    group_layout = QVBoxLayout(group_box)
    group_layout.addWidget(frame_agentes)

    return group_box

def create_combo_box(current_text, items, fixed_width, fixed_height):
    combo_box = QComboBox()
    combo_box.addItems(items)
    combo_box.setFixedWidth(fixed_width)
    combo_box.setFixedHeight(fixed_height)  # Define a altura fixa do ComboBox
    combo_box.setCurrentText(current_text)
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