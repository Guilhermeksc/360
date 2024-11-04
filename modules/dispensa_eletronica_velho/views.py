from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from modules.utils.search_bar import setup_search_bar, MultiColumnFilterProxyModel
from modules.utils.add_button import add_button, create_button
from config.styles.styless import apply_table_custom_style
from modules.dispensa_eletronica.dialogs.editar_dados import EditDataDialog
from pathlib import Path
import pandas as pd

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
            QMainWindow {
                font-size: 16px;
            }
        """)

        self.widgets_map = {}
        
        # Configurações da janela
        self.setWindowTitle("Editar Dados")
        self.setWindowIcon(self.icons.get("edit", None))
        self.setFixedSize(1250, 720)
        
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
        
        navigation_layout = self.create_navigation_layout()
        Left_layout.addLayout(navigation_layout)

        # Adiciona o QStackedWidget abaixo do layout de navegação
        Left_layout.addWidget(self.stacked_widget)
        
        self.central_layout.addLayout(Left_layout)

        # Layout direito
        Right_layout = QVBoxLayout()
        layout_consulta_api = self.setup_consulta_api()
        Right_layout.addWidget(layout_consulta_api)
        self.central_layout.addLayout(Right_layout)

        # Configuração dos widgets no QStackedWidget
        self.setup_stacked_widgets()

    def create_navigation_layout(self):
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(0)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        buttons = [
            ("Informações", "Informações"),
            ("Setor Responsável", "Setor Responsável"),
            ("Documentos", "Documentos"),
            ("Anexos", "Anexos"),
            ("PNCP", "PNCP"),
        ]

        for text, name in buttons:
            button = QPushButton(text, self)
            button.setObjectName(name)
            button.setProperty("class", "nav-button")
            button.clicked.connect(lambda _, n=name, b=button: self.on_navigation_button_clicked(n, b))
            nav_layout.addWidget(button)

        # Adiciona um espaço expansivo no final para empurrar os botões para a esquerda
        nav_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.setStyleSheet("""
            QPushButton[class="nav-button"] {
                background-color: #181928;
                color: #8BE9D9;
                border: none;
                font-size: 14px;
                border-top: 10px solid #181928;
            }
            QPushButton[class="nav-button"]:hover {
                background-color: #13141F;
                color: white;
                font-size: 14px;
                border-top: 10px solid #13141F;
            }
            QPushButton[class="nav-button selected"] {
                background-color: #000000;
                color: white;
                border-top: 3px solid #FF79C6;
                font-weight: bold;
                font-size: 14px;
            }
        """)


        return nav_layout

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
            "PNCP": self.stacked_widget_pncp(data),
        }

        # Adiciona cada widget ao QStackedWidget
        for name, widget in self.widgets_map.items():
            self.stacked_widget.addWidget(widget)

    def stacked_widget_info(self, data):
        frame = QFrame()
        layout = QVBoxLayout()
        hbox_top_layout = QHBoxLayout()
        contratacao_layout = self.create_contratacao_group(data)
        hbox_top_layout.addLayout(contratacao_layout)
        layout.addLayout(hbox_top_layout)
        frame.setLayout(layout)
        return frame

    # Exemplo de função para criar o grupo de contratação
    def create_contratacao_group(self, data):
        contratacao_layout = QVBoxLayout()

        # Objeto
        self.objeto_edit = QLineEdit(data['objeto'])

        # Criando um layout horizontal para o campo de entrada de texto e o ícone
        objeto_layout = QHBoxLayout()

        objeto_label = QLabel("Objeto:")
        objeto_layout.addWidget(objeto_label)
        objeto_layout.addWidget(self.objeto_edit)

        # Criando o ícone
        icon_label = QLabel()
        icon = QIcon(self.icons.get("prioridade", None))
        icon_pixmap = icon.pixmap(27, 27)  # Definindo o tamanho do ícone
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(30, 30)

        # Adicionando o ícone ao layout
        objeto_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignRight)
        # Adicionando o layout horizontal diretamente ao layout principal de contratação
        contratacao_layout.addLayout(objeto_layout)

        # Configuração Situação
        situacao_layout = QHBoxLayout()
        situacao_label = QLabel("Situação:")
        self.situacao_edit = self.create_combo_box(data.get('situacao', 'Planejamento'), ["Planejamento", "Aprovado", "Sessão Pública", "Homologado", "Empenhado", "Concluído", "Arquivado"], 185, 35)
        situacao_layout.addWidget(situacao_label)
        situacao_layout.addWidget(self.situacao_edit)
        contratacao_layout.addLayout(situacao_layout)

        # Adiciona outros layouts ao layout de contratação
        self.nup_edit = QLineEdit(data['nup'])
        contratacao_layout.addLayout(self.create_layout("NUP:", self.nup_edit))

        # Configuração de Material/Serviço na mesma linha
        material_layout = QHBoxLayout()
        material_label = QLabel("Material/Serviço:")
        self.material_edit = self.create_combo_box(data.get('material_servico', 'Material'), ["Material", "Serviço"], 185, 35)
        material_layout.addWidget(material_label)
        material_layout.addWidget(self.material_edit)
        contratacao_layout.addLayout(material_layout)

        # Configuração da Data da Sessão na mesma linha
        data_layout = QHBoxLayout()
        data_label = QLabel("Data da Sessão Pública:")
        self.data_edit = QDateEdit()
        # self.data_edit.setFixedWidth(120)
        self.data_edit.setCalendarPopup(True)
        data_sessao_str = data.get('data_sessao', '')
        if data_sessao_str:
            self.data_edit.setDate(QDate.fromString(data_sessao_str, "yyyy-MM-dd"))
        else:
            self.data_edit.setDate(QDate.currentDate())
        data_layout.addWidget(data_label)
        data_layout.addWidget(self.data_edit)
        contratacao_layout.addLayout(data_layout)

        previsao_contratacao_layout = QHBoxLayout()
        previsao_contratacao_label = QLabel("Previsão da Contratação:")
        self.previsao_contratacao_edit = QDateEdit()
        # self.previsao_contratacao_edit.setFixedWidth(120)
        self.previsao_contratacao_edit.setCalendarPopup(True)
        previsao_contratacao_str = data.get('previsao_contratacao', '')
        if previsao_contratacao_str:
            self.previsao_contratacao_edit.setDate(QDate.fromString(previsao_contratacao_str, "yyyy-MM-dd"))
        else:
            self.previsao_contratacao_edit.setDate(QDate.currentDate())
        previsao_contratacao_layout.addWidget(previsao_contratacao_label)
        previsao_contratacao_layout.addWidget(self.previsao_contratacao_edit)
        contratacao_layout.addLayout(previsao_contratacao_layout)

        # Vigência
        self.vigencia_edit = QComboBox()
        self.vigencia_edit.setEditable(True)
        for i in range(1, 13):
            self.vigencia_edit.addItem(f"{i} ({self.number_to_text(i)}) meses")
        vigencia = data.get('vigencia', '2 (dois) meses')
        self.vigencia_edit.setCurrentText(vigencia)
        contratacao_layout.addLayout(self.create_layout("Vigência:", self.vigencia_edit))

        # Configuração de Critério de Julgamento na mesma linha
        criterio_layout = QHBoxLayout()
        criterio_label = QLabel("Critério Julgamento:")
        self.criterio_edit = self.create_combo_box(data.get('criterio_julgamento', 'Menor Preço'), ["Menor Preço", "Maior Desconto"], 185, 30)
        criterio_layout.addWidget(criterio_label)
        criterio_layout.addWidget(self.criterio_edit)
        contratacao_layout.addLayout(criterio_layout)

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

        cnpj_layout = QHBoxLayout()

        # Criação do campo de texto com o valor '00394502000144'
        self.cnpj_matriz_edit = QLineEdit('00394502000144')
        cnpj_layout.addLayout(self.create_layout("CNPJ Matriz:", self.cnpj_matriz_edit))

        # Adicionando o campo CNPJ ao layout principal
        contratacao_layout.addLayout(cnpj_layout)

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

    def number_to_text(self, number):
        numbers_in_words = ["um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze"]
        return numbers_in_words[number - 1] 

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
            
    def stacked_widget_responsaveis(self, data):
        frame = QFrame()
        layout = QVBoxLayout()
        label = QLabel("Conteúdo do Setor Responsável")
        layout.addWidget(label)
        frame.setLayout(layout)
        return frame

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
        
    def setup_consulta_api(self):
        """Configura o layout para consulta à API com campos de CNPJ e Sequencial PNCP."""
        # Cria o GroupBox para a consulta API
        group_box = QGroupBox("Consulta API", self)
        layout = QVBoxLayout(group_box)

        # Label CNPJ Matriz
        label_cnpj = QLabel("CNPJ Matriz:", self)
        layout.addWidget(label_cnpj)

        # Campo de edição para o CNPJ com valor pré-preenchido
        self.cnpj_edit = QLineEdit(self)
        self.cnpj_edit.setText("00394502000144")  # Valor pré-preenchido
        layout.addWidget(self.cnpj_edit)

        # Label Sequencial PNCP
        label_sequencial = QLabel("Sequencial PNCP:", self)
        layout.addWidget(label_sequencial)

        # Campo de edição para o Sequencial PNCP
        self.sequencial_edit = QLineEdit(self)
        self.sequencial_edit.setPlaceholderText("Digite o Sequencial PNCP")
        layout.addWidget(self.sequencial_edit)

        # Botão de consulta usando a função create_button com ícone obtido diretamente de self.icons["api"]
        btn_consultar = create_button(
            text="Consultar",
            icon=self.icons.get("api", None),  # Ícone obtido diretamente
            callback=self.consultar_api,
            tooltip_text="Clique para consultar dados usando o CNPJ e Sequencial PNCP",
            parent=self
        )
        layout.addWidget(btn_consultar)

        return group_box

    
    def consultar_api(self):
        """Função de exemplo para consulta à API. Substitua pela lógica real."""
        cnpj = self.cnpj_edit.text()
        print(f"Consultando API com o CNPJ: {cnpj}")
        # Implementar a lógica de consulta à API aqui

    def setup_layout_titulo(self):
        """Configura o layout do título com o ID do processo e a seção de consulta API."""
        layout_titulo = QHBoxLayout()

        brasil_icon = QIcon(self.icons.get("brasil_2", None))
        image_label_esquerda = QLabel()
        image_label_esquerda.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label_esquerda.setPixmap(brasil_icon.pixmap(30, 30))
        layout_titulo.addWidget(image_label_esquerda)
        #        
        tipo = self.dados.get("tipo", "N/A")
        numero = self.dados.get("numero", "N/A")
        ano = self.dados.get("ano", "N/A")
        title_label = QLabel(f"{tipo} nº {numero}/{ano}", self)
        
        # Define o tamanho da fonte para 18 e em negrito
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title_label.setFont(font)

        layout_titulo.addWidget(title_label)
          
        add_button("Salvar", "confirm", self.save_data, layout_titulo, self.icons, tooltip="Salvar os Dados")

        # Layout consulta API em V dentro do título
        consulta_api_layout = QVBoxLayout()
        
        layout_titulo.addLayout(consulta_api_layout)
        
        return layout_titulo

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