from enum import Enum

class ActiveInactiveStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class SensorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    STATION_ADMIN = "station_admin"

class AlertEventType(str, Enum):
    CREATED = "created"
    UPGRADED = "upgraded"
    DOWNGRADED = "downgraded"
    RESOLVED = "resolved"