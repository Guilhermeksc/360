from PyQt6.QtWidgets import *

from modules.utils.add_button import add_button

def setup_formularios(parent, icons, max_width=300):
    """Configura o layout para consulta à API com campos de CNPJ e Sequencial PNCP."""
    group_box = QGroupBox("Formulário", parent)
    group_box.setMaximumWidth(max_width) 
    layout = QVBoxLayout(group_box)

    # Aplicando o estilo CSS específico ao GroupBox
    group_box.setStyleSheet("""
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
    
    # Cria um layout vertical para os botões à esquerda
    vlayout_botoes = QVBoxLayout()
    add_button("   Novo Formulário   ", "excel_down", parent.save_data, vlayout_botoes, parent.icons, tooltip="Gerar o Formulário")
    add_button("Importar Formulário", "excel_up", parent.save_data, vlayout_botoes, parent.icons, tooltip="Carregar o Formulário")

    # Adiciona o layout vertical dos botões ao layout principal e aplica o espaçador à direita
    layout.addLayout(vlayout_botoes)

    return group_box