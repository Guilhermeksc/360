# config/icon_loader.py
from pathlib import Path
from PyQt6.QtGui import QIcon
from src.config.paths import ICONS_DIR
import logging

# Configuração de logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Cache para ícones
_icon_cache = {}

def load_icon(icon_name):
    """Carrega e armazena em cache os ícones como QIcon. Verifica se o arquivo existe antes de carregar."""
    if icon_name not in _icon_cache:
        icon_path = ICONS_DIR / icon_name
        if icon_path.exists():
            _icon_cache[icon_name] = QIcon(str(icon_path))
        else:
            logger.warning(f"Ícone '{icon_name}' não encontrado em {icon_path}")
            _icon_cache[icon_name] = QIcon()  # Retorna um ícone vazio em caso de falha
    return _icon_cache[icon_name]

# Funções específicas para carregar ícones usados frequentemente
def load_icons():
    return {
        "brasil": load_icon("brasil.png"),
        "arquivo": load_icon("arquivo.png"),
        "api": load_icon("api.png"),
        "init": load_icon("init.png"),
        "dash": load_icon("dash.png"),
        "dash_hover": load_icon("dash_hover.png"),
        "init_hover": load_icon("init_hover.png"),
        "dispensa": load_icon("dispensa.png"),
        "dispensa_hover": load_icon("dispensa_hover.png"),
        "ata": load_icon("ata.png"),
        "ata_hover": load_icon("ata_hover.png"),
        "plan": load_icon("plan.png"),
        "plan_hover": load_icon("plan_hover.png"),
        "contract": load_icon("contract.png"),
        "contract_hover": load_icon("contract_hover.png"),
        "config": load_icon("config.png"),
        "config_hover": load_icon("config_hover.png"),
        "confirm": load_icon("confirm.png"),
        "business": load_icon("business.png"),
        "aproved": load_icon("aproved.png"),
        "session": load_icon("session.png"),
        "deal": load_icon("deal.png"),
        "emenda_parlamentar": load_icon("emenda_parlamentar.png"),
        "verify_menu": load_icon("verify_menu.png"),
        "archive": load_icon("archive.png"),
        "plus": load_icon("plus.png"),
        "save_to_drive": load_icon("save_to_drive.png"),
        "loading": load_icon("loading.png"),
        "delete": load_icon("delete.png"),
        "data-server": load_icon("data-server.png"),
        "performance": load_icon("performance.png"),
        "excel": load_icon("excel.png"),
        "calendar": load_icon("calendar.png"),
        "report": load_icon("report.png"),
        "signature": load_icon("signature.png"),
        "planning": load_icon("planning.png"),
        "website_menu": load_icon("website_menu.png"),
        "automation": load_icon("automation.png"),
        "pdf": load_icon("pdf.png"),
        "management": load_icon("management.png"),
        "edit": load_icon("management.png"),
        "image-processing": load_icon("image-processing.png"),
        "brasil_2": load_icon("brasil_2.png"),
        "prioridade": load_icon("prioridade.png"),
        "link": load_icon("link.png"),
        "excel_down": load_icon("excel_down.png"),
        "excel_up": load_icon("excel_up.png"),
        "acanto": load_icon("acanto.png"),
        "folder_v": load_icon("folder_v.png"),
        "folder_x": load_icon("folder_x.png"),
        "magnifying-glass": load_icon("magnifying-glass.png"),
        "loading_table": load_icon("loading_table.png"),
        "table": load_icon("table.png"),
        "copy_1": load_icon("copy_1.png"),
        "concluido": load_icon("concluido.png"),
        "grid": load_icon("grid.png"),
        "efetivo": load_icon("efetivo.png"),
        "dash_titulo": load_icon("dash_titulo.png"),
        "oficial": load_icon("oficial.png"),
        "suboficial": load_icon("suboficial.png"),
        "sg1": load_icon("sg1.png"),
        "sg2": load_icon("sg2.png"),
        "sg3": load_icon("sg3.png"),
        "cb": load_icon("cb.png"),
        "mn": load_icon("mn.png"),
        "create-folder": load_icon("create-folder.png"),
        "zip-folder": load_icon("zip-folder.png"),
        "template": load_icon("template.png"),
        "cancel": load_icon("cancel.png"),
        "open-folder": load_icon("open-folder.png"),
        "browser": load_icon("browser.png"),
        "open_icon": load_icon("open_icon.png"),
        "refresh": load_icon("refresh.png"),
        "confirm_green": load_icon("confirm_green.png"),
        "checked": load_icon("checked.png"),
        "test": load_icon("testing.png"),
                }