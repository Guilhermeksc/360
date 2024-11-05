from PyQt6.QtWidgets import *
from PyQt6.QtCore import QDate
import pandas as pd

def create_classificacao_orcamentaria_group(data):
    """Cria o QGroupBox para a seção de Classificação Orçamentária."""
    classificacao_orcamentaria_group_box = QGroupBox("Classificação Orçamentária")
    classificacao_orcamentaria_group_box.setStyleSheet("""
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
            padding: 0 3px;
        }
    """)
    classificacao_orcamentaria_group_box.setFixedWidth(400)
    
    layout = QVBoxLayout()
    widgets_classificacao_orcamentaria = {}  # Dicionário para armazenar os widgets

    # Definindo campos de entrada
    fields = [
        ("Valor Estimado:", 'valor_total'),
        ("Ação Interna:", 'acao_interna'),
        ("Fonte de Recurso (FR):", 'fonte_recursos'),
        ("Natureza de Despesa (ND):", 'natureza_despesa'),
        ("Unidade Orçamentária (UO):", 'unidade_orcamentaria'),
        ("PTRES:", 'ptres')
    ]

    for label_text, key in fields:
        field_layout = QHBoxLayout()
        label = QLabel(label_text)
        widget = QLineEdit(str(data.get(key, '')) if pd.notna(data.get(key)) else "")
        field_layout.addWidget(label)
        field_layout.addWidget(widget)
        layout.addLayout(field_layout)

        # Armazena o widget no dicionário
        widgets_classificacao_orcamentaria[key] = widget

    # Adicionando o rádio button de Atividade de Custeio
    custeio_layout = QHBoxLayout()
    custeio_label = QLabel("Atividade de Custeio?")
    radio_custeio_sim = QRadioButton("Sim")
    radio_custeio_nao = QRadioButton("Não")
    custeio_group = QButtonGroup()  # Grupo exclusivo para o conjunto de botões
    custeio_group.addButton(radio_custeio_sim)
    custeio_group.addButton(radio_custeio_nao)

    # Define o estado inicial com base nos dados
    atividade_custeio_value = data.get('atividade_custeio', 'Não')
    radio_custeio_sim.setChecked(atividade_custeio_value == 'Sim')
    radio_custeio_nao.setChecked(atividade_custeio_value == 'Não')

    custeio_layout.addWidget(custeio_label)
    custeio_layout.addWidget(radio_custeio_sim)
    custeio_layout.addWidget(radio_custeio_nao)
    
    # Adiciona o layout do rádio button ao layout principal
    layout.addLayout(custeio_layout)

    # Armazena cada botão de rádio separadamente no dicionário
    widgets_classificacao_orcamentaria['radio_custeio_sim'] = radio_custeio_sim
    widgets_classificacao_orcamentaria['radio_custeio_nao'] = radio_custeio_nao

    classificacao_orcamentaria_group_box.setLayout(layout)
    
    return classificacao_orcamentaria_group_box, widgets_classificacao_orcamentaria
