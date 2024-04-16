from flask import Blueprint

# Crie um Blueprint para as rotas
routes_blueprint = Blueprint('routes', __name__)

# Importe as rotas dos arquivos individuais
from .usuarios_routes import usuarios_routes
from .plano_routes import plano_routes
from .IntegracaoBI_routes import integracaoBI
from .metaPlano_routes import metaPlano_routes
from .estrutura_routes import estrutura_routes
from .rotasPlataformaWeb import rotasPlataformaWeb
from .responsabilidadeFase_routes import ResponsabilidadeFase_routes
from .dashboardTV import dashboardTVroute
from .AutomacaoSugestaoPedidos_routes import reservaPrefatroute
from .monitor_routes import monitorPreFaturamento_routes

#from .DashboardNovos import dashboard_routes
# Importe mais arquivos de rotas conforme necessário

# Registre as rotas nos blueprints
routes_blueprint.register_blueprint(usuarios_routes)
routes_blueprint.register_blueprint(plano_routes)
routes_blueprint.register_blueprint(integracaoBI)
routes_blueprint.register_blueprint(metaPlano_routes)
routes_blueprint.register_blueprint(estrutura_routes)
routes_blueprint.register_blueprint(rotasPlataformaWeb)
routes_blueprint.register_blueprint(ResponsabilidadeFase_routes)
routes_blueprint.register_blueprint(dashboardTVroute)
routes_blueprint.register_blueprint(reservaPrefatroute)
routes_blueprint.register_blueprint(monitorPreFaturamento_routes)

#routes_blueprint.register_blueprint(dashboard_routes)

