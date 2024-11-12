import locale
from PyQt6.QtWidgets import QLineEdit

# Define o locale para BRL
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def formatar_para_brl(valor):
    """Converte o valor para o formato BRL."""
    try:
        valor = float(valor.replace(',', '.'))
        return locale.currency(valor, grouping=True, symbol=True)
    except ValueError:
        return "R$ 0,00"

class CustomQLineEdit(QLineEdit):
    def __init__(self, valor_inicial, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.valor_inicial = valor_inicial
        self.setText(formatar_para_brl(valor_inicial))  # Exibe o valor inicial formatado

    def focusOutEvent(self, event):
        """Override do evento focusOut para aplicar formatação BRL apenas se o valor for alterado."""
        texto_atual = self.text().replace('R$', '').strip()  # Remove "R$" para comparação
        if texto_atual != str(self.valor_inicial).replace('.', ','):
            self.setText(formatar_para_brl(texto_atual))
        else:
            self.setText(formatar_para_brl(self.valor_inicial))
        super().focusOutEvent(event)