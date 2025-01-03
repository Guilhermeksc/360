from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from pathlib import Path
from datetime import datetime
import sqlite3

class AddItemDialog(QDialog):
    def __init__(self, icons, database_path, controle_om, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.database_path = database_path
        self.controle_om = controle_om
        self.om_details = {}  # Inicializa como dicionário vazio para evitar erros
        self.setWindowTitle("Adicionar Item")
        self.setWindowIcon(self.icons["plus"])

        # self.setFixedSize(550, 250)
        # self.database_manager = DatabaseManager(self.database_path)
        self.layout = QVBoxLayout(self)
        self.setStyleSheet("QWidget { font-size: 14px; }")

        self.setup_ui()
        self.load_sigla_om()  # Preenche self.om_details com dados do banco
        self.load_next_numero()

    def setup_ui(self):
        self.tipo_cb, self.numero_le, self.ano_le = self.setup_first_line()
        self.objeto_le = self.setup_third_line()
        self.nup_le, self.sigla_om_cb = self.setup_fourth_line()
        self.material_radio, self.servico_radio = self.setup_fifth_line()
        self.setup_save_button()

    def setup_first_line(self):
        hlayout = QHBoxLayout()
        tipo_cb = QComboBox()
        numero_le = QLineEdit()
        ano_le = QLineEdit()

        [tipo_cb.addItem(option[0]) for option in [("Pregão Eletrônico (PE)", "Pregão Eletrônico")]]
        tipo_cb.setCurrentText("Pregão Eletrônico (PE)")
        numero_le.setValidator(QIntValidator(1, 99999))
        ano_le.setValidator(QIntValidator(1000, 9999))
        ano_le.setText(str(datetime.now().year))

        hlayout.addWidget(QLabel("Tipo:"))
        hlayout.addWidget(tipo_cb)
        hlayout.addWidget(QLabel("Número:"))
        hlayout.addWidget(numero_le)
        hlayout.addWidget(QLabel("Ano:"))
        hlayout.addWidget(ano_le)
        self.layout.addLayout(hlayout)

        return tipo_cb, numero_le, ano_le

    def setup_third_line(self):
        hlayout = QHBoxLayout()
        objeto_le = QLineEdit()
        objeto_le.setPlaceholderText("Exemplo: 'Material de Limpeza' (Utilizar no máximo 3 palavras)")
        hlayout.addWidget(QLabel("Objeto:"))
        hlayout.addWidget(objeto_le)
        self.layout.addLayout(hlayout)
        return objeto_le

    def setup_fourth_line(self):
        hlayout = QHBoxLayout()
        nup_le = QLineEdit()
        sigla_om_cb = QComboBox()
        nup_le.setPlaceholderText("Exemplo: '00000.00000/0000-00'")
        hlayout.addWidget(QLabel("Nup:"))
        hlayout.addWidget(nup_le)
        hlayout.addWidget(QLabel("OM:"))
        hlayout.addWidget(sigla_om_cb)
        self.layout.addLayout(hlayout)
        return nup_le, sigla_om_cb

    def setup_fifth_line(self):
        hlayout = QHBoxLayout()
        material_radio = QRadioButton("Material")
        servico_radio = QRadioButton("Serviço")
        group = QButtonGroup(self)
        group.addButton(material_radio)
        group.addButton(servico_radio)
        material_radio.setChecked(True)

        hlayout.addWidget(QLabel("Material/Serviço:"))
        hlayout.addWidget(material_radio)
        hlayout.addWidget(servico_radio)
        self.layout.addLayout(hlayout)
        return material_radio, servico_radio

    def setup_save_button(self):
        btn = QPushButton("Adicionar Item")
        btn.clicked.connect(self.on_save)
        self.layout.addWidget(btn)

    def on_save(self):
        data = self.get_data()
        try:
            if self.check_id_exists(data['id_processo']):
                res = QMessageBox.question(
                    self, "Confirmação",
                    "ID do processo já existe. Deseja sobrescrever?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if res == QMessageBox.StandardButton.Yes:
                    self.accept()  # Substitui o diálogo aceitar com a sobreposição
            else:
                self.accept()  # Aceita normalmente se o ID do processo não existir
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                QMessageBox.warning(self, "Erro", "A tabela 'controle_licitacao' não existe. Por favor, atualize a interface gráfica do módulo.")
            else:
                QMessageBox.warning(self, "Erro", f"Ocorreu um erro: {str(e)}")

    def check_id_exists(self, id_processo):
        query = "SELECT 1 FROM controle_licitacao WHERE id_processo = ?"
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (id_processo,))
                return cursor.fetchone() is not None
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                QMessageBox.warning(self, "Erro", "A tabela 'controle_licitacao' não existe. Por favor, crie a tabela primeiro.")
            else:
                raise 

    def load_next_numero(self):
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                # Converte o campo `numero` em um inteiro para garantir a comparação correta
                cursor.execute("SELECT MAX(CAST(numero AS INTEGER)) FROM controle_licitacao")
                max_number = cursor.fetchone()[0]
                next_number = 1 if max_number is None else int(max_number) + 1
                self.numero_le.setText(str(next_number))
        except Exception as e:
            print(f"Erro ao carregar o próximo número: {e}")

    def get_data(self):
        # Define o valor de 'sigla_om' como "CeIMBra" se a seleção atual estiver vazia
        sigla_selected = self.sigla_om_cb.currentText() or "CeIMBra"

        # Define valores padrão para 'orgao_responsavel' e 'uasg' caso 'sigla_selected' não esteja em 'self.om_details'
        orgao_responsavel = self.om_details.get(sigla_selected, {}).get('orgao_responsavel', "Orgão Padrão")
        uasg = self.om_details.get(sigla_selected, {}).get('uasg', "000000")

        material_servico = "Material" if self.material_radio.isChecked() else "Serviço"
        tipo_de_processo = self.tipo_cb.currentText()
        com_disputa = "Sim"  
        pesquisa_preco = "Não"  
        atividade_custeio = "Não"  

        data = {
            'tipo': tipo_de_processo,
            'numero': self.numero_le.text(),
            'ano': self.ano_le.text(),
            'nup': self.nup_le.text(),
            'objeto': self.objeto_le.text(),
            'sigla_om': sigla_selected,
            'orgao_responsavel': orgao_responsavel,
            'uasg': uasg,
            'material_servico': material_servico,
            'com_disputa': com_disputa,
            'pesquisa_preco': pesquisa_preco,
            'atividade_custeio': atividade_custeio
        }

        # Mapeamento do tipo de processo para o nome interno
        tipo_map = {
            "Pregão Eletrônico (PE)": ("PE", "Pregão Eletrônico"),
        }
        
        if tipo_de_processo in tipo_map:
            abreviatura, nome_interno = tipo_map[tipo_de_processo]
            data['tipo'] = nome_interno
            data['id_processo'] = f"{abreviatura} {data['numero']}/{data['ano']}"
        else:
            data['tipo'] = "Tipo Desconhecido"
            data['id_processo'] = f"Desconhecido {data['numero']}/{data['ano']}"

        return data
    
    def load_sigla_om(self):
        try:
            with sqlite3.connect(self.controle_om) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT sigla_om, orgao_responsavel, uasg FROM controle_om ORDER BY sigla_om")
                self.om_details = {"CeIMBra": {"orgao_responsavel": "Centro de Intendência da Marinha em Brasília", "uasg": "787010"}}
                self.sigla_om_cb.clear()
                ceimbra_found = False
                default_index = 0

                for index, row in enumerate(cursor.fetchall()):
                    sigla, orgao, uasg = row
                    self.sigla_om_cb.addItem(sigla)
                    self.om_details[sigla] = {"orgao_responsavel": orgao, "uasg": uasg}
                    if sigla == "CeIMBra":
                        ceimbra_found = True
                        default_index = index

                if ceimbra_found:
                    self.sigla_om_cb.setCurrentIndex(default_index)
                else:
                    self.sigla_om_cb.setCurrentText("CeIMBra")

        except Exception as e:
            print(f"Erro ao carregar siglas de OM: {e}")
            # Garantindo a existência de "CeIMBra" em caso de erro de carregamento
            self.om_details = {"CeIMBra": {"orgao_responsavel": "Centro de Intendência da Marinha em Brasília", "uasg": "787010"}}
            self.sigla_om_cb.addItem("CeIMBra")
            self.sigla_om_cb.setCurrentText("CeIMBra")
