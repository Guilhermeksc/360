from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
import sqlite3
import os
from src.config.diretorios import ICONS_DIR, CONTROLE_DADOS
from src.modules.dispensa_eletronica.dialogs.gerar_tabela import TabelaResumidaManager
import pandas as pd

class DataManager(QDialog):
    def __init__(self, icons, model, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.model = model
        self.setWindowTitle("Database")
        self.setWindowIcon(self.icons["data-server"])
        self.setFixedSize(300, 300)  # Aumentado para ajustar o novo botão
        layout = QVBoxLayout()
        self.setStyleSheet("QWidget { font-size: 16px; }")

        # Layout horizontal para o título com ícone
        title_layout = QHBoxLayout()
        # Título com texto
        title_label = QLabel("Gerenciamento de Dados")
        title_label.setStyleSheet("font-size: 36px; font-weight: bold;")
        title_layout.addWidget(title_label)

        # Adiciona o layout de título ao layout principal
        layout.addLayout(title_layout)

        # Botão para salvar tabela completa
        btn_tabela_completa = QPushButton(" Tabela Completa", self)
        btn_tabela_completa.setIcon(self.icons["table"])
        btn_tabela_completa.setIconSize(QSize(40, 40))
        btn_tabela_completa.clicked.connect(self.salvar_tabela_completa)
        layout.addWidget(btn_tabela_completa)

        # Botão para salvar tabela resumida
        btn_tabela_resumida = QPushButton(" Tabela Resumida", self)
        btn_tabela_resumida.setIcon(self.icons["table"])
        btn_tabela_resumida.setIconSize(QSize(40, 40))
        btn_tabela_resumida.clicked.connect(self.salvar_tabela_resumida)
        layout.addWidget(btn_tabela_resumida)

        # Botão para carregar tabela
        btn_carregar_tabela = QPushButton("  Carregar Tabela", self)
        btn_carregar_tabela.setIcon(self.icons["loading_table"])
        btn_carregar_tabela.setIconSize(QSize(40, 40))
        btn_carregar_tabela.clicked.connect(self.carregar_tabela)
        layout.addWidget(btn_carregar_tabela)

        # Botão para excluir a tabela 'controle_dispensas'
        btn_excluir_database = QPushButton(" Excluir Database", self)
        btn_carregar_tabela.setIcon(self.icons["delete"])
        btn_excluir_database.setIconSize(QSize(40, 40))
        btn_excluir_database.clicked.connect(self.excluir_database)
        layout.addWidget(btn_excluir_database)

        self.setLayout(layout)

    def carregar_tabela(self): 
        filepath, _ = QFileDialog.getOpenFileName(self, "Abrir arquivo de tabela", "", "Tabelas (*.xlsx *.xls *.ods)")
        if filepath:
            try:
                # Carrega os dados do arquivo Excel para um DataFrame
                df = pd.read_excel(filepath)
                print("Tabela carregada do Excel com sucesso.")
                
                # Valida e processa os dados
                self.validate_and_process_data(df)

                # Converte o DataFrame para dicionários e insere no banco de dados
                for _, row in df.iterrows():
                    data = row.to_dict()
                    self.model.insert_or_update_data(data)  # Usa o método do modelo para inserir ou atualizar

                # Notificação de sucesso
                QMessageBox.information(self, "Carregamento concluído", "Dados carregados com sucesso.")
            except Exception as e:
                QMessageBox.warning(self, "Erro ao carregar", f"Ocorreu um erro ao carregar a tabela: {str(e)}")

    def validate_and_process_data(self, df):
        # Colunas obrigatórias
        required_columns = ['ID Processo', 'NUP', 'Objeto', 'uasg']
        if not all(col in df.columns for col in required_columns):
            missing_columns = [col for col in required_columns if col not in df.columns]
            raise ValueError(f"As seguintes colunas estão ausentes: {', '.join(missing_columns)}")
        
        # Renomeia colunas para que correspondam ao esquema do banco de dados
        df.rename(columns={
            'ID Processo': 'id_processo',
            'NUP': 'nup',
            'Objeto': 'objeto'
        }, inplace=True)

        # Processamento de colunas específicas
        self.desmembramento_id_processo(df)
        self.salvar_detalhes_uasg_sigla_nome(df)

    def desmembramento_id_processo(self, df):
        df[['tipo', 'numero', 'ano']] = df['id_processo'].str.extract(r'(\D+)(\d+)/(\d+)', expand=True)
        df['tipo'] = df['tipo'].map({'DE ': 'Dispensa Eletrônica'}).fillna('Tipo Desconhecido')


    def salvar_detalhes_uasg_sigla_nome(self, df):
        with sqlite3.connect(self.model.database_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT uasg, sigla_om, orgao_responsavel FROM controle_om")
            om_details = {row[0]: {'sigla_om': row[1], 'orgao_responsavel': row[2]} for row in cursor.fetchall()}
        df['sigla_om'] = df['uasg'].map(lambda x: om_details.get(x, {}).get('sigla_om', ''))
        df['orgao_responsavel'] = df['uasg'].map(lambda x: om_details.get(x, {}).get('orgao_responsavel', ''))

    def salvar_tabela_resumida(self):
        # Recarregar os dados mais recentes do banco de dados no modelo
        self.model.select()  # Atualiza o modelo com os dados mais recentes

        # Criar instância do TabelaResumidaManager
        tabela_manager = TabelaResumidaManager(self.model)

        # Carregar dados do modelo
        tabela_manager.carregar_dados()

        # Exportar para Excel
        output_path = os.path.join(os.getcwd(), "tabela_resumida.xlsx")
        tabela_manager.exportar_para_excel(output_path)

        # Abrir o arquivo Excel gerado
        tabela_manager.abrir_arquivo_excel(output_path)

    def salvar_tabela_completa(self):
        self.model.select()  
        tabela_manager = TabelaResumidaManager(self.model)
        # Carregar dados do modelo
        tabela_manager.carregar_dados()
        # Exportar para Excel
        output_path = os.path.join(os.getcwd(), "tabela_completa.xlsx")   

        tabela_manager.exportar_df_completo_para_excel(output_path)

        # Abrir o arquivo Excel gerado
        tabela_manager.abrir_arquivo_excel(output_path)

    def excluir_database(self):
        reply = QMessageBox.question(
            self,
            "Confirmação de Exclusão",
            "Tem certeza que deseja excluir a tabela 'controle_dispensas'?\nRecomenda-se salvar um backup antes de proceder com a exclusão. Deseja prosseguir?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Caminho do backup na área de trabalho do usuário
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            backup_path = os.path.join(desktop_path, "controle_dispensas_backup.xlsx")
            
            # Salvar backup antes de excluir
            try:
                self.parent().output_path = backup_path  # Define o caminho de saída do backup
                self.parent().salvar_tabela_completa()
                QMessageBox.information(self, "Backup Criado", f"Backup salvo na área de trabalho: {backup_path}")
                
                # Excluir a tabela após o backup
                conn = sqlite3.connect(CONTROLE_DADOS)
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS controle_dispensas")
                conn.commit()
                cursor.close()
                conn.close()
                QMessageBox.information(self, "Sucesso", "Tabela 'controle_dispensas' excluída com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao excluir a tabela: {str(e)}")
        else:
            QMessageBox.information(self, "Cancelado", "Exclusão cancelada pelo usuário.")
