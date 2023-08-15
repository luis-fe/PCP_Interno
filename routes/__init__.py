from flask import Blueprint

# Crie um Blueprint para as rotas
routes_blueprint = Blueprint('routes', __name__)

# Importe as rotas dos arquivos individuais
from .usuarios_routes import usuarios_routes
from .plano_routes import plano_routes
from .IntegracaoBI_routes import integracaoBI
from .metaPlano_routes import metaPlano_routes

# Importe mais arquivos de rotas conforme necessário

# Registre as rotas nos blueprints
routes_blueprint.register_blueprint(usuarios_routes)
routes_blueprint.register_blueprint(plano_routes)
routes_blueprint.register_blueprint(integracaoBI)
routes_blueprint.register_blueprint(metaPlano_routes)