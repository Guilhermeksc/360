from PyQt6.QtWidgets import *

def create_contratacao_group(data):
    contratacao_group_box = QGroupBox("Informações da Contratação")
    contratacao_group_box.setStyleSheet("""
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

    contratacao_layout = QVBoxLayout()

    # Campo de Objeto
    objeto_layout = QHBoxLayout()
    objeto_label = QLabel("Objeto:")
    objeto_edit = QLineEdit(data.get('objeto', ''))
    objeto_layout.addWidget(objeto_label)
    objeto_layout.addWidget(objeto_edit)
    contratacao_layout.addLayout(objeto_layout)

    # NUP, Material e Serviço com seleção exclusiva
    nup_layout = QHBoxLayout()
    nup_label = QLabel("NUP:")
    nup_edit = QLineEdit(data.get('nup', ''))
    nup_layout.addWidget(nup_label)
    nup_layout.addWidget(nup_edit)

    contratacao_layout.addLayout(nup_layout)

    # Layout para Vigência e Critério de Julgamento
    vigencia_criterio_layout = QHBoxLayout()

    # Vigência ComboBox
    vigencia_label = QLabel("Vigência:")
    vigencia_combo = QComboBox()
    vigencia_combo.setEditable(True)
    vigencia_combo.setStyleSheet("font-size: 14px;")  # Define o tamanho da fonte via stylesheet
    for i in range(1, 13):
        vigencia_combo.addItem(f"{i} ({number_to_text(i)}) meses")
    vigencia = data.get('vigencia', '2 (dois) meses')
    vigencia_combo.setCurrentText(vigencia)

    # Expansão horizontal apenas, mantendo altura padrão
    vigencia_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    # Adiciona Vigência ao layout
    vigencia_criterio_layout.addWidget(vigencia_label)
    vigencia_criterio_layout.addWidget(vigencia_combo)

    # Critério de Julgamento ComboBox
    criterio_label = QLabel("Critério Julgamento:")
    criterio_combo = QComboBox()
    criterio_combo.setStyleSheet("font-size: 14px;")  # Define o tamanho da fonte via stylesheet
    criterio_combo.addItems(["Menor Preço", "Maior Desconto"])
    criterio_combo.setCurrentText(data.get('criterio_julgamento', 'Menor Preço'))

    # Expansão horizontal apenas, mantendo altura padrão
    criterio_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    # Adiciona Critério de Julgamento ao layout
    vigencia_criterio_layout.addWidget(criterio_label)
    vigencia_criterio_layout.addWidget(criterio_combo)

    # Adiciona o layout ao layout principal de contratação
    contratacao_layout.addLayout(vigencia_criterio_layout)

    # Material e Serviço com seleção exclusiva usando RadioButtons
    material_servico_layout = QHBoxLayout()
    material_servico_label = QLabel("Material/Serviço:")
    radio_material = QRadioButton("Material")
    radio_servico = QRadioButton("Serviço")

    # Grupo de botões exclusivo para Material e Serviço
    material_servico_group = QButtonGroup()
    material_servico_group.addButton(radio_material)
    material_servico_group.addButton(radio_servico)

    # Define o estado inicial
    material_servico = data.get('material_servico', 'Material')
    radio_servico.setChecked(material_servico == "Serviço")
    radio_material.setChecked(material_servico == "Material")

    # Adiciona ao layout
    material_servico_layout.addWidget(material_servico_label)
    material_servico_layout.addWidget(radio_material)
    material_servico_layout.addWidget(radio_servico)
    contratacao_layout.addLayout(material_servico_layout)

    # Com Disputa
    disputa_layout = QHBoxLayout()
    disputa_label = QLabel("Com disputa?")
    radio_disputa_sim = QRadioButton("Sim")
    radio_disputa_nao = QRadioButton("Não")
    disputa_group = QButtonGroup()  # Grupo exclusivo para este conjunto
    disputa_group.addButton(radio_disputa_sim)
    disputa_group.addButton(radio_disputa_nao)

    # Define o estado inicial com base nos dados, considerando ambos os botões
    com_disputa_value = data.get('com_disputa', 'Sim')
    radio_disputa_sim.setChecked(com_disputa_value == 'Sim')
    radio_disputa_nao.setChecked(com_disputa_value == 'Não')

    disputa_layout.addWidget(disputa_label)
    disputa_layout.addWidget(radio_disputa_sim)
    disputa_layout.addWidget(radio_disputa_nao)
    contratacao_layout.addLayout(disputa_layout)

    # Pesquisa de Preço Concomitante
    pesquisa_layout = QHBoxLayout()
    pesquisa_label = QLabel("Pesquisa Concomitante?")
    radio_pesquisa_sim = QRadioButton("Sim")
    radio_pesquisa_nao = QRadioButton("Não")
    pesquisa_group = QButtonGroup()  # Grupo exclusivo para este conjunto
    pesquisa_group.addButton(radio_pesquisa_sim)
    pesquisa_group.addButton(radio_pesquisa_nao)

    # Define o estado inicial com base nos dados, considerando ambos os botões
    pesquisa_preco_value = data.get('pesquisa_preco', 'Não')
    radio_pesquisa_sim.setChecked(pesquisa_preco_value == 'Sim')
    radio_pesquisa_nao.setChecked(pesquisa_preco_value == 'Não')

    pesquisa_layout.addWidget(pesquisa_label)
    pesquisa_layout.addWidget(radio_pesquisa_sim)
    pesquisa_layout.addWidget(radio_pesquisa_nao)
    contratacao_layout.addLayout(pesquisa_layout)

    # Atividade de Custeio
    custeio_layout = QHBoxLayout()
    custeio_label = QLabel("Atividade de Custeio?")
    radio_custeio_sim = QRadioButton("Sim")
    radio_custeio_nao = QRadioButton("Não")
    custeio_group = QButtonGroup()  # Grupo exclusivo para este conjunto
    custeio_group.addButton(radio_custeio_sim)
    custeio_group.addButton(radio_custeio_nao)

    # Define o estado inicial com base nos dados, considerando ambos os botões
    atividade_custeio_value = data.get('atividade_custeio', 'Não')
    radio_custeio_sim.setChecked(atividade_custeio_value == 'Sim')
    radio_custeio_nao.setChecked(atividade_custeio_value == 'Não')

    custeio_layout.addWidget(custeio_label)
    custeio_layout.addWidget(radio_custeio_sim)
    custeio_layout.addWidget(radio_custeio_nao)
    contratacao_layout.addLayout(custeio_layout)

    # Configura layout do GroupBox
    contratacao_group_box.setLayout(contratacao_layout)

    # Armazena widgets, incluindo os grupos
    widgets = {
        'objeto_edit': objeto_edit,
        'nup_edit': nup_edit,
        'radio_material': radio_material,
        'radio_servico': radio_servico,
        'vigencia_combo': vigencia_combo,
        'criterio_combo': criterio_combo,
        'radio_disputa_sim': radio_disputa_sim,
        'radio_disputa_nao': radio_disputa_nao,
        'radio_pesquisa_sim': radio_pesquisa_sim,
        'radio_pesquisa_nao': radio_pesquisa_nao,
        'radio_custeio_sim': radio_custeio_sim,
        'radio_custeio_nao': radio_custeio_nao,
        'material_servico_group': material_servico_group,
        'disputa_group': disputa_group,
        'pesquisa_group': pesquisa_group,
        'custeio_group': custeio_group,
    }
    
    return contratacao_group_box, widgets

def number_to_text(number):
    numbers_in_words = ["um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze"]
    return numbers_in_words[number - 1] 

def create_info_comprasnet(data):
    """Cria um box com informações de compras, com campos somente leitura."""
    comprasnet_group_box = QGroupBox("Informações Integradas ao ComprasNet")
    comprasnet_group_box.setStyleSheet("""
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
    
    comprasnet_layout = QVBoxLayout()

    # Função auxiliar para criar um layout de linha com label e campo de texto não editável
    def create_info_row(label_text, value):
        row_layout = QHBoxLayout()
        label = QLabel(label_text)
        edit = QLineEdit(value)
        edit.setReadOnly(True)
        row_layout.addWidget(label)
        row_layout.addWidget(edit)
        return row_layout

    # Adiciona as informações no layout do grupo
    comprasnet_layout.addLayout(create_info_row("Valor Homologado:", data.get("valor_homologado", "")))
    comprasnet_layout.addLayout(create_info_row("Status:", data.get("status", "")))
    comprasnet_layout.addLayout(create_info_row("Última Atualização:", data.get("ultima_atualizacao", "")))
    comprasnet_layout.addLayout(create_info_row("Quantidade de Itens Homologados:", data.get("qtd_itens_homologados", "")))
    comprasnet_layout.addLayout(create_info_row("Itens Fracassados/Desertos:", data.get("itens_fracassados_desertos", "")))
    comprasnet_layout.addLayout(create_info_row("Itens Não Definidos:", data.get("itens_nao_definidos", "")))

    # Define o layout do QGroupBox
    comprasnet_group_box.setLayout(comprasnet_layout)

    return comprasnet_group_box
