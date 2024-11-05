from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from modules.utils.add_button import add_button, add_button_func
from modules.utils.consulta_api import setup_consulta_api
from modules.dispensa_eletronica.dialogs.edit_data.widgets.formulario import setup_formularios
from modules.dispensa_eletronica.dialogs.edit_data.widgets.gerar_documentos import ConsolidarDocumentos
from modules.dispensa_eletronica.dialogs.edit_data.widgets.sigdem_layout import create_GrupoSIGDEM, create_utilidades_group
from modules.dispensa_eletronica.dialogs.edit_data.widgets.setor_responsavel import create_dados_responsavel_contratacao_group
from modules.dispensa_eletronica.dialogs.edit_data.widgets.contratacao import create_contratacao_group, create_info_comprasnet
from modules.dispensa_eletronica.dialogs.edit_data.widgets.classificacao_orcamentaria import create_classificacao_orcamentaria_group
from modules.utils.linha_layout import linha_divisoria_layout
from modules.utils.select_om import create_selecao_om_layout, load_sigla_om, on_om_changed
from modules.utils.agentes_responsaveis_layout import create_agentes_responsaveis_layout
from pathlib import Path
from config.paths import CONTROLE_DADOS
import json

CONFIG_FILE = 'config.json'

def load_config_path_id():
    if not Path(CONFIG_FILE).exists():
        return {}
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)


