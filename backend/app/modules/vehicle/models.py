"""
Vehicle models for module-level imports.

Use centralized SQLAlchemy models from app.data.models to avoid metadata duplication.
"""

from app.data.models.vehicle import Vehicle as _Vehicle
from app.data.models.vehicle_valuation import VehicleValuation

# Compatibility shim: keep legacy `owner_id` accepted by callers in this module layer.
_vehicle_init_orig = _Vehicle.__init__


def _vehicle_init(self, *args, **kwargs):
  if "owner_id" in kwargs and "user_id" not in kwargs:
    kwargs["user_id"] = kwargs.pop("owner_id")
  _vehicle_init_orig(self, *args, **kwargs)


def _get_owner_id(self):
  return self.user_id


def _set_owner_id(self, value):
  self.user_id = value


Vehicle = _Vehicle
Vehicle.__init__ = _vehicle_init
Vehicle.owner_id = property(_get_owner_id, _set_owner_id)

__all__ = ["Vehicle", "VehicleValuation"]
