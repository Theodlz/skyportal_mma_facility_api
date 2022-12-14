__all__ = ["Instrument"]

import re

import sqlalchemy as sa
from skyportal_mma_facility.models import Base, DBSession
from sqlalchemy.orm import relationship
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from skyportal_mma_facility.utils.enum_types import (
    instrument_types,
    allowed_bandpasses,
)


class ArrayOfEnum(ARRAY):
    def bind_expression(self, bindvalue):
        return cast(bindvalue, self)

    def result_processor(self, dialect, coltype):
        super_rp = super().result_processor(dialect, coltype)

        def handle_raw_string(value):
            if value is None or value == "{}":  # 2nd case, empty array
                return []
            inner = re.match(r"^{(.*)}$", value).group(1)
            return inner.split(",")

        def process(value):
            return super_rp(handle_raw_string(value))

        return process


class Instrument(Base):
    name = sa.Column(sa.String, unique=True, nullable=False, doc="Instrument name.")
    type = sa.Column(
        instrument_types,
        nullable=False,
        doc="Instrument type, one of Imager, Spectrograph, or Imaging Spectrograph.",
    )

    band = sa.Column(
        sa.String,
        doc="The spectral band covered by the instrument " "(e.g., Optical, IR).",
    )
    telescope_id = sa.Column(
        sa.ForeignKey("telescopes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="The ID of the Telescope that hosts the Instrument.",
    )
    telescope = relationship(
        "Telescope",
        back_populates="instruments",
        doc="The Telescope that hosts the Instrument.",
    )

    filters = sa.Column(
        ArrayOfEnum(allowed_bandpasses),
        nullable=False,
        default=[],
        doc="List of filters on the instrument (if any).",
    )

    sensitivity_data = sa.Column(
        JSONB,
        nullable=True,
        doc="JSON describing the filters on the instrument and the filter's corresponding limiting magnitude and exposure time.",
    )

    operational = sa.Column(sa.Boolean, nullable=False, default=True)

    observations = relationship(
        "Observation",
        back_populates="instrument",
        cascade="save-update, merge, refresh-expire, expunge",
        passive_deletes=True,
        doc="The Observations performed with this Instrument.",
    )

    observation_plans = relationship(
        "ObservationPlan",
        back_populates="instrument",
        cascade="save-update, merge, refresh-expire, expunge",
        passive_deletes=True,
        doc="The Observation Plans that use this Instrument.",
    )
