from PyQt6.QtWidgets import *
from PyQt6.QtCore import QDate
import pandas as pd

def create_vigencia_criterio_layout(data):
    """Cria o layout para seleção de Vigência e Critério de Julgamento."""
    vigencia_criterio_layout = QHBoxLayout()

    # Vigência ComboBox
    vigencia_label = QLabel("Vigência:")
    vigencia_combo = QComboBox()
    vigencia_combo.setEditable(True)
    for i in range(1, 13):
        vigencia_combo.addItem(f"{i} ({number_to_text(i)}) meses")
    vigencia = data.get('vigencia', '2 (dois) meses')
    vigencia_combo.setCurrentText(vigencia)
    
    # Adiciona Vigência ao layout
    vigencia_criterio_layout.addWidget(vigencia_label)
    vigencia_criterio_layout.addWidget(vigencia_combo)

    # Critério de Julgamento ComboBox
    criterio_label = QLabel("Critério Julgamento:")
    criterio_combo = QComboBox()
    criterio_combo.addItems(["Menor Preço", "Maior Desconto"])
    criterio_combo.setCurrentText(data.get('criterio_julgamento', 'Menor Preço'))
    
    # Adiciona Critério de Julgamento ao layout
    vigencia_criterio_layout.addWidget(criterio_label)
    vigencia_criterio_layout.addWidget(criterio_combo)

    return vigencia_criterio_layout

def create_layout(label_text, widget, fixed_width=None):
    layout = QHBoxLayout()
    label = QLabel(label_text)        
    # Adiciona a largura fixa se especificada
    if fixed_width and isinstance(widget, QWidget):
        widget.setFixedWidth(fixed_width)
    
    layout.addWidget(label)
    layout.addWidget(widget)
    return layout

def number_to_text(number):
    numbers_in_words = ["um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze"]
    return numbers_in_words[number - 1] 


