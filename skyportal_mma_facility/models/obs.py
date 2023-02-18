__all__ = ["Observation", "ObservationPlan"]

import sqlalchemy as sa
from skyportal_mma_facility.models import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property


class Observation(Base):

    # SKYPORTAL SPECIFIC

    request_id = sa.Column(
        sa.Integer,
        nullable=False,
        doc="The ID of the request of the observation.",
    )

    field_id = sa.Column(
        sa.BigInteger,
        nullable=False,
        doc="The ID of the field of the observation.",
    )

    ra = sa.Column(
        sa.Float,
        nullable=False,
        doc="The RA of the observation.",
    )

    dec = sa.Column(
        sa.Float,
        nullable=False,
        doc="The DEC of the observation.",
    )

    filter = sa.Column(
        sa.String,
        nullable=False,
        doc="The sncosmo filter used for the observation.",
    )

    exposure_time = sa.Column(
        sa.Float,
        nullable=False,
        doc="The exposure time of the observation.",
    )

    program_pi = sa.Column(
        sa.String,
        nullable=False,
        doc="The PI of the program of the observation.",
    )

    # END SKYPORTAL SPECIFIC

    status = sa.Column(
        sa.String,
        nullable=False,
        default="pending",
        index=True,
        doc="Status of the observation.",
    )

    # we want the date, exposure_time, and a completed flag
    date = sa.Column(
        sa.DateTime,
        nullable=True,
        default=None,
        doc="The date of the observation, set when it is completed.",
    )

    _fits_path = sa.Column(
        "fits",
        sa.String,
        nullable=True,
        doc="The path to the FITS file of the observation. Added once the observation is completed.",
    )

    instrument_id = sa.Column(
        sa.ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="The ID of the Instrument that performs the observation.",
    )
    instrument = relationship(
        "Instrument",
        back_populates="observations",
        doc="The Instrument that performs the observation.",
    )

    observation_plan_id = sa.Column(
        sa.ForeignKey("observationplans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="The ID of the Observation Plan that contains the observation.",
    )

    observation_plan = relationship(
        "ObservationPlan",
        back_populates="observations",
        doc="The Observation Plan that contains the observation.",
    )

    def save(self, path):
        self._fits_path = path

    def data(self):
        # later, we want that method to open the fits file and return the data
        return self._fits_path


class ObservationPlan(Base):

    # this column has to be unique
    queue_name = sa.Column(
        sa.String,
        nullable=False,
        unique=True,
        doc="The name of the queue that the observation plan is part of.",
        index=True,
    )

    user = sa.Column(
        sa.String,
        nullable=False,
        doc="The user that created the observation plan.",
    )

    status = sa.Column(
        sa.String,
        nullable=False,
        default="pending",
        index=True,
        doc="Status of the observation plan's processing.",
    )

    instrument_id = sa.Column(
        sa.ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="The ID of the Instrument that hosts the Observation Plan.",
    )
    instrument = relationship(
        "Instrument",
        back_populates="observation_plans",
        doc="The Instrument that hosts the Observation Plan.",
    )

    validity_window_start = sa.Column(
        sa.DateTime,
        nullable=False,
        doc="The start of the validity window of the observation plan.",
    )

    validity_window_end = sa.Column(
        sa.DateTime,
        nullable=False,
        doc="The end of the validity window of the observation plan.",
    )

    payload = sa.Column(
        JSONB,
        nullable=False,
        doc="The payload of the observation plan.",
    )

    observations = relationship(
        "Observation",
        back_populates="observation_plan",
        doc="The Observations that are part of the Observation Plan.",
    )
