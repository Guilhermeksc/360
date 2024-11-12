from PyQt6.QtWidgets import QHBoxLayout, QLabel, QComboBox, QMessageBox
import sqlite3

def create_selecao_om_layout(database_path, dados, load_sigla_om_callback, on_om_changed_callback):
    """
    Cria um layout horizontal para a seleção de OM (Organização Militar).

    Args:
        database_path (str): Caminho para o banco de dados.
        dados (dict): Dicionário com dados iniciais para configuração do layout.
        load_sigla_om_callback (callable): Função para carregar sigla OM no combo.
        on_om_changed_callback (callable): Callback para mudanças na seleção de OM.

    Returns:
        tuple: layout QHBoxLayout configurado e o QComboBox.
    """
    # Criação do layout
    om_layout = QHBoxLayout()

    # Label "OM"
    om_label = QLabel("  OM:  ")
    om_label.setStyleSheet("font-size: 16px; font-weight: bold")
    om_layout.addWidget(om_label)

    # ComboBox para sigla OM
    om_combo = QComboBox()
    om_combo.setStyleSheet("font-size: 14px")
    om_layout.addWidget(om_combo)

    # Determina o valor inicial da sigla OM
    sigla_om = dados.get('sigla_om', 'CeIMBra')

    # Carrega as siglas OM e define o item selecionado
    load_sigla_om_callback(database_path, om_combo, sigla_om)

    # Conecta a função on_om_changed_callback para mudanças no combo
    om_combo.currentTextChanged.connect(lambda: on_om_changed_callback(om_combo, dados, database_path))

    return om_layout, om_combo

def load_sigla_om(database_path, om_combo, sigla_om):
    """Carrega as siglas OM no QComboBox."""
    try:
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT sigla_om FROM controle_om ORDER BY sigla_om")
            items = [row[0] for row in cursor.fetchall()]
            om_combo.addItems(items)
            om_combo.setCurrentText(sigla_om)  # Define o texto atual do combo
            # print(f"Loaded sigla_om items: {items}")
    except Exception as e:
        QMessageBox.warning(None, "Erro", f"Erro ao carregar OM: {e}")
        print(f"Error loading sigla_om: {e}")

def on_om_changed(obj, om_combo, dados, database_path):
    """Callback acionado quando a seleção de OM muda no QComboBox."""
    selected_om = om_combo.currentText()
    print(f"OM changed to: {selected_om}")
    try:
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT uasg, orgao_responsavel, uf, codigoMunicipioIbge FROM controle_om WHERE sigla_om = ?", (selected_om,))
            result = cursor.fetchone()
            if result:
                uasg, orgao_responsavel, uf, codigoMunicipioIbge = result
                dados['uasg'] = str(uasg)  # Converte `uasg` para string
                dados['orgao_responsavel'] = orgao_responsavel
                dados['uf'] = uf
                dados['codigoMunicipioIbge'] = codigoMunicipioIbge

                # Atualiza os valores diretamente no objeto principal
                obj.uasg = str(uasg)  # Converte para string antes de atribuir a `self.uasg`
                obj.orgao_responsavel = orgao_responsavel

                # Emite o sinal para atualizar o om_label
                obj.status_atualizado.emit(obj.uasg, obj.orgao_responsavel)

                print(f"Updated dados: uasg={obj.uasg}, orgao_responsavel={obj.orgao_responsavel}")
    except Exception as e:
        QMessageBox.warning(None, "Erro", f"Erro ao atualizar dados de OM: {e}")
        print(f"Error updating OM: {e}")

