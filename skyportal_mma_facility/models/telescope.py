__all__ = ["Telescope"]

import sqlalchemy as sa
from skyportal_mma_facility.models import Base
from sqlalchemy.orm import relationship


class Telescope(Base):
    """A facility that can be used to observe targets."""

    name = sa.Column(sa.String, nullable=False, unique=True)
    nickname = sa.Column(sa.String, nullable=False, unique=True)
    lat = sa.Column(sa.Float, nullable=True)
    lon = sa.Column(sa.Float, nullable=True)
    elevation = sa.Column(sa.Float, nullable=True)
    diameter = sa.Column(sa.Float, nullable=False)
    skycam_link = sa.Column(sa.String, nullable=True)
    robotic = sa.Column(sa.Boolean, nullable=False, default=False)
    fixed_location = sa.Column(sa.Boolean, nullable=False, default=False)

    operational = sa.Column(sa.Boolean, nullable=False, default=True)

    instruments = relationship(
        "Instrument",
        back_populates="telescope",
        cascade="save-update, merge, refresh-expire, expunge",
        passive_deletes=True,
        doc="The Instruments on this telescope.",
    )
