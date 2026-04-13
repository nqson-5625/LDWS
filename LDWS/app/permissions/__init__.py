from app.permissions.authz import require_roles
from app.permissions.roles import STATION_ADMIN, SUPER_ADMIN
from app.permissions.station_scope import ensure_station_scope, get_current_station_scope