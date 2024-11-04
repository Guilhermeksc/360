from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon, QCursor
from PyQt6.QtCore import QSize, Qt
from pathlib import Path

def add_button(label, icon_name, signal, layout, icons, tooltip=None):
    """
    Cria e adiciona um botão a um layout com o ícone e sinal fornecidos,
    aplicando estilo personalizado.
    
    :param label: Texto do botão.
    :param icon_name: Nome do ícone no dicionário.
    :param signal: Sinal a ser emitido ao clicar no botão.
    :param layout: Layout onde o botão será adicionado.
    :param icons: Dicionário de ícones carregados.
    :param tooltip: Texto opcional para o tooltip exibido ao passar o mouse sobre o botão.
    """
    button = QPushButton(label)
    
    # Obtém o ícone de `icons`
    icon = icons.get(icon_name)
    if icon:
        button.setIcon(icon)
    else:
        print(f"Aviso: Ícone '{icon_name}' não encontrado em `icons`.")

    button.setIconSize(QSize(30, 30))
    button.clicked.connect(signal.emit)
    
    # Aplicando o CSS para o estilo do botão
    button.setStyleSheet("""
        QPushButton {
            background-color: #181928;
            color: #8AB4F7;
            font-size: 14px;
            font-weight: bold;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
        }
        QPushButton:hover {
            background-color: #2C2F3F;
            color: #FFFFFF;
        }
    """)
    
    # Define o cursor como mão ao passar o mouse sobre o botão
    button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    if tooltip:
        button.setToolTip(tooltip)
    
    layout.addWidget(button)
    return button

def create_button(text, icon, callback, tooltip_text, parent, icon_size=QSize(30, 30)):
    btn = QPushButton(text, parent)
    if icon:
        btn.setIcon(QIcon(icon))
        btn.setIconSize(icon_size)
    if callback:
        btn.clicked.connect(callback)
    if tooltip_text:
        btn.setToolTip(tooltip_text)

    return btn