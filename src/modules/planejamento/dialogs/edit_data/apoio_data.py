COLUNAS_LEGIVEIS = {
    'nup': 'NUP',
    'material_servico': 'Material (M) ou Serviço (S)',
    'vigencia': 'Vigência (Ex: 2 (dois) meses, 6 (seis) meses), etc.',
    'criterio_julgamento': 'Critério de Julgamento (Menor Preço ou Maior Desconto)',
    'com_disputa': 'Com disputa? Sim (S) ou Não (N)',
    'pesquisa_preco': 'Pesquisa Concomitante? Sim (S) ou Não (N)',
    'sigla_om': 'OM',
    'setor_responsavel': 'Setor Responsável',
    'cod_par': 'Código PAR',
    'prioridade_par': 'Prioridade PAR (Necessário, Urgente ou Desejável)',
    'cep': 'CEP',
    'endereco': 'Endereço',
    'email': 'Email',
    'telefone': 'Telefone',
    'dias_para_recebimento': 'Dias para Recebimento',
    'horario_para_recebimento': 'Horário para Recebimento',
    'valor_total': 'Valor Total',
    'acao_interna': 'Ação Interna',
    'fonte_recursos': 'Fonte de Recursos',
    'natureza_despesa': 'Natureza da Despesa',
    'unidade_orcamentaria': 'Unidade Orçamentária',
    'ptres': 'PTRES',
    'atividade_custeio': 'Atividade de Custeio',
    'justificativa': 'Justificativa',
    'comunicacao_padronizada': 'Comunicação Padronizada (CP), Ex: 60-25',
}

# Dicionário inverso
COLUNAS_LEGIVEIS_INVERSO = {v: k for k, v in COLUNAS_LEGIVEIS.items()}

CORRECAO_VALORES = {
    'material_servico': {
        'M': 'Material', 'm': 'Material', 'Material': 'Material', 'material': 'Material',
        'S': 'Serviço', 's': 'Serviço', 'Serviço': 'Serviço', 'serviço': 'Serviço',
        'Servico': 'Serviço', 'servico': 'Serviço'
    },
    'com_disputa': {
        'S': 'Sim', 's': 'Sim', 'Sim': 'Sim', 'sim': 'Sim',
        'N': 'Não', 'n': 'Não', 'Não': 'Não', 'não': 'Não',
        'Nao': 'Não', 'nao': 'Não'
    },
    'pesquisa_preco': {
        'S': 'Sim', 's': 'Sim', 'Sim': 'Sim', 'sim': 'Sim',
        'N': 'Não', 'n': 'Não', 'Não': 'Não', 'não': 'Não',
        'Nao': 'Não', 'nao': 'Não'
    },
    'atividade_custeio': {
        'S': 'Sim', 's': 'Sim', 'Sim': 'Sim', 'sim': 'Sim',
        'N': 'Não', 'n': 'Não', 'Não': 'Não', 'não': 'Não',
        'Nao': 'Não', 'nao': 'Não'
    }
}

STYLE_STACKED_WIDGET = """
    QLabel { font-size: 16px; }
    QCheckBox { font-size: 16px; }
    QLineEdit { font-size: 14px; }
"""
STYLE_GROUP_BOX = """
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
    QTextEdit {
        font-size: 14px;
    }
    QPushButton {
        font-size: 18px;
    }
"""

STYLE_NAV_LAYOUT = """
    QPushButton[class="nav-button"] {
        background-color: #181928;
        color: #8BE9D9;
        border: none;
        font-size: 14px;
        border-top: 10px solid #181928;
        border-bottom: 5px solid #13141F;                           
    }
    QPushButton[class="nav-button"]:hover {
        background-color: #181928;
        color: white;
        font-size: 14px;
        border-top: 3px solid #181928;
        border-bottom: 5px solid #13141F;
    }
    QPushButton[class="nav-button selected"] {
        background-color: #13141F;
        color: white;
        font-weight: bold;
        font-size: 14px;
        border-top: 2px solid #FF79C6;
        border-bottom: 5px solid #13141F;
    }
"""