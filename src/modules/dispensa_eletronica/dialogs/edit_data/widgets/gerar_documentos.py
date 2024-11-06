from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import pandas as pd
from pathlib import Path
from src.config.diretorios import *
import re
import num2words
import subprocess
import os
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QSize
from fpdf import FPDF
import json
from docxtpl import DocxTemplate
import win32com.client
from PyPDF2 import PdfMerger

CONFIG_FILE = 'config.json'

def load_config_path_id():
    if not Path(CONFIG_FILE).exists():
        return {}
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)


class ConsolidarDocumentos(QObject):
    status_atualizado = pyqtSignal(str, str)
  
    def __init__(self, dados, status_label=None):
        super().__init__()  # Inicializa o QObject
        self.dados = dados
        self.config = load_config_path_id()
        self.pasta_base = Path(self.config.get('pasta_base', str(Path.home() / 'Desktop')))

        # Inicialize as variáveis conforme o exemplo anterior
        id_processo = self.dados.get('id_processo', 'desconhecido').replace("/", "-")
        objeto = self.dados.get('objeto', 'objeto_desconhecido').replace("/", "-")
        self.nome_pasta = f"{id_processo} - {objeto}"
        self.ICONS_DIR = ICONS_DIR

        # Verifica se `dados` é um DataFrame
        if isinstance(self.dados, pd.DataFrame):
            self.id_processo = self.dados['id_processo'].iloc[0]
            self.objeto = self.dados['objeto'].iloc[0]
        elif isinstance(self.dados, dict):  # Caso seja um dicionário
            self.id_processo = self.dados.get('id_processo', 'Desconhecido')
            self.objeto = self.dados.get('objeto', 'Desconhecido')
        else:
            raise ValueError("O tipo de 'dados' não é suportado. Esperado DataFrame ou dict.")

        # Exemplo de dados de índice
        self.data = {
            'id_processo': 'DE 15/2024',
            'tipo': 'DE',
            'numero': '50',
            'ano': '2024',
            'situacao': 'Planejamento, Sessão Pública, Concluído',
            'nup': '62055.00055/2024-01',
            'material_servico': 'Material ou Serviço',
            'objeto': 'Suprimentos de informática',
            'vigencia': '12 meses a partir da assinatura',
            'data_sessao': '15/10/2024',
            'operador': 'João da Silva',
            'criterio_julgamento': 'Menor preço, Técnica e preço',
            'com_disputa': 'Sim, Não',
        }

    def criar_e_abrir_pasta(self):
        # Verifica e cria a estrutura de pastas
        pastas_existem = self.verificar_e_criar_pastas(self.pasta_base / self.nome_pasta)
        
        # Reexecuta a verificação para garantir o status atualizado
        pastas_existem = self.verificar_pastas(self.pasta_base)

        # Atualiza o status e emite o sinal com o resultado atualizado
        status_texto = "Pastas encontradas" if pastas_existem else "Pastas não encontradas"
        icone = "folder_v.png" if pastas_existem else "folder_x.png"
        
        # Emitindo o sinal para atualizar o ícone e a mensagem
        print(f"Emitting status_atualizado with status_texto: '{status_texto}' and icone: '{icone}'")
        self.status_atualizado.emit(status_texto, str(self.ICONS_DIR / icone))

        # Abre a pasta criada
        self.abrir_pasta(self.pasta_base / self.nome_pasta)

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

    def create_gerar_documentos_group(self, handle_gerar_autorizacao, handle_gerar_autorizacao_sidgem,
                                      handle_gerar_comunicacao_padronizada, handle_gerar_comunicacao_padronizada_sidgem,
                                      handle_gerar_aviso_dispensa, handle_gerar_aviso_dispensa_sidgem):
        gerar_documentos_layout = QVBoxLayout()
                
        # Botões para gerar documentos
        icon_pdf = QIcon(str(self.ICONS_DIR / "pdf.png"))
        icon_copy = QIcon(str(self.ICONS_DIR / "copy.png"))

        buttons_info = [
            ("Autorização para Abertura", handle_gerar_autorizacao, handle_gerar_autorizacao_sidgem),
            ("Comunicação Padronizada e anexos", handle_gerar_comunicacao_padronizada, handle_gerar_comunicacao_padronizada_sidgem),
            ("Aviso de Dispensa", handle_gerar_aviso_dispensa, handle_gerar_aviso_dispensa_sidgem)
        ]

        for text, visualizar_callback, sigdem_callback in buttons_info:
            button_layout = QHBoxLayout()
            
            if visualizar_callback:
                visualizar_pdf_button = self.create_button(
                    text=text,
                    icon=icon_pdf,
                    callback=visualizar_callback,
                    tooltip_text="Clique para visualizar o PDF",
                    button_size=QSize(310, 40),
                    icon_size=QSize(40, 40)
                )
                button_layout.addWidget(visualizar_pdf_button)
                
            if sigdem_callback:
                sigdem_button = self.create_button(
                    text="",
                    icon=icon_copy,
                    callback=sigdem_callback,
                    tooltip_text="Clique para copiar",
                    button_size=QSize(40, 40),
                    icon_size=QSize(30, 30)
                )
                button_layout.addWidget(sigdem_button)

            gerar_documentos_layout.addLayout(button_layout)
        
        return gerar_documentos_layout
    
    def create_button(self, text, icon, callback, tooltip_text, button_size, icon_size):
        # Criar o botão e definir o tamanho
        button = QPushButton()
        button.setFixedSize(button_size)
        button.setToolTip(tooltip_text)
        button.clicked.connect(callback)

        # Criar um widget para o layout
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Criar o ícone e adicionar ao layout
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(icon_size))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Criar o texto e adicionar ao layout
        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label)

        # Adicionar o widget ao botão
        button.setLayout(layout)
        
        return button
    
    def editar_modelo(self, button_font_size=18, icon_size=QSize(40, 40)):
        dialog = QDialog()
        dialog.setWindowTitle("Editar Template")
        
        # Adicionar ícone ao título
        icon_confirm = QIcon(str(self.ICONS_DIR / "confirm_green.png"))
        dialog.setWindowIcon(icon_confirm)

        # Ícones para os botões
        icon_index = QIcon(str(self.ICONS_DIR / "pdf.png"))  # Ícone para "Abrir índice"
        icon_open = QIcon(str(self.ICONS_DIR / "open_icon.png"))  # Ícone para os demais botões "Abrir"

        # Layout principal do diálogo
        main_layout = QVBoxLayout(dialog)
        
        # Layout horizontal para o botão "Abrir índice"
        top_layout = QHBoxLayout()
        button_open_index = QPushButton("Índice")
        button_open_index.setIcon(icon_index)
        button_open_index.setFixedSize(110, 40)  # Definir tamanho fixo para uniformidade
        button_open_index.setIconSize(icon_size)  # Ajusta o tamanho do ícone
        button_open_index.setStyleSheet("font-size: 18px;")  # Ajusta o tamanho da fonte
        button_open_index.clicked.connect(self.abrir_indice)
        
        # Adicionar o texto ao lado do botão "Abrir índice"
        label_info = QLabel("Relação de Variáveis e exemplos de uso")
        label_info.setStyleSheet("font-size: 18px;")  # Definir tamanho da fonte para 14

        top_layout.addWidget(button_open_index, alignment=Qt.AlignmentFlag.AlignLeft)
        top_layout.addWidget(label_info, alignment=Qt.AlignmentFlag.AlignLeft)
        
        top_layout.addStretch()
        # Layout para os templates
        templates_layout = QVBoxLayout()

        # Lista de templates e seus caminhos
        templates = [
            ("Template Autorização", TEMPLATE_DISPENSA_DIR / "template_autorizacao_dispensa.docx"),
            ("Template Comunicação Padronizada", TEMPLATE_DISPENSA_DIR / "template_cp.docx"),
            ("Template DFD", TEMPLATE_DISPENSA_DIR / "template_dfd.docx"),
            ("Template Termo de Referência", TEMPLATE_DISPENSA_DIR / "template_tr.docx"),
            ("Template Declaração de Adequação Orçamentária", TEMPLATE_DISPENSA_DIR / "template_dec_adeq.docx"),
            ("Template Aviso de Dispensa", TEMPLATE_DISPENSA_DIR / "template_aviso_dispensa.docx")
        ]

        # Adicionar os templates ao layout
        for template_name, template_path in templates:
            template_row = QHBoxLayout()
            
            label = QLabel(template_name)
            label.setStyleSheet("font-size: 18px;")  # Definir tamanho da fonte para 14
            button_open_template = QPushButton("Abrir")
            button_open_template.setIcon(icon_open)
            button_open_template.setFixedSize(110, 40)  # Definir tamanho fixo para uniformidade
            button_open_template.setIconSize(icon_size)  # Ajusta o tamanho do ícone
            button_open_template.setStyleSheet("font-size: 18px;")  # Ajusta o tamanho da fonte
            button_open_template.clicked.connect(lambda _, path=template_path: self.abrir_template(path))
            
            template_row.addWidget(button_open_template)
            template_row.addWidget(label)
            templates_layout.addLayout(template_row)

        # Adicionar layouts ao layout principal
        main_layout.addLayout(top_layout)
        main_layout.addLayout(templates_layout)

        dialog.setLayout(main_layout)
        dialog.exec()

    def abrir_template(self, path):
        # Verificar se o arquivo existe
        if path.exists() and path.is_file():
            print(f"Arquivo encontrado: {path}")
            try:
                # Abre o arquivo utilizando o caminho absoluto
                full_path = str(path.resolve())  # Resolve para o caminho absoluto
                subprocess.run(f'start "" "{full_path}"', shell=True)  # Windows
                # Para Linux ou macOS, use os comandos adequados
                # subprocess.run(['xdg-open', full_path])  # Linux
                # subprocess.run(['open', full_path])  # macOS
            except Exception as e:
                print(f"Erro ao abrir o template: {e}")
        else:
            print(f"Arquivo não encontrado: {path}")

    def abrir_indice(self):
        # Cria o PDF dos índices
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Adicionar título
        pdf.cell(200, 10, txt="Índices Utilizados nos Templates", ln=True, align='C')

        # Adicionar exemplos de cada índice com cores personalizadas
        for key, example in self.data.items():
            # Definir cor para o 'key' (azul marinho)
            pdf.set_text_color(0, 0, 128)  # Azul marinho (RGB: 0, 0, 128)
            pdf.write(10, f"{{{{{key}}}}}: ")

            # Definir cor para o 'example' (vermelho escuro)
            pdf.set_text_color(139, 0, 0)  # Vermelho escuro (RGB: 139, 0, 0)
            pdf.write(10, f"Exemplo: {example}\n")  # Adiciona texto com nova linha

        # Salva o PDF
        pdf_path = self.pasta_base / "indice_templates.pdf"
        pdf.output(str(pdf_path))

        print(f"Arquivo PDF de índices criado: {pdf_path}")

        # Abrir o PDF criado
        if pdf_path.exists() and pdf_path.is_file():
            try:
                subprocess.run(f'start "" "{str(pdf_path)}"', shell=True)  # Windows
                # Para Linux ou macOS, use os comandos adequados
                # subprocess.run(['xdg-open', str(pdf_path)])  # Linux
                # subprocess.run(['open', str(pdf_path)])  # macOS
            except Exception as e:
                print(f"Erro ao abrir o PDF de índices: {e}")
        else:
            print(f"Arquivo PDF de índices não encontrado: {pdf_path}")

    def alterar_diretorio_base(self):
        new_dir = QFileDialog.getExistingDirectory(None, "Selecione o Novo Diretório Base", str(Path.home()))
        if new_dir:
            self.pasta_base = Path(new_dir)
            self.config['pasta_base'] = str(self.pasta_base)
            save_config(self.config)
            QMessageBox.information(None, "Diretório Base Alterado", f"O novo diretório base foi alterado para: {self.pasta_base}")

    def abrir_pasta_base(self):
        try:
            os.startfile(self.pasta_base)
        except Exception as e:
            print(f"Erro ao abrir a pasta base: {e}")
            QMessageBox.warning(None, "Erro", f"Erro ao abrir a pasta base: {e}")

    def abrirDocumento(self, docx_path):
        try:
            pdf_path = self.convert_to_pdf(docx_path)
            os.startfile(pdf_path)
            print(f"Documento PDF aberto: {pdf_path}")
        except Exception as e:
            print(f"Erro ao abrir ou converter o documento: {e}")
            QMessageBox.warning(None, "Erro", f"Erro ao abrir ou converter o documento: {e}")

    def salvarPDF(self, docx_path):
        try:
            pdf_path = self.convert_to_pdf(docx_path)
            print(f"Documento PDF salvo: {pdf_path}")
            return pdf_path
        except Exception as e:
            print(f"Erro ao converter o documento: {e}")
            QMessageBox.warning(None, "Erro", f"Erro ao converter o documento: {e}")
            return None

    def convert_to_pdf(self, docx_path):
        docx_path = Path(docx_path) if not isinstance(docx_path, Path) else docx_path
        pdf_path = docx_path.with_suffix('.pdf')
        word = win32com.client.Dispatch("Word.Application")
        doc = None
        try:
            doc = word.Documents.Open(str(docx_path))
            doc.SaveAs(str(pdf_path), FileFormat=17)
        except Exception as e:
            raise e
        finally:
            if doc is not None:
                doc.Close()
            word.Quit()
        if not pdf_path.exists():
            raise FileNotFoundError(f"O arquivo PDF não foi criado: {pdf_path}")
        return pdf_path

    def valor_por_extenso(self, valor):
        if not valor or valor.strip() == '':  # Verifica se o valor está vazio ou None
            return None  # Retorna None se o valor não for válido

        try:
            valor = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
            valor_float = float(valor)
            parte_inteira = int(valor_float)
            parte_decimal = int(round((valor_float - parte_inteira) * 100))

            if parte_decimal > 0:
                valor_extenso = f"{num2words(parte_inteira, lang='pt_BR')} reais e {num2words(parte_decimal, lang='pt_BR')} centavos"
            else:
                valor_extenso = f"{num2words(parte_inteira, lang='pt_BR')} reais"

            # Corrige "um reais" para "um real"
            valor_extenso = valor_extenso.replace("um reais", "um real")

            return valor_extenso

        except ValueError:
            return None

    def alterar_posto(self, posto):
        # Define um dicionário de mapeamento de postos e suas respectivas abreviações
        mapeamento_postos = {
            r'Capitão[\s\-]de[\s\-]Corveta': 'CC',
            r'Capitão[\s\-]de[\s\-]Fragata': 'CF',
            r'Capitão[\s\-]de[\s\-]Mar[\s\-]e[\s\-]Guerra': 'CMG',
            r'Capitão[\s\-]Tenente': 'CT',
            r'Primeiro[\s\-]Tenente': '1ºTen',
            r'Segundo[\s\-]Tenente': '2ºTen',
            r'Primeiro[\s\-]Sargento': '1ºSG',
            r'Segundo[\s\-]Sargento': '2ºSG',
            r'Terceiro[\s\-]Sargento': '3ºSG',
            r'Cabo': 'CB',
            r'Sub[\s\-]oficial': 'SO',
        }

        # Itera sobre o dicionário de mapeamento e aplica a substituição
        for padrao, substituicao in mapeamento_postos.items():
            if re.search(padrao, posto, re.IGNORECASE):
                return re.sub(padrao, substituicao, posto, flags=re.IGNORECASE)

        # Retorna o posto original se nenhuma substituição for aplicada
        return posto

    def formatar_responsavel(self, chave, data, context):
        responsavel = data.get(chave)
        if responsavel and isinstance(responsavel, str):
            try:
                nome, posto, funcao = responsavel.split('\n')
                posto_alterado = self.alterar_posto(posto)
                responsavel_dict = {
                    'nome': nome,
                    'posto': posto_alterado,
                }
                responsavel_extenso = f"{responsavel_dict.get('posto', '')} {responsavel_dict.get('nome', '')}"
                context.update({f'{chave}_formatado': responsavel_extenso})
            except ValueError:
                context.update({f'{chave}_formatado': 'Não especificado\nNão especificado'})
        else:
            context.update({f'{chave}_formatado': 'Não especificado\nNão especificado'})

    def prepare_context(self, data):
        context = {key: (str(value) if value is not None else 'Não especificado') for key, value in data.items()}
        descricao_servico = "aquisição de" if data['material_servico'] == "Material" else "contratação de empresa especializada em"
        descricao_servico_primeira_letra_maiuscula = descricao_servico[0].upper() + descricao_servico[1:]
        context.update({'descricao_servico': descricao_servico})
        context.update({'descricao_servico_primeira_letra_maiuscula': descricao_servico_primeira_letra_maiuscula})

        # Processar responsável pela demanda e operador
        self.formatar_responsavel('responsavel_pela_demanda', data, context)
        self.formatar_responsavel('operador', data, context)

        valor_total = data.get('valor_total')
        if valor_total and isinstance(valor_total, str):
            valor_extenso = self.valor_por_extenso(valor_total)
            valor_total_e_extenso = f"{valor_total} ({valor_extenso})"
            context.update({'valor_total_e_extenso': valor_total_e_extenso})
        else:
            context.update({'valor_total_e_extenso': 'Não especificado'})

        # Lógica para atividade_custeio
        if data.get('atividade_custeio') == 'Sim':
            texto_custeio = (
                "A presente contratação por dispensa de licitação está enquadrada como atividade de custeio, "
                "conforme mencionado no artigo 2º da Portaria ME nº 7.828, de 30 de agosto de 2022. "
                "Conforme previsão do art. 3º do Decreto nº 10.193, de 27 de dezembro de 2019, e as normas "
                "infralegais de delegação de competência no âmbito da Marinha, que estabelecem limites e instâncias "
                "de governança, essa responsabilidade é delegada ao ordenador de despesas, respeitando os valores "
                "estipulados no decreto."
            )
        else:
            texto_custeio = (
                "A presente contratação por dispensa de licitação não se enquadra nas hipóteses de atividades de "
                "custeio previstas no Decreto nº 10.193, de 27 de dezembro de 2019, pois o objeto contratado não se "
                "relaciona diretamente às atividades comuns de suporte administrativo mencionadas no artigo 2º da "
                "Portaria ME nº 7.828, de 30 de agosto de 2022."
            )
        context.update({'texto_custeio': texto_custeio})

        # Alterar formato de data_sessao
        data_sessao = data.get('data_sessao')
        if data_sessao:
            try:
                data_obj = datetime.strptime(data_sessao, '%Y-%m-%d')
                dia_semana = data_obj.strftime('%A')
                data_formatada = data_obj.strftime('%d/%m/%Y') + f" ({dia_semana})"
                context.update({'data_sessao_formatada': data_formatada})
            except ValueError as e:
                context.update({'data_sessao_formatada': 'Data inválida'})
                print("Erro ao processar data da sessão:", e)
        else:
            context.update({'data_sessao_formatada': 'Não especificado'})
            print("Data da sessão não especificada")

        return context

    def gerarDocumento(self, template_type, subfolder_name, file_description):
        if self.df_registro_selecionado.empty:
            QMessageBox.warning(None, "Seleção Necessária", "Por favor, selecione um registro na tabela antes de gerar um documento.")
            return

        template_filename = f"template_{template_type}.docx"
        template_path, save_path = self.setup_document_paths(template_filename, subfolder_name, file_description)

        self.verificar_e_criar_pastas(self.pasta_base / self.nome_pasta)

        if not template_path.exists():
            QMessageBox.warning(None, "Erro de Template", f"O arquivo de template não foi encontrado: {template_path}")
            return

        with open(str(template_path), 'rb') as template_file:
            doc = DocxTemplate(template_file)
            context = self.df_registro_selecionado.to_dict('records')[0]
            context = self.prepare_context(context)
            doc.render(context)
            doc.save(str(save_path))
        return save_path

    def setup_document_paths(self, template_filename, subfolder_name, file_description):
        template_path = TEMPLATE_DISPENSA_DIR / template_filename
        id_processo = self.df_registro_selecionado['id_processo'].iloc[0].replace('/', '-')
        objeto = self.df_registro_selecionado['objeto'].iloc[0]
        self.nome_pasta = f"{id_processo} - {objeto}"
        if 'pasta_base' not in self.config:
            self.alterar_diretorio_base()
        pasta_base = Path(self.config['pasta_base']) / self.nome_pasta / subfolder_name
        pasta_base.mkdir(parents=True, exist_ok=True)
        save_path = pasta_base / f"{id_processo} - {file_description}.docx"
        return template_path, save_path

    def verificar_pastas(self, pasta_base):
        id_processo_modificado = self.id_processo.replace("/", "-")
        objeto_modificado = self.objeto.replace("/", "-")
        base_path = pasta_base / f'{id_processo_modificado} - {objeto_modificado}'

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
        
    def gerar_e_abrir_documento(self, template_type, subfolder_name, file_description):
        docx_path = self.gerarDocumento(template_type, subfolder_name, file_description)
        if docx_path:
            self.abrirDocumento(docx_path)

    def gerar_autorizacao(self):
        self.gerar_e_abrir_documento("autorizacao_dispensa", "1. Autorizacao", "Autorizacao para abertura de Processo Administrativo")

    def gerar_comunicacao_padronizada(self):
        documentos = [
            {"template": "cp", "subfolder": "2. CP e anexos", "desc": "Comunicacao Padronizada"},
            {"template": "dfd", "subfolder": "2. CP e anexos/DFD", "desc": "Documento de Formalizacao de Demanda", "cover": "dfd.pdf"},
            {"subfolder": "2. CP e anexos/DFD/Anexo A - Relatorio Safin", "cover": "anexo-a-dfd.pdf"},
            {"subfolder": "2. CP e anexos/DFD/Anexo B - Especificações e Quantidade", "cover": "anexo-b-dfd.pdf"},
            {"template": "tr", "subfolder": "2. CP e anexos/TR", "desc": "Termo de Referencia", "cover": "tr.pdf"},
            {"subfolder": "2. CP e anexos/TR/Pesquisa de Preços", "cover": "anexo-tr.pdf"},
            {"template": "dec_adeq", "subfolder": "2. CP e anexos/Declaracao de Adequação Orçamentária", "desc": "Declaracao de Adequação Orçamentária", "cover": "dec_adeq.pdf"},
            {"subfolder": "2. CP e anexos/Declaracao de Adequação Orçamentária/Relatório do PDM-Catser", "cover": "anexo-dec-adeq.pdf"},
            {"template": "justificativas", "subfolder": "2. CP e anexos/Justificativas Relevantes", "desc": "Justificativas Relevantes", "cover": "justificativas.pdf"},
        ]

        pdf_paths = []

        for doc in documentos:
            if "template" in doc:
                docx_path = self.gerarDocumento(doc["template"], doc["subfolder"], doc["desc"])
                if docx_path:
                    pdf_path = self.salvarPDF(docx_path)
                    if pdf_path:
                        pdf_info = {"pdf_path": pdf_path}
                        if "cover" in doc:
                            pdf_info["cover_path"] = TEMPLATE_DISPENSA_DIR / doc["cover"]
                        pdf_paths.append(pdf_info)
            else:
                pdf_path = self.get_latest_pdf(self.pasta_base / self.nome_pasta / doc["subfolder"])
                if pdf_path:
                    pdf_paths.append({"pdf_path": pdf_path, "cover_path": TEMPLATE_DISPENSA_DIR / doc["cover"]})
                else:
                    QMessageBox.warning(None, "Erro", f"Arquivo PDF não encontrado: {doc['subfolder']}")

        self.concatenar_e_abrir_pdfs(pdf_paths)
           
    def concatenar_e_abrir_pdfs(self, pdf_paths):
        if not pdf_paths:
            QMessageBox.warning(None, "Erro", "Nenhum PDF foi gerado para concatenar.")
            return

        output_pdf_path = self.pasta_base / self.nome_pasta / "2. CP e anexos" / "CP_e_anexos.pdf"
        merger = PdfMerger()

        try:
            for pdf in pdf_paths:
                if "cover_path" in pdf:
                    merger.append(str(pdf["cover_path"]))
                merger.append(str(pdf["pdf_path"]))

            merger.write(str(output_pdf_path))
            merger.close()

            os.startfile(output_pdf_path)
            print(f"PDF concatenado salvo e aberto: {output_pdf_path}")
        except Exception as e:
            print(f"Erro ao concatenar os PDFs: {e}")
            QMessageBox.warning(None, "Erro", f"Erro ao concatenar os PDFs: {e}")

    def get_latest_pdf(self, directory):
        pdf_files = list(directory.glob("*.pdf"))
        if not pdf_files:
            return None
        latest_pdf = max(pdf_files, key=os.path.getmtime)
        return latest_pdf


    def gerar_documento_de_formalizacao_de_demanda(self):
        self.gerarDocumento("dfd", "2. CP e anexos/DFD", "Documento de Formalizacao de Demanda")

    def gerar_declaracao_orcamentaria(self):
        self.gerarDocumento("declaracao_orcamentaria", "2. CP e anexos/Declaracao de Adequação Orçamentária", "Declaracao Orcamentaria")

    def gerar_termo_de_referencia(self):
        self.gerarDocumento("tr", "2. CP e anexos/TR", "Termo de Referencia")

    def gerar_aviso_dispensa(self):
        self.gerar_e_abrir_documento("aviso_dispensa", "3. Aviso", "Aviso de Dispensa")

    def verificar_e_criar_pastas(self, pasta_base):
        pastas_necessarias = [
            pasta_base / '1. Autorizacao',
            pasta_base / '2. CP e anexos',
            pasta_base / '3. Aviso',
            pasta_base / '2. CP e anexos' / 'DFD',
            pasta_base / '2. CP e anexos' / 'DFD' / 'Anexo A - Relatorio Safin',
            pasta_base / '2. CP e anexos' / 'DFD' / 'Anexo B - Especificações e Quantidade',
            pasta_base / '2. CP e anexos' / 'TR',
            pasta_base / '2. CP e anexos' / 'TR' / 'Pesquisa de Preços',
            pasta_base / '2. CP e anexos' / 'Declaracao de Adequação Orçamentária',
            pasta_base / '2. CP e anexos' / 'Declaracao de Adequação Orçamentária' / 'Relatório do PDM-Catser',
            pasta_base / '2. CP e anexos' / 'Justificativas Relevantes',
        ]
        pastas_existem = True
        for pasta in pastas_necessarias:
            if not pasta.exists():
                pasta.mkdir(parents=True)
                pastas_existem = False
        
        # Emita o sinal após verificar as pastas
        status_text = "Pastas encontradas" if pastas_existem else "Pastas não encontradas"
        icon_path = ICONS_DIR / ("folder_v.png" if pastas_existem else "folder_x.png")
        self.status_atualizado.emit(status_text, str(icon_path))

        return pastas_existem
    
    def abrir_pasta(self, caminho):
        if os.path.exists(caminho):
            os.startfile(caminho)  # Abre o caminho no Windows
            

