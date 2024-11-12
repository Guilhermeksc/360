# dashboard_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QPushButton
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize

class DashboardWidget(QWidget):
    def __init__(self, icons):
        super().__init__()
        self.icons = icons  # Recebe o dicionário de ícones
        self.setup_ui()

    def setup_ui(self):
        # Layout principal vertical para o dashboard
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Configura o ícone e o título do dashboard
        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dash_icon_button = QPushButton()  # Cria um botão para exibir o ícone
        dash_icon_button.setIcon(self.icons["dash_titulo"])  # Define o ícone
        dash_icon_button.setIconSize(QSize(40, 40))  # Define o tamanho do ícone
        dash_icon_button.setFlat(True)  # Remove a borda do botão para exibir só o ícone
        title_layout.addWidget(dash_icon_button)

        # Título do dashboard
        title_label = QLabel("Dashboard Licitação")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_layout.addWidget(title_label)

        # Adiciona o layout de título e ícone ao layout principal
        main_layout.addLayout(title_layout)

        # Layout horizontal para as três seções principais
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(20)

        # Configura o QGroupBox da seção "Efetivo" com subseções
        efetivo_groupbox = QGroupBox("Efetivo")
        efetivo_layout = QHBoxLayout(efetivo_groupbox)
        efetivo_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        efetivo_groupbox.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3C3C5A;
                border-radius: 10px;
                font-size: 20px;
                font-weight: bold;
                color: white;
                margin-top: 13px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                padding: 0 3px;
            }
        """)
        efetivo_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        efetivo_layout.addLayout(self.create_subsection_layout("Efetivo Atual", "efetivo", "10"))
        efetivo_layout.addLayout(self.create_subsection_layout("Oficiais", "grid", "2"))
        efetivo_layout.addLayout(self.create_subsection_layout("Licitação", "grid", "3"))
        efetivo_layout.addLayout(self.create_subsection_layout("Contratos", "grid", "3"))
        efetivo_layout.addLayout(self.create_subsection_layout("Contratação Direta", "grid", "2"))


        # Configura o layout da seção "Distribuição por patente"
        patente_groupbox = QGroupBox("Posto/Graduação")
        patente_layout = QVBoxLayout(patente_groupbox)
        patente_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        patente_groupbox.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3C3C5A;
                border-radius: 10px;
                font-size: 20px;
                font-weight: bold;
                color: white;
                margin-top: 13px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                padding: 0 3px;
            }
        """)
        patente_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        patente_layout.addLayout(self.create_subsection_hlayout("Oficiais", "oficial", "2"))
        patente_layout.addLayout(self.create_subsection_hlayout("Suboficiais", "suboficial", "4"))
        patente_layout.addLayout(self.create_subsection_hlayout("1º Sargento", "sg1", "0"))
        patente_layout.addLayout(self.create_subsection_hlayout("2º Sargento", "sg2", "2"))
        patente_layout.addLayout(self.create_subsection_hlayout("3º Sargento", "sg3", "1"))
        patente_layout.addLayout(self.create_subsection_hlayout("Cabo", "cb", "0"))
        patente_layout.addLayout(self.create_subsection_hlayout("Marinheiro", "mn", "1"))
        # Adicione widgets específicos ao layout patente, se necessário

        # Configura o layout da seção "Controle"
        controle_groupbox = QGroupBox("Controle")
        controle_layout = QVBoxLayout(controle_groupbox)
        controle_groupbox.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3C3C5A;
                border-radius: 10px;
                font-size: 20px;
                font-weight: bold;
                color: white;
                margin-top: 13px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                padding: 0 3px;
            }
        """)
        controle_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        controle_layout.addLayout(self.create_subsection_layout("Dispensa Eletrônica", "grid", "3"))
        # Adicione widgets específicos ao layout controle, se necessário

        # Adiciona os layouts verticais ao layout horizontal principal
        efetivo_groupbox.setLayout(efetivo_layout) 
        horizontal_layout.addWidget(efetivo_groupbox)

        patente_groupbox.setLayout(patente_layout) 
        horizontal_layout.addWidget(patente_groupbox)

        controle_groupbox.setLayout(controle_layout)
        horizontal_layout.addWidget(controle_groupbox)

        # Adiciona o layout horizontal ao layout principal do dashboard
        main_layout.addLayout(horizontal_layout)

        # Define o layout principal para o widget de dashboard
        self.setLayout(main_layout)

    def create_subsection_layout(self, label_text, icon_key, value_text):
        """
        Cria um layout horizontal para uma subseção com um layout vertical para o ícone e 
        outro layout vertical para o título e valor, para estilo de dashboard.
        """
        # Layout principal da subseção (horizontal)
        subsection_layout = QHBoxLayout()
        subsection_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        subsection_layout.setContentsMargins(10, 10, 10, 10)
        subsection_layout.setSpacing(15)

        # Layout vertical para o ícone
        icon_layout = QVBoxLayout()
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_button = QPushButton()
        icon_button.setIcon(self.icons[icon_key])
        icon_button.setIconSize(QSize(40, 40))
        icon_button.setFlat(True)  # Remove a borda do botão
        icon_layout.addWidget(icon_button)

        # Layout vertical para o título e o valor
        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Título
        title_label = QLabel(label_text)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        text_layout.addWidget(title_label)

        # Valor
        value_label = QLabel(value_text)
        value_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        text_layout.addWidget(value_label)

        # Adiciona o layout do ícone e o layout de texto ao layout principal
        subsection_layout.addLayout(icon_layout)
        subsection_layout.addLayout(text_layout)

        return subsection_layout

    def create_subsection_hlayout(self, label_text, icon_key, value_text):
        """
        Cria um layout horizontal para uma subseção com um layout vertical para o ícone e 
        outro layout vertical para o título e valor, para estilo de dashboard.
        """
        # Layout principal da subseção (horizontal)
        subsection_layout = QHBoxLayout()
        subsection_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        subsection_layout.setContentsMargins(10, 10, 10, 10)
        subsection_layout.setSpacing(15)

        # Layout vertical para o ícone
        icon_layout = QVBoxLayout()
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_button = QPushButton()
        icon_button.setIcon(self.icons[icon_key])
        icon_button.setIconSize(QSize(40, 40))
        icon_button.setFlat(True)  # Remove a borda do botão
        icon_layout.addWidget(icon_button)

        # Layout vertical para o título e o valor
        text_layout = QHBoxLayout()
        text_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Título
        title_label = QLabel(label_text)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        text_layout.addWidget(title_label)

        # Valor
        value_label = QLabel(value_text)
        value_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        text_layout.addWidget(value_label)

        # Adiciona o layout do ícone e o layout de texto ao layout principal
        subsection_layout.addLayout(icon_layout)
        subsection_layout.addLayout(text_layout)

        return subsection_layout
