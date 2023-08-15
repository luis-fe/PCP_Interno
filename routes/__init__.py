from flask import Blueprint

# Crie um Blueprint para as rotas
routes_blueprint = Blueprint('routes', __name__)

# Importe as rotas dos arquivos individuais
from .usuarios_routes import usuarios_routes

# Importe mais arquivos de rotas conforme necessário

# Registre as rotas nos blueprints
routes_blueprint.register_blueprint(usuarios_routes)
# Registre mais blueprints conforme necessário
