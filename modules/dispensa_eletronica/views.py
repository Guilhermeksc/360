from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from modules.utils.search_bar import setup_search_bar, MultiColumnFilterProxyModel
from modules.utils.add_button import add_button, create_button
from config.styles.styless import apply_table_custom_style
from modules.dispensa_eletronica.dialogs.editar_dados import EditDataDialog
from modules.utils.consulta_api import setup_consulta_api
from modules.utils.formulario import setup_formularios
from modules.dispensa_eletronica.dialogs.classificacao_orcamentaria import create_vigencia_criterio_layout
from modules.utils.linha_layout import linha_divisoria_layout
from modules.utils.custom_date_edit import CustomDateEdit
from modules.utils.select_om import create_selecao_om_layout, load_sigla_om, on_om_changed
from modules.utils.agentes_responsaveis_layout import create_agentes_responsaveis_layout
from pathlib import Path
import pandas as pd
from config.paths import CONTROLE_DADOS
class EditarDadosWindow(QMainWindow):
    save_data = pyqtSignal()
    
    """Classe para a janela de edição de dados."""
    def __init__(self, dados, icons, parent=None):
        super().__init__(parent)
        self.dados = dados
        self.icons = icons
        self.selected_button = None
        self.stacked_widget = QStackedWidget(self)        
        # Define estilo para a fonte e borda do central_widget
        self.stacked_widget.setStyleSheet("""
            QLabel {
                font-size: 16px;
            }
            QCheckBox {
                font-size: 16px;
            }
            QLineEdit {
                font-size: 14px;
            }
        """)

        self.widgets_map = {}
        
        # Configurações da janela
        self.setWindowTitle("Editar Dados")
        self.setWindowIcon(self.icons.get("edit", None))
        self.setFixedSize(1250, 780)
        
        self.database_path = CONTROLE_DADOS
        # Configuração da interface
        self.setup_ui()

    def setup_ui(self):
        # Configura o widget principal e define o fundo preto e borda
        main_widget = QWidget(self)

        self.setCentralWidget(main_widget)

        # Configuração do layout principal com margens e espaçamento zero
        self.central_layout = QHBoxLayout(main_widget)
        self.central_layout.setSpacing(0)
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        # Layout esquerdo
        Left_layout = QVBoxLayout()
        
        # Adiciona título e navegação
        layout_titulo = self.setup_layout_titulo()
        Left_layout.addLayout(layout_titulo)
        
        nav_frame = self.create_navigation_layout()
        Left_layout.addWidget(nav_frame)

        # Adiciona o QStackedWidget abaixo do layout de navegação
        Left_layout.addWidget(self.stacked_widget)
        
        self.central_layout.addLayout(Left_layout)

        # Configura o layout da consulta API
        group_box_consulta_api, self.cnpj_edit, self.sequencial_edit = setup_consulta_api(parent=self, icons=self.icons)
        
        group_box_agentes = create_agentes_responsaveis_layout(self.database_path)

        group_box_formulario = setup_formularios(parent=self, icons=self.icons)

        group_box_sessao =  self.create_sessao_publica_group()

        # Adicione o frame ao layout desejado
        Right_layout = QVBoxLayout()
        Right_layout.addWidget(group_box_consulta_api)
        Right_layout.addWidget(group_box_agentes)
        Right_layout.addWidget(group_box_formulario)
        Right_layout.addWidget(group_box_sessao)
        self.central_layout.addLayout(Right_layout)

        # Configuração dos widgets no QStackedWidget
        self.setup_stacked_widgets()

    def create_navigation_layout(self):
        # Criação do frame que conterá o nav_layout e aplicará a borda inferior
        nav_frame = QFrame()
        nav_frame.setStyleSheet("""
            QFrame {
                border-bottom: 5px solid #13141F;
            }
        """)

        # Layout horizontal para os botões de navegação
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setSpacing(0)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        buttons = [
            ("Informações", "Informações"),
            ("Setor Responsável", "Setor Responsável"),
            ("Documentos", "Documentos"),
            ("Anexos", "Anexos"),
            ("Resultados", "Resultados"),
        ]

        for index, (text, name) in enumerate(buttons):
            button = QPushButton(text, self)
            button.setObjectName(name)
            button.setProperty("class", "nav-button")
            button.clicked.connect(lambda _, n=name, b=button: self.on_navigation_button_clicked(n, b))
            nav_layout.addWidget(button)

            # Define o botão "Informações" como selecionado
            if name == "Informações":
                button.setProperty("class", "nav-button selected")
                button.setStyleSheet("")  # Aplica o estilo imediatamente
                self.selected_button = button  # Mantém o botão "Informações" como o selecionado inicial

        # Adiciona um espaço expansivo no final para empurrar os botões para a esquerda
        nav_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Define o estilo para os botões dentro do nav_layout
        self.setStyleSheet("""
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
        """)

        return nav_frame

    def on_navigation_button_clicked(self, name, button):
        if self.selected_button:
            self.selected_button.setProperty("class", "nav-button")
            self.selected_button.setStyleSheet("")

        button.setProperty("class", "nav-button selected")
        button.setStyleSheet("")

        self.selected_button = button
        self.show_widget(name)

    def show_widget(self, name):
        widget = self.widgets_map.get(name)
        if widget:
            self.stacked_widget.setCurrentWidget(widget)

    def setup_stacked_widgets(self):
        """Configura os widgets para cada seção e os adiciona ao QStackedWidget"""
        # Dados de exemplo para preencher os widgets
        data = self.dados  # Utilize os dados reais

        # Cria widgets para cada seção
        self.widgets_map = {
            "Informações": self.stacked_widget_info(data),
            "Setor Responsável": self.stacked_widget_responsaveis(data),
            "Documentos": self.stacked_widget_documentos(data),
            "Anexos": self.stacked_widget_anexos(data),
            "Resultados": self.stacked_widget_pncp(data),
        }

        # Adiciona cada widget ao QStackedWidget
        for name, widget in self.widgets_map.items():
            self.stacked_widget.addWidget(widget)

    def stacked_widget_info(self, data):
        frame = QFrame()
        layout = QVBoxLayout()
        hbox_top_layout = QHBoxLayout()
        contratacao_layout = self.create_contratacao_group(data)
        classificacao_orcamentaria_group_box = self.create_classificacao_orcamentaria_group(data)
        hbox_top_layout.addLayout(contratacao_layout)
        hbox_top_layout.addWidget(classificacao_orcamentaria_group_box)
        layout.addLayout(hbox_top_layout)
        frame.setLayout(layout)
        return frame

    def stacked_widget_responsaveis(self, data):
        frame = QFrame()
        layout = QVBoxLayout()
        setor_responsavel_layout = self.create_dados_responsavel_contratacao_group(data)
        layout.addLayout(setor_responsavel_layout)
        frame.setLayout(layout)
        return frame
    
    def create_dados_responsavel_contratacao_group(self, data):
        setor_responsavel_layout = QVBoxLayout()
        
        self.par_edit = QLineEdit(str(data.get('cod_par', '')))
        self.par_edit.setFixedWidth(50)
        self.prioridade_combo = self.create_combo_box(data.get('prioridade_par', 'Necessário'), ["Necessário", "Urgente", "Desejável"], 110, 30)
            
        par_layout = QHBoxLayout()

        # Configuração da CP
        cp_label = QLabel("Número da CP:")
        self.cp_edit = QLineEdit(data['comunicacao_padronizada'])
        self.cp_edit.setFixedWidth(50)  # Ajuste do tamanho para 50
        par_layout.addWidget(cp_label)
        par_layout.addWidget(self.cp_edit)

        par_label = QLabel("Meta do PAR:")
        prioridade_label = QLabel("Prioridade:")
        par_layout.addWidget(par_label)
        par_layout.addWidget(self.par_edit)
        par_layout.addWidget(prioridade_label)
        par_layout.addWidget(self.prioridade_combo)
        setor_responsavel_layout.addLayout(par_layout)

        self.endereco_edit = QLineEdit(data['endereco'])
        self.endereco_edit.setFixedWidth(350)
        self.cep_edit = QLineEdit(str(data.get('cep', '')))
        endereco_cep_layout = QHBoxLayout()
        endereco_label = QLabel("Endereço:")
        cep_label = QLabel("CEP:")
        endereco_cep_layout.addWidget(endereco_label)
        endereco_cep_layout.addWidget(self.endereco_edit)
        endereco_cep_layout.addWidget(cep_label)
        endereco_cep_layout.addWidget(self.cep_edit)
        setor_responsavel_layout.addLayout(endereco_cep_layout)

        self.email_edit = QLineEdit(data['email'])
        self.email_edit.setFixedWidth(400)
        self.telefone_edit = QLineEdit(data['telefone'])
        email_telefone_layout = QHBoxLayout()
        email_telefone_layout.addLayout(self.create_layout("E-mail:", self.email_edit))
        email_telefone_layout.addLayout(self.create_layout("Tel:", self.telefone_edit))
        setor_responsavel_layout.addLayout(email_telefone_layout)

        self.dias_edit = QLineEdit("Segunda à Sexta")
        setor_responsavel_layout.addLayout(self.create_layout("Dias para Recebimento:", self.dias_edit))

        self.horario_edit = QLineEdit("09 às 11h20 e 14 às 16h30")
        setor_responsavel_layout.addLayout(self.create_layout("Horário para Recebimento:", self.horario_edit))

        # Adicionando Justificativa
        justificativa_label = QLabel("Justificativa para a contratação:")
        justificativa_label.setStyleSheet("font-size: 12pt;")
        self.justificativa_edit = QTextEdit(self.get_justification_text())
        setor_responsavel_layout.addWidget(justificativa_label)
        setor_responsavel_layout.addWidget(self.justificativa_edit)

        return setor_responsavel_layout

    def get_justification_text(self):
        pass
        # current_justification = self.df_registro_selecionado['justificativa'].iloc[0]

        # # Retorna o valor atual se ele existir, senão, constrói uma justificativa baseada no tipo de material/serviço
        # if current_justification:  # Checa se existe uma justificativa
        #     return current_justification
        # else:
        #     # Gera justificativa padrão com base no tipo de material ou serviço
        #     if self.material_servico == 'Material':
        #         return (f"A aquisição de {self.objeto} se faz necessária para o atendimento das necessidades do(a) {self.setor_responsavel} do(a) {self.orgao_responsavel} ({self.sigla_om}). A disponibilidade e a qualidade dos materiais são essenciais para garantir a continuidade das operações e a eficiência das atividades desempenhadas pelo(a) {self.setor_responsavel}.")
        #     elif self.material_servico == 'Serviço':
        #         return (f"A contratação de empresa especializada na prestação de serviços de {self.objeto} é imprescindível para o atendimento das necessidades do(a) {self.setor_responsavel} do(a) {self.orgao_responsavel} ({self.sigla_om}).")
        #     return ""
        
    def create_classificacao_orcamentaria_group(self, data):
        classificacao_orcamentaria_group_box = QGroupBox("Classificação Orçamentária")
        # Aplicando o estilo CSS específico ao GroupBox
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
        classificacao_orcamentaria_layout = QVBoxLayout()

        # Valor Estimado
        self.valor_edit = QLineEdit(str(data['valor_total']) if pd.notna(data['valor_total']) else "")
        valor_layout = QHBoxLayout()
        valor_label = QLabel("Valor Estimado:")
        valor_layout.addWidget(valor_label)
        valor_layout.addWidget(self.valor_edit)
        classificacao_orcamentaria_layout.addLayout(valor_layout)

        self.acao_interna_edit = QLineEdit(data['acao_interna'])
        self.fonte_recurso_edit = QLineEdit(data['fonte_recursos'])
        self.natureza_despesa_edit = QLineEdit(data['natureza_despesa'])
        self.unidade_orcamentaria_edit = QLineEdit(data['unidade_orcamentaria'])
        self.ptres_edit = QLineEdit(data['ptres'])

        classificacao_orcamentaria_layout.addLayout(self.create_layout("Ação Interna:", self.acao_interna_edit))
        classificacao_orcamentaria_layout.addLayout(self.create_layout("Fonte de Recurso (FR):", self.fonte_recurso_edit))
        classificacao_orcamentaria_layout.addLayout(self.create_layout("Natureza de Despesa (ND):", self.natureza_despesa_edit))
        classificacao_orcamentaria_layout.addLayout(self.create_layout("Unidade Orçamentária (UO):", self.unidade_orcamentaria_edit))
        classificacao_orcamentaria_layout.addLayout(self.create_layout("PTRES:", self.ptres_edit))
    
        classificacao_orcamentaria_group_box.setLayout(classificacao_orcamentaria_layout)

        return classificacao_orcamentaria_group_box

    def create_contratacao_group(self, data):
        contratacao_layout = QVBoxLayout()

        # Objeto
        self.objeto_edit = QLineEdit(data['objeto'])

        # Criando um layout horizontal para o campo de entrada de texto e o ícone
        objeto_layout = QHBoxLayout()

        objeto_label = QLabel("Objeto:")
        objeto_layout.addWidget(objeto_label)
        objeto_layout.addWidget(self.objeto_edit)
        # Adicionando o layout horizontal diretamente ao layout principal de contratação
        contratacao_layout.addLayout(objeto_layout)

        nup_material_servico_layout = QHBoxLayout()

        nup_label = QLabel("NUP:")
        self.nup_edit = QLineEdit(data['nup'])
        nup_material_servico_layout.addWidget(nup_label)
        nup_material_servico_layout.addWidget(self.nup_edit)
    
        self.checkbox_material = QCheckBox("Material")
        self.checkbox_servico = QCheckBox("Serviço")

        # Agrupa os checkboxes em um QButtonGroup para garantir seleção exclusiva
        self.material_servico_group = QButtonGroup()
        self.material_servico_group.addButton(self.checkbox_material)
        self.material_servico_group.addButton(self.checkbox_servico)

        # Define o estado inicial dos checkboxes com base nos dados fornecidos
        material_servico = data.get('material_servico', 'Material')
        self.checkbox_material.setChecked(material_servico == "Material")
        self.checkbox_servico.setChecked(material_servico == "Serviço")

        # Adiciona os checkboxes ao layout
        nup_material_servico_layout.addWidget(self.checkbox_material)
        nup_material_servico_layout.addWidget(self.checkbox_servico)

        # Adiciona o layout de Material/Serviço ao layout principal
        contratacao_layout.addLayout(nup_material_servico_layout)

        contratacao_layout.addLayout(create_vigencia_criterio_layout(data))
        
        # Configuração de Com Disputa na mesma linha
        disputa_layout = QHBoxLayout()
        disputa_label = QLabel("Com disputa?")
        self.radio_disputa_sim = QRadioButton("Sim")
        self.radio_disputa_nao = QRadioButton("Não")
        self.disputa_group = QButtonGroup(self)
        self.disputa_group.addButton(self.radio_disputa_sim)
        self.disputa_group.addButton(self.radio_disputa_nao)
        disputa_layout.addWidget(disputa_label)
        disputa_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        disputa_layout.addWidget(self.radio_disputa_sim)
        disputa_layout.addWidget(self.radio_disputa_nao)
        contratacao_layout.addLayout(disputa_layout)

        com_disputa_value = data.get('com_disputa', 'Sim')
        if com_disputa_value is None or pd.isna(com_disputa_value):
            com_disputa_value = 'Sim'
        self.radio_disputa_sim.setChecked(com_disputa_value == 'Sim')
        self.radio_disputa_nao.setChecked(com_disputa_value != 'Sim')

        # Pesquisa de Preço Concomitante
        pesquisa_concomitante_layout = QHBoxLayout()
        pesquisa_concomitante_label = QLabel("Pesquisa Concomitante?")
        self.radio_pesquisa_sim = QRadioButton("Sim")
        self.radio_pesquisa_nao = QRadioButton("Não")
        self.pesquisa_group = QButtonGroup(self)
        self.pesquisa_group.addButton(self.radio_pesquisa_sim)
        self.pesquisa_group.addButton(self.radio_pesquisa_nao)
        pesquisa_preco_value = data.get('pesquisa_preco', 'Não')
        self.radio_pesquisa_sim.setChecked(pesquisa_preco_value == 'Sim')
        self.radio_pesquisa_nao.setChecked(pesquisa_preco_value != 'Sim')
        pesquisa_concomitante_layout.addWidget(pesquisa_concomitante_label)
        pesquisa_concomitante_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        pesquisa_concomitante_layout.addWidget(self.radio_pesquisa_sim)
        pesquisa_concomitante_layout.addWidget(self.radio_pesquisa_nao)
        contratacao_layout.addLayout(pesquisa_concomitante_layout)

        # Atividade de Custeio
        atividade_custeio_layout = QHBoxLayout()
        custeio_label = QLabel("Atividade de Custeio?")
        self.radio_custeio_sim = QRadioButton("Sim")
        self.radio_custeio_nao = QRadioButton("Não")
        atividade_custeio_value = data.get('atividade_custeio', 'Não')
        self.radio_custeio_sim.setChecked(atividade_custeio_value == 'Sim')
        self.radio_custeio_nao.setChecked(atividade_custeio_value != 'Sim')
        atividade_custeio_layout.addWidget(custeio_label)
        atividade_custeio_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        atividade_custeio_layout.addWidget(self.radio_custeio_sim)
        atividade_custeio_layout.addWidget(self.radio_custeio_nao)
        contratacao_layout.addLayout(atividade_custeio_layout)

        return contratacao_layout

    def create_combo_box(self, current_text, items, fixed_width, fixed_height):
        combo_box = QComboBox()
        combo_box.addItems(items)
        combo_box.setFixedWidth(fixed_width)
        combo_box.setFixedHeight(fixed_height)  # Define a altura fixa do ComboBox
        combo_box.setCurrentText(current_text)
        return combo_box

    def create_layout(self, label_text, widget, fixed_width=None):
        layout = QHBoxLayout()
        label = QLabel(label_text)        
        # Adiciona a largura fixa se especificada
        if fixed_width and isinstance(widget, QWidget):
            widget.setFixedWidth(fixed_width)
        
        layout.addWidget(label)
        layout.addWidget(widget)
        return layout
    
    def create_frame_formulario_group(self):
        formulario_group_box = QGroupBox("Formulário de Dados")
        self.apply_widget_style(formulario_group_box)   
        formulario_group_box.setFixedWidth(400)   
        formulario_layout = QVBoxLayout()

        # Adicionando os botões ao layout
        icon_excel_up = QIcon(str(self.ICONS_DIR / "excel_up.png"))
        icon_excel_down = QIcon(str(self.ICONS_DIR / "excel_down.png"))

        criar_formulario_button = self.create_button(
            "   Criar Formulário   ", 
            icon=icon_excel_up, 
            callback=self.formulario_excel.criar_formulario, 
            tooltip_text="Clique para criar o formulário", 
            button_size=QSize(220, 50), 
            icon_size=QSize(45, 45)
        )

        carregar_formulario_button = self.create_button(
            "Carregar Formulário", 
            icon=icon_excel_down, 
            callback=self.formulario_excel.carregar_formulario, 
            tooltip_text="Clique para carregar o formulário", 
            button_size=QSize(220, 50), 
            icon_size=QSize(45, 45)
        )

        formulario_layout.addWidget(criar_formulario_button, alignment=Qt.AlignmentFlag.AlignCenter)
        formulario_layout.addWidget(carregar_formulario_button, alignment=Qt.AlignmentFlag.AlignCenter)
        formulario_group_box.setLayout(formulario_layout)

        return formulario_group_box

    def stacked_widget_documentos(self, data):
        frame = QFrame()
        layout = QVBoxLayout()
        label = QLabel("Conteúdo de Documentos")
        layout.addWidget(label)
        frame.setLayout(layout)
        return frame

    def stacked_widget_anexos(self, data):
        frame = QFrame()
        layout = QVBoxLayout()
        label = QLabel("Conteúdo de Anexos")
        layout.addWidget(label)
        frame.setLayout(layout)
        return frame

    def stacked_widget_pncp(self, data):
        frame = QFrame()
        layout = QVBoxLayout()
        label = QLabel("Conteúdo do PNCP")
        layout.addWidget(label)
        frame.setLayout(layout)
        return frame

    def setup_layout_titulo(self):
        """Configura o layout do título com o ID do processo e a seção de consulta API."""
        layout_titulo = QHBoxLayout()

        spacer_left = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout_titulo.addSpacerItem(spacer_left)

        # Cria um layout vertical para o título e um layout horizontal para ícones e texto
        vlayout_titulo = QVBoxLayout()
        hlayout_titulo = QHBoxLayout()  # Layout horizontal para ícone esquerdo, título e ícone direito


        # Ícone à esquerda
        brasil_icon = QIcon(self.icons.get("brasil_2", None))
        image_label_esquerda = QLabel()
        image_label_esquerda.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label_esquerda.setPixmap(brasil_icon.pixmap(30, 30))
        hlayout_titulo.addWidget(image_label_esquerda)

        # Texto do título centralizado
        tipo = self.dados.get("tipo", "N/A")
        numero = self.dados.get("numero", "N/A")
        ano = self.dados.get("ano", "N/A")
        title_label = QLabel(f"{tipo} nº {numero}/{ano}", self)

        # Define o tamanho da fonte para 18 e em negrito
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hlayout_titulo.addWidget(title_label)

        # Ícone à direita
        acanto_icon = QIcon(self.icons.get("acanto", None))
        image_label_direita = QLabel()
        image_label_direita.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label_direita.setPixmap(acanto_icon.pixmap(40, 40))
        hlayout_titulo.addWidget(image_label_direita)

        # Adiciona o layout horizontal ao layout vertical do título
        vlayout_titulo.addLayout(hlayout_titulo)

        # Cria a linha divisória com espaçamento e adiciona ao layout
        linha_divisoria, spacer_baixo_linha = linha_divisoria_layout()
        vlayout_titulo.addWidget(linha_divisoria)
        vlayout_titulo.addSpacerItem(spacer_baixo_linha)

        # Cria um layout horizontal para o campo "Situação"
        situacao_om_setor_layout = QHBoxLayout()
        spacer_situacao = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        situacao_om_setor_layout.addSpacerItem(spacer_situacao)

        situacao_label = QLabel("Situação: ")
        situacao_label.setStyleSheet("font-size: 16px; font-weight: bold")
        situacao_om_setor_layout.addWidget(situacao_label)

        # Cria um combobox para a situação
        situacao_combo = QComboBox()
        situacao_combo.setStyleSheet("font-size: 14px")
        situacao_combo.addItems(["Planejamento", "Aprovado", "Sessão Pública", "Homologado", "Empenhado", "Concluído", "Arquivado"])
        situacao_combo.setCurrentText(self.dados.get('situacao', 'Planejamento'))
        situacao_om_setor_layout.addWidget(situacao_combo)

        om_layout, self.om_combo = create_selecao_om_layout(
            self.database_path,
            dados=self.dados,
            load_sigla_om_callback=load_sigla_om,
            on_om_changed_callback=on_om_changed
        )

        situacao_om_setor_layout.addLayout(om_layout)
        vlayout_titulo.addLayout(situacao_om_setor_layout)

        divisao_layout = QHBoxLayout()
        divisao_label = QLabel("  Divisão: ")
        divisao_label.setStyleSheet("font-size: 16px; font-weight: bold")
        divisao_layout.addWidget(divisao_label)

        # Criando o QComboBox editável
        setor_responsavel_combo = QComboBox()
        setor_responsavel_combo.setStyleSheet("font-size: 14px")
        # Adicionando as opções ao ComboBox
        divisoes = [
            "Divisão de Abastecimento",
            "Divisão de Finanças",
            "Divisão de Obtenção",
            "Divisão de Pagamento",
            "Divisão de Administração",
            "Divisão de Subsistência"
        ]
        setor_responsavel_combo.addItems(divisoes)

        # Definindo o texto atual com base nos dados fornecidos
        setor_responsavel_combo.setCurrentText(self.dados.get('setor_responsavel', 'Selecione a Divisão'))
        divisao_layout.addWidget(setor_responsavel_combo)

        situacao_om_setor_layout.addLayout(divisao_layout)
            # Espaçador abaixo da linha divisória
        spacer_baixo_linha = QSpacerItem(5, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        vlayout_titulo.addSpacerItem(spacer_baixo_linha)

        # Adiciona o layout vertical com título e situação ao layout principal
        layout_titulo.addLayout(vlayout_titulo)

        # Espaçador para empurrar o título e o botão "Salvar" para a direita
        spacer_right = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout_titulo.addSpacerItem(spacer_right)

        # Botão "Salvar" à direita
        add_button("Salvar", "confirm", self.save_data, layout_titulo, self.icons, tooltip="Salvar os Dados")

        return layout_titulo

    def create_sessao_publica_group(self):
        # Criação do QGroupBox para a seção Sessão Pública
        sessao_groupbox = QGroupBox("Sessão Pública:")
        sessao_groupbox.setMaximumWidth(300)
        sessao_groupbox.setStyleSheet("""
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

        group_layout = QHBoxLayout(sessao_groupbox)
        
        # Ícone de calendário ao lado do label "Defina a data:"
        calendar_icon = QIcon(self.icons.get("calendar", None))
        icon_label = QLabel()
        icon_label.setPixmap(calendar_icon.pixmap(40, 40))  # Tamanho do ícone ajustado
        
        # Label "Defina a data:"
        date_label = QLabel("Defina a data:")
        date_label.setStyleSheet("font-size: 16px")
        # Layout horizontal para o ícone e o label "Defina a data:"
        top_layout = QHBoxLayout()
        top_layout.addWidget(icon_label)
        top_layout.addWidget(date_label)
        top_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        group_layout.addLayout(top_layout)
        
        # Configuração do DateEdit com a data inicial
        self.data_edit = QDateEdit()
        self.data_edit.setStyleSheet("font-size: 14px")
        self.data_edit.setCalendarPopup(True)
        data_sessao_str = self.dados.get('data_sessao', '')
        if data_sessao_str:
            self.data_edit.setDate(QDate.fromString(data_sessao_str, "yyyy-MM-dd"))
        else:
            self.data_edit.setDate(QDate.currentDate())

        group_layout.addWidget(self.data_edit)
        
        return sessao_groupbox

    def setup_layout_conteudo(self):
        """Configura o layout de conteúdo com StackedWidget e agentes responsáveis."""
        layout_conteudo = QHBoxLayout()
        
        # Layout StackedWidget e ao lado layout agentes responsáveis
        stacked_widget = QStackedWidget(self)
        layout_conteudo.addWidget(stacked_widget)

        # Layout para agentes responsáveis ao lado do StackedWidget
        agentes_responsaveis_layout = QVBoxLayout()
        layout_conteudo.addLayout(agentes_responsaveis_layout)
        
        return layout_conteudo
       
class DispensaEletronicaWidget(QMainWindow):
    # Sinais para comunicação com o controlador
    addItem = pyqtSignal()
    deleteItem = pyqtSignal()
    salvar_tabela = pyqtSignal()
    salvar_graficos = pyqtSignal()
    salvar_print = pyqtSignal()
    loadData = pyqtSignal(str)
    # doubleClickRow = pyqtSignal(int)

    def __init__(self, icons, model, database_path, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.model = model
        self.database_path = database_path
        self.selected_row_data = None
        
        # Inicializa o proxy_model e configura o filtro
        self.proxy_model = MultiColumnFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        # Configura a interface de usuário
        self.setup_ui()

    def setup_ui(self):
        # Cria o widget principal e layout principal
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        
        # Layout para a barra de ferramentas
        top_layout = QHBoxLayout()
        self.search_bar = setup_search_bar(top_layout, self.proxy_model)
        self.setup_buttons(top_layout)
        self.main_layout.addLayout(top_layout)
        
        # Configuração da tabela
        self.setup_table_view()

        # Chama configure_table_model para aplicar as configurações à tabela
        self.configure_table_model()

        self.adjust_columns()

    def on_table_double_click(self, index):
        row = self.proxy_model.mapToSource(index).row()
        id_processo = self.model.index(row, self.model.fieldIndex("id_processo")).data()
        
        dados = self.carregar_dados_por_id(id_processo)
        if dados:
            nova_janela = EditarDadosWindow(dados, self.icons, self)
            nova_janela.show()
        else:
            QMessageBox.warning(self, "Erro", "Falha ao carregar dados para o ID do processo selecionado.")
    
    def carregar_dados_por_id(self, id_processo):
        """Carrega os dados da linha selecionada a partir do banco de dados usando `id_processo`."""
        query = f"SELECT * FROM controle_dispensas WHERE id_processo = '{id_processo}'"
        try:
            # Obtenha os dados do banco de dados
            dados = self.model.database_manager.fetch_all(query)
            
            # Converte para DataFrame caso dados seja uma lista
            if isinstance(dados, list):
                dados = pd.DataFrame(dados, columns=self.model.column_names)  # Substitua `self.model.column_names` pela lista de nomes de colunas correta
            
            # Verifica se o DataFrame não está vazio
            return dados.iloc[0].to_dict() if not dados.empty else None
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return None
        
    def editar_dados(self, registro_selecionado):        
        window = EditDataDialog(self.icons, parent=self, dados=registro_selecionado.iloc[0].to_dict())
        window.dados_atualizados.connect(self.refresh_model)  
        window.show() 

    def setup_buttons(self, layout):
        add_button("Adicionar", "plus", self.addItem, layout, self.icons, tooltip="Adicionar um novo item")  # Alteração aqui
        add_button("Excluir", "delete", self.deleteItem, layout, self.icons, tooltip="Excluir o item selecionado")
        add_button("Tabelas", "excel", self.salvar_tabela, layout, self.icons, tooltip="Salva o dataframe em um arquivo Excel")
        add_button("Gráficos", "performance", self.salvar_graficos, layout, self.icons, tooltip="Carrega dados de uma tabela")
        add_button("ConGes", "image-processing", self.salvar_print, layout, self.icons, tooltip="Abre o painel de controle do processo")

    def refresh_model(self):
        """Atualiza a tabela com os dados mais recentes do banco de dados."""
        self.model.select()

    def setup_table_view(self):
        self.table_view = QTableView(self)
        self.table_view.setModel(self.proxy_model)  # Usa o proxy_model corretamente
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.doubleClicked.connect(self.on_table_double_click)
        
        # Configurações adicionais de estilo e comportamento
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)

        self.table_view.setStyleSheet("""
            QTableView {
                font-size: 14px;
                padding: 4px;
                border: 1px solid #8AB4F7;
                border-radius: 6px;
                gridline-color: #3C3C5A;
            }
        """)
        
        # Define CenterAlignDelegate para centralizar o conteúdo em todas as colunas
        center_delegate = CenterAlignDelegate(self.table_view)
        for column in range(self.model.columnCount()):
            self.table_view.setItemDelegateForColumn(column, center_delegate)

        # Aplica CustomItemDelegate à coluna "situação" para exibir ícones
        situacao_index = self.model.fieldIndex('situacao')
        self.table_view.setItemDelegateForColumn(situacao_index, CustomItemDelegate(self.icons, self.table_view, self.model))

        self.main_layout.addWidget(self.table_view)

    def configure_table_model(self):
        self.proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self.update_column_headers()
        self.hide_unwanted_columns()

    def update_column_headers(self):
        titles = {0: "Status", 1: "ID Processo", 5: "NUP", 7: "Objeto", 17: "OM"}
        for column, title in titles.items():
            self.model.setHeaderData(column, Qt.Orientation.Horizontal, title)

    def hide_unwanted_columns(self):
        visible_columns = {0, 1, 5, 7, 17}
        for column in range(self.model.columnCount()):
            if column not in visible_columns:
                self.table_view.hideColumn(column)

    def adjust_columns(self):
        # Ajustar automaticamente as larguras das colunas ao conteúdo
        self.table_view.resizeColumnsToContents()
        QTimer.singleShot(1, self.apply_custom_column_sizes) 

    def apply_custom_column_sizes(self):
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(17, QHeaderView.ResizeMode.Fixed)

        header.resizeSection(0, 150)        
        header.resizeSection(1, 130)
        header.resizeSection(5, 170)
        header.resizeSection(17, 100)

class CenterAlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter

class CustomItemDelegate(QStyledItemDelegate):
    def __init__(self, icons, parent=None, model=None):
        super().__init__(parent)
        self.icons = icons
        self.model = model

    def paint(self, painter, option, index):
        # Verifica se estamos na coluna de situação
        if index.column() == self.model.fieldIndex('situacao'):
            situacao = index.data(Qt.ItemDataRole.DisplayRole)
            # Define o mapeamento de ícones
            icon_key = {
                'Planejamento': 'business',
                'Aprovado': 'verify_menu',
                'Sessão Pública': 'session',
                'Homologado': 'deal',
                'Empenhado': 'emenda_parlamentar',
                'Concluído': 'aproved',
                'Arquivado': 'archive'
            }.get(situacao)

            # Desenha o ícone se encontrado no mapeamento
            if icon_key and icon_key in self.icons:
                icon = self.icons[icon_key]
                icon_size = 24
                icon_rect = QRect(option.rect.left() + 5,
                                  option.rect.top() + (option.rect.height() - icon_size) // 2,
                                  icon_size, icon_size)
                painter.drawPixmap(icon_rect, icon.pixmap(icon_size, icon_size))

                # Desenha o texto ao lado do ícone
                text_rect = QRect(icon_rect.right() + 5, option.rect.top(),
                                  option.rect.width() - icon_size - 10, option.rect.height())
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, situacao)
        else:
            # Desenha normalmente nas outras colunas
            super().paint(painter, option, index)