def create_classificacao_orcamentaria_group(data):
    """Cria o QGroupBox para Classificação Orçamentária."""
    classificacao_group = QGroupBox("Classificação Orçamentária")
    classificacao_group.setStyleSheet("""
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
    classificacao_group.setFixedWidth(400)
    
    layout = QVBoxLayout()
    fields = [
        ("Valor Estimado:", 'valor_total'),
        ("Ação Interna:", 'acao_interna'),
        ("Fonte de Recurso (FR):", 'fonte_recursos'),
        ("Natureza de Despesa (ND):", 'natureza_despesa'),
        ("Unidade Orçamentária (UO):", 'unidade_orcamentaria'),
        ("PTRES:", 'ptres')
    ]
    
    for label_text, key in fields:
        layout.addLayout(create_layout(label_text, QLineEdit(str(data[key]) if pd.notna(data[key]) else "")))

    classificacao_group.setLayout(layout)
    return classificacao_group

def create_contratacao_group(data):
    """Configura o layout principal para contratação."""
    contratacao_layout = QVBoxLayout()

    # Campo de Objeto
    objeto_layout = QHBoxLayout()
    objeto_label = QLabel("Objeto:")
    objeto_edit = QLineEdit(data.get('objeto', ''))
    objeto_layout.addWidget(objeto_label)
    objeto_layout.addWidget(objeto_edit)
    contratacao_layout.addLayout(objeto_layout)

    # NUP, Material e Serviço com seleção exclusiva
    nup_material_servico_layout = QHBoxLayout()
    nup_label = QLabel("NUP:")
    nup_edit = QLineEdit(data.get('nup', ''))
    nup_material_servico_layout.addWidget(nup_label)
    nup_material_servico_layout.addWidget(nup_edit)

    checkbox_material = QCheckBox("Material")
    checkbox_servico = QCheckBox("Serviço")
    material_servico_group = QButtonGroup()
    material_servico_group.addButton(checkbox_material)
    material_servico_group.addButton(checkbox_servico)
    
    # Estado inicial com base nos dados
    material_servico = data.get('material_servico', 'Material')
    checkbox_material.setChecked(material_servico == "Material")
    checkbox_servico.setChecked(material_servico == "Serviço")

    nup_material_servico_layout.addWidget(checkbox_material)
    nup_material_servico_layout.addWidget(checkbox_servico)
    contratacao_layout.addLayout(nup_material_servico_layout)

    # Vigência e Critério de Julgamento
    contratacao_layout.addLayout(create_vigencia_criterio_layout(data))

    # Com Disputa
    disputa_layout = QHBoxLayout()
    disputa_label = QLabel("Com disputa?")
    radio_disputa_sim = QRadioButton("Sim")
    radio_disputa_nao = QRadioButton("Não")
    disputa_group = QButtonGroup()
    disputa_group.addButton(radio_disputa_sim)
    disputa_group.addButton(radio_disputa_nao)
    com_disputa = data.get('com_disputa', 'Sim')
    radio_disputa_sim.setChecked(com_disputa == 'Sim')
    radio_disputa_nao.setChecked(com_disputa != 'Sim')

    disputa_layout.addWidget(disputa_label)
    disputa_layout.addWidget(radio_disputa_sim)
    disputa_layout.addWidget(radio_disputa_nao)
    contratacao_layout.addLayout(disputa_layout)

    # Pesquisa de Preço Concomitante
    pesquisa_concomitante_layout = QHBoxLayout()
    pesquisa_label = QLabel("Pesquisa Concomitante?")
    radio_pesquisa_sim = QRadioButton("Sim")
    radio_pesquisa_nao = QRadioButton("Não")
    pesquisa_group = QButtonGroup()
    pesquisa_group.addButton(radio_pesquisa_sim)
    pesquisa_group.addButton(radio_pesquisa_nao)
    pesquisa_concomitante = data.get('pesquisa_preco', 'Não')
    radio_pesquisa_sim.setChecked(pesquisa_concomitante == 'Sim')
    radio_pesquisa_nao.setChecked(pesquisa_concomitante != 'Sim')

    pesquisa_concomitante_layout.addWidget(pesquisa_label)
    pesquisa_concomitante_layout.addWidget(radio_pesquisa_sim)
    pesquisa_concomitante_layout.addWidget(radio_pesquisa_nao)
    contratacao_layout.addLayout(pesquisa_concomitante_layout)

    # Atividade de Custeio
    custeio_layout = QHBoxLayout()
    custeio_label = QLabel("Atividade de Custeio?")
    radio_custeio_sim = QRadioButton("Sim")
    radio_custeio_nao = QRadioButton("Não")
    custeio_group = QButtonGroup()
    custeio_group.addButton(radio_custeio_sim)
    custeio_group.addButton(radio_custeio_nao)
    atividade_custeio = data.get('atividade_custeio', 'Não')
    radio_custeio_sim.setChecked(atividade_custeio == 'Sim')
    radio_custeio_nao.setChecked(atividade_custeio != 'Sim')

    custeio_layout.addWidget(custeio_label)
    custeio_layout.addWidget(radio_custeio_sim)
    custeio_layout.addWidget(radio_custeio_nao)
    contratacao_layout.addLayout(custeio_layout)

    # Linha divisória
    contratacao_layout.addLayout(linha_divisoria_layout())

    # Data da Sessão Pública com QCalendarWidget
    data_layout = QVBoxLayout()
    data_label = QLabel("Data da Sessão Pública:")
    data_calendar = QCalendarWidget()
    data_calendar.setGridVisible(True)
    data_sessao = data.get('data_sessao', QDate.currentDate())
    data_calendar.setSelectedDate(QDate.fromString(data_sessao, "yyyy-MM-dd") if isinstance(data_sessao, str) else QDate.currentDate())

    data_layout.addWidget(data_label)
    data_layout.addWidget(data_calendar)
    contratacao_layout.addLayout(data_layout)

    return contratacao_layout

def linha_divisoria_layout():
    """Cria uma linha divisória."""
    linha_divisoria = QFrame()
    linha_divisoria.setFrameShape(QFrame.Shape.HLine)
    linha_divisoria.setFrameShadow(QFrame.Shadow.Sunken)
    linha_divisoria.setFixedHeight(2)
    linha_divisoria.setStyleSheet("background-color: #3C3C5A;")
    
    layout = QVBoxLayout()
    layout.addWidget(linha_divisoria)
    layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
    return layout
