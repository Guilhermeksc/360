from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "database"
CONFIG_FILE = BASE_DIR / "config.json"
STYLE_PATH = BASE_DIR / "style.css" 

# Resources
RESOURCES_DIR = BASE_DIR / "resources"
TEMPLATE_DIR = RESOURCES_DIR / "templates"
ICONS_DIR = RESOURCES_DIR / "icons"
IMAGES_DIR = RESOURCES_DIR / "images"

# Modules
MODULES_DIR = BASE_DIR / "modules"
DISPENSA_ELETRONICA_DIR = MODULES_DIR / "dispensa_eletronica"
DATA_DISPENSA_ELETRONICA_PATH = DISPENSA_ELETRONICA_DIR / "controle_contratacao_direta.db"

LICITACAO_DIR = MODULES_DIR / "planejamento"
DATA_LICITACAO_PATH = LICITACAO_DIR / "controle_licitacao.db"

CONTROLE_DADOS = DATABASE_DIR / "controle_dados.db"
CONTROLE_CONTRATOS_DADOS = DATABASE_DIR / "controle_contrato.db"
CONTROLE_ASS_CONTRATOS_DADOS = DATABASE_DIR / "controle_assinatura.db"
HOME_PATH = BASE_DIR / "main.py"
CONTROLE_ATAS_DIR = DATABASE_DIR / "Atas"

TEMPLATE_DISPENSA_DIR = DISPENSA_ELETRONICA_DIR / "template"

CONFIG_FILE = 'config.json'

def load_config_path_id():
    if not Path(CONFIG_FILE).exists():
        return {}
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)