class EditarDadosWindow(QMainWindow):
    save_data_signal = pyqtSignal(dict)
    sinalFormulario = pyqtSignal()
    status_atualizado = pyqtSignal(str, str)

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
        self.setFixedSize(1150, 780)
        
        self.database_path = CONTROLE_DADOS
        # Inicialize a instância de consolidador
        self.status_label = QLabel(self)
        self.config = load_config_path_id()
        self.pasta_base = Path(self.config.get('pasta_base', str(Path.home() / 'Desktop')))
        # Inicialize a instância de ConsolidarDocumentos e conecte o sinal
        self.consolidador = ConsolidarDocumentos(self.dados)
        self.consolidador.status_atualizado.connect(self.atualizar_status)

        self.setup_ui()


    def atualizar_status(self, status_texto, icone_path):
        """Atualiza o texto e o ícone do status_label"""
        # Print para verificar a recepção do sinal
        print(f"Received signal in atualizar_status with status_texto: '{status_texto}', icone_path: '{icone_path}'")
        
        self.status_label.setText(status_texto)
        icon_folder = QIcon(icone_path)
        icon_pixmap = icon_folder.pixmap(30, 30)
        self.icon_label.setPixmap(icon_pixmap)  # Atualiza o pixmap do ícone

    def setup_ui(self):
        # Configura o widget principal e define o fundo preto e borda
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Configuração do layout principal com margens e espaçamento zero
        self.central_layout = QHBoxLayout(main_widget)

        # Layout esquerdo
        Left_layout = QVBoxLayout()
        layout_titulo = self.setup_layout_titulo()
        Left_layout.addLayout(layout_titulo)
        nav_frame = self.create_navigation_layout()
        Left_layout.addWidget(nav_frame)
        Left_layout.addWidget(self.stacked_widget)
        self.central_layout.addLayout(Left_layout)

        # Configura o layout da consulta API
        group_box_consulta_api, self.cnpj_edit, self.sequencial_edit = setup_consulta_api(parent=self, icons=self.icons)
        group_box_agentes = create_agentes_responsaveis_layout(self.database_path)
        group_box_sessao = self.create_sessao_publica_group()

        # Cria um widget para o Right_layout e define o fundo preto
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            background-color: #12131D;
            border: 2px solid #12131D;
            border-radius: 15px;
        """)
        Right_layout = QVBoxLayout(right_widget)
        Right_layout.addWidget(group_box_consulta_api)
        Right_layout.addWidget(group_box_agentes)
        Right_layout.addWidget(group_box_sessao)

        self.central_layout.addWidget(right_widget)

        # Configuração dos widgets no QStackedWidget
        self.setup_stacked_widgets()

    def verificar_pastas(self, pasta_base):
        # Acesse o id_processo a partir de self.dados
        id_processo = self.dados.get('id_processo', 'desconhecido').replace("/", "-")  # Use uma chave de dicionário
        objeto = self.dados.get('objeto', 'objeto_desconhecido').replace("/", "-")  # Acessando corretamente o objeto

        base_path = pasta_base / f'{id_processo} - {objeto}'

        pastas_necessarias = [
            base_path / '1. Autorizacao',
            base_path / '2. CP e anexos',
            base_path / '3. Aviso',
            base_path / '2. CP e anexos' / 'DFD',
            base_path / '2. CP e anexos' / 'DFD' / 'Anexo A - Relatorio Safin',
            base_path / '2. CP e anexos' / 'DFD' / 'Anexo B - Especificações e Quantidade',
            base_path / '2. CP e anexos' / 'TR',
            base_path / '2. CP e anexos' / 'TR' / 'Pesquisa de Preços',
            base_path / '2. CP e anexos' / 'Declaracao de Adequação Orçamentária',
            base_path / '2. CP e anexos' / 'Declaracao de Adequação Orçamentária' / 'Relatório do PDM-Catser',
            base_path / '2. CP e anexos' / 'Justificativas Relevantes',
        ]

        # Verifica se todas as pastas necessárias existem
        pastas_existentes = all(pasta.exists() for pasta in pastas_necessarias)
        return pastas_existentes

    def create_navigation_layout(self):
        # Criação do frame que conterá o nav_layout e aplicará a borda inferior
        nav_frame = QFrame()
        nav_frame.setStyleSheet("QFrame {border-bottom: 5px solid #13141F;}")

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

        nav_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Verifica se as pastas existem e define o ícone e status
        pastas_existentes = self.verificar_pastas(self.pasta_base)
        status_text = "Pastas encontradas" if pastas_existentes else "Pastas não encontradas"
        icon_key = "folder_v" if pastas_existentes else "folder_x"
        icon = self.icons.get(icon_key)
        self.status_label = QLabel(status_text)
        self.icon_label = QLabel()
        if icon and isinstance(icon, QIcon):
            icon_pixmap = icon.pixmap(30, 30)
            self.icon_label.setPixmap(icon_pixmap)

        # Layout de status com ícone e texto
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.icon_label)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        nav_layout.addLayout(status_layout)

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

        info_contratacao_layout = QVBoxLayout()

        self.contratacao_layout, self.contratacao_widgets = create_contratacao_group(self.dados)

        info_comprasnet_layout = create_info_comprasnet(data)
        info_contratacao_layout.addWidget(self.contratacao_layout)
        info_contratacao_layout.addWidget(info_comprasnet_layout)

        classificacao_orcamentaria_formulario_layout = QVBoxLayout()
        self.classificacao_orcamentaria_group_box, self.widgets_classificacao_orcamentaria = create_classificacao_orcamentaria_group(self.dados)
        
        group_box_formulario = setup_formularios(parent=self, icons=self.icons)
        classificacao_orcamentaria_formulario_layout.addWidget(self.classificacao_orcamentaria_group_box)
        classificacao_orcamentaria_formulario_layout.addWidget(group_box_formulario)

        hbox_top_layout.addLayout(info_contratacao_layout)
        hbox_top_layout.addLayout(classificacao_orcamentaria_formulario_layout)

        layout.addLayout(hbox_top_layout)
        frame.setLayout(layout)

        return frame

    def stacked_widget_responsaveis(self, data):
        frame = QFrame()
        layout = QVBoxLayout()
        self.setor_responsavel_layout, self.widget_setor_responsavel = create_dados_responsavel_contratacao_group(data)
        layout.addLayout(self.setor_responsavel_layout)
        frame.setLayout(layout)
        return frame

    def stacked_widget_documentos(self, data):
        frame = QFrame()
        layout = QVBoxLayout()

        # Configuração de parâmetros
        nome_pasta = f"{self.consolidador.id_processo.replace('/', '-')}_{self.consolidador.objeto.replace('/', '-')}"
        icons_dir = self.consolidador.ICONS_DIR
        criar_e_abrir_pasta = self.consolidador.criar_e_abrir_pasta
        alterar_diretorio_base = self.consolidador.alterar_diretorio_base
        editar_modelo = self.consolidador.editar_modelo

        # Chama `create_gerar_documentos_group` sem passar o parâmetro `consolidador`
        self.gerar_documentos = self.consolidador.create_gerar_documentos_group(
            handle_gerar_autorizacao=self.consolidador.gerar_autorizacao,
            handle_gerar_autorizacao_sidgem=None,  # Removido ou definido como None
            handle_gerar_comunicacao_padronizada=self.consolidador.gerar_comunicacao_padronizada,
            handle_gerar_comunicacao_padronizada_sidgem=None,  # Removido ou definido como None
            handle_gerar_aviso_dispensa=self.consolidador.gerar_aviso_dispensa,
            handle_gerar_aviso_dispensa_sidgem=None  # Removido ou definido como None
        )
        self.sigdem_group = create_GrupoSIGDEM(self.dados)

        self.utilidade_group = create_utilidades_group(
            pasta_base=self.pasta_base,
            nome_pasta=nome_pasta,
            icons_dir=icons_dir,
            criar_e_abrir_pasta=criar_e_abrir_pasta,
            alterar_diretorio_base=alterar_diretorio_base,
            editar_modelo=editar_modelo
        )

        # Adiciona o layout gerado ao layout principal
        layout.addLayout(self.gerar_documentos)
        layout.addWidget(self.sigdem_group)
        layout.addLayout(self.utilidade_group)
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
        add_button_func("Salvar", "confirm", self.save_data, layout_titulo, self.icons, tooltip="Salvar os Dados")

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

            
    def save_data(self):
        # Coleta os dados dos widgets de contratação
        data_to_save = {
            'id_processo': self.dados.get('id_processo'),
            'tipo': self.dados.get('tipo'),
            'numero': self.dados.get('numero'),
            'ano': self.dados.get('ano'),
            'objeto': self.contratacao_widgets['objeto_edit'].text(),
            'nup': self.contratacao_widgets['nup_edit'].text(),
            'material_servico': 'Material' if self.contratacao_widgets['radio_material'].isChecked() else 'Serviço',
            'vigencia': self.contratacao_widgets['vigencia_combo'].currentText(),
            'criterio_julgamento': self.contratacao_widgets['criterio_combo'].currentText(),
            'com_disputa': 'Sim' if self.contratacao_widgets['radio_disputa_sim'].isChecked() else 'Não',
            'pesquisa_preco': 'Sim' if self.contratacao_widgets['radio_pesquisa_sim'].isChecked() else 'Não'
        }
        
        # Coleta os dados dos widgets de classificação orçamentária
        data_to_save.update({
            'valor_total': self.widgets_classificacao_orcamentaria['valor_total'].text(),
            'acao_interna': self.widgets_classificacao_orcamentaria['acao_interna'].text(),
            'fonte_recursos': self.widgets_classificacao_orcamentaria['fonte_recursos'].text(),
            'natureza_despesa': self.widgets_classificacao_orcamentaria['natureza_despesa'].text(),
            'unidade_orcamentaria': self.widgets_classificacao_orcamentaria['unidade_orcamentaria'].text(),
            'ptres': self.widgets_classificacao_orcamentaria['ptres'].text(),
            'atividade_custeio': 'Sim' if self.widgets_classificacao_orcamentaria['radio_custeio_sim'].isChecked() else 'Não'
        })

        data_to_save.update({
            'cp': self.widget_setor_responsavel['cp_edit'].text(),
            'cod_par': self.widget_setor_responsavel['par_edit'].text(),
            'prioridade_par': self.widget_setor_responsavel['prioridade_combo'].currentText(),
            'endereco': self.widget_setor_responsavel['endereco_edit'].text(),
            'cep': self.widget_setor_responsavel['cep_edit'].text(),
            'email': self.widget_setor_responsavel['email_edit'].text(),
            'telefone': self.widget_setor_responsavel['telefone_edit'].text(),
            'dias_recebimento': self.widget_setor_responsavel['dias_edit'].text(),
            'horario_recebimento': self.widget_setor_responsavel['horario_edit'].text(),
            'justificativa': self.widget_setor_responsavel['justificativa_edit'].toPlainText()
        })
        
        # Debug para verificar o conteúdo de data_to_save
        print("Dados para salvar:", data_to_save)

        # Emissão do sinal para salvar os dados
        self.save_data_signal.emit(data_to_save)
        