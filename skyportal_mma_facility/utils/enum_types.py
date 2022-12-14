import astropy.units as u
import inspect
import numpy as np
import sncosmo
from sncosmo.bandpasses import _BANDPASSES
from sncosmo.magsystems import _MAGSYSTEMS
import sqlalchemy as sa

from enum import Enum
from skyportal_mma_facility.utils.env import load_env

_, cfg = load_env()

# load additional bandpasses into the SN comso registry
existing_bandpasses_names = [val["name"] for val in _BANDPASSES.get_loaders_metadata()]
additional_bandpasses_names = []
for additional_bandpasses in cfg.get("additional_bandpasses", []):
    name = additional_bandpasses.get("name")
    if not name:
        continue
    if name in existing_bandpasses_names:
        print(
            f"Additional Bandpass name={name} is already in the sncosmo registry. Skipping."
        )
    try:
        wavelength = np.array(additional_bandpasses.get("wavelength"))
        transmission = np.array(additional_bandpasses.get("transmission"))
        band = sncosmo.Bandpass(wavelength, transmission, name=name, wave_unit=u.AA)
    except Exception as e:
        print(f"Could not make bandpass for {name}: {e}")
        continue

    sncosmo.registry.register(band)
    additional_bandpasses_names.append(name)
    print(f"added custom bandpass '{name}'")


def force_render_enum_markdown(values):
    return ", ".join(list(map(lambda v: f"`{v}`", values)))


ALLOWED_MAGSYSTEMS = tuple(val["name"] for val in _MAGSYSTEMS.get_loaders_metadata())
# though in the registry, the additional bandpass names are not in the _BANDPASSES list
ALLOWED_BANDPASSES = tuple(existing_bandpasses_names + additional_bandpasses_names)

INSTRUMENT_TYPES = ("imager", "spectrograph", "imaging spectrograph")
FOLLOWUP_PRIORITIES = ("1", "2", "3", "4", "5")

allowed_magsystems = sa.Enum(
    *ALLOWED_MAGSYSTEMS, name="magsystems", validate_strings=True
)
allowed_bandpasses = sa.Enum(
    *ALLOWED_BANDPASSES, name="bandpasses", validate_strings=True
)
instrument_types = sa.Enum(
    *INSTRUMENT_TYPES, name="instrument_types", validate_strings=True
)
followup_priorities = sa.Enum(
    *FOLLOWUP_PRIORITIES, name="followup_priorities", validate_strings=True
)
py_allowed_magsystems = Enum("magsystems", ALLOWED_MAGSYSTEMS)
py_allowed_bandpasses = Enum("bandpasses", ALLOWED_BANDPASSES)
py_followup_priorities = Enum("priority", FOLLOWUP_PRIORITIES)


sqla_enum_types = [
    allowed_bandpasses,
    instrument_types,
    followup_priorities,
]
