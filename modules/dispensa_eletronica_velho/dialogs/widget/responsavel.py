from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QHBoxLayout

class SetorResponsavelWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Configuração dos componentes com base em `data`
        layout.addWidget(QLabel(f"Setor Responsável: {self.data[2]}"))  # Exemplo
        self.setLayout(layout)