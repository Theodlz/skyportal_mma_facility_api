import contextvars
import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from skyportal_mma_facility.utils.json_util import to_json

session_context_id = contextvars.ContextVar("request_id", default=None)


DBSession = scoped_session(sessionmaker(), scopefunc=session_context_id.get)

EXECUTEMANY_PAGESIZE = 50000

utcnow = func.timezone("UTC", func.current_timestamp())


class _VerifiedSession(sa.orm.session.Session):
    def __init__(self, **kwargs):
        super().__init__()

    def commit(self):
        super().commit()


def VerifiedSession():
    return scoped_session(
        sessionmaker(class_=_VerifiedSession),
        scopefunc=session_context_id.get,
    )()


class BaseMixin:
    @classmethod
    def select(
        cls,
        user_or_token,
        mode="read",
        options=[],
        columns=None,
    ):
        """Return the select statement for all database records accessible by the
        specified User or token.

        Parameters
        ----------
        user_or_token : `baselayer.app.models.User` or `baselayer.app.models.Token`
            The User or Token to check.
        mode : string
            Type of access to check. Valid choices are `['create', 'read', 'update',
            'delete']`.
        options : list of `sqlalchemy.orm.MapperOption`s
            Options that will be passed to `options()` in the loader query.
        columns : list of sqlalchemy.Column, optional, default None
            The columns to retrieve from the target table. If None, queries
            the mapped class directly and returns mapped instances.

        Returns
        -------
        sqlalchemy select object
        """

        logic = getattr(cls, mode)
        stmt = logic.select_accessible_rows(cls, user_or_token, columns=columns)
        for option in options:
            stmt = stmt.options(option)
        return stmt

    query = DBSession.query_property()

    id = sa.Column(
        sa.Integer,
        primary_key=True,
        autoincrement=True,
        doc="Unique object identifier.",
    )
    created_at = sa.Column(
        sa.DateTime,
        nullable=False,
        default=utcnow,
        index=True,
        doc="UTC time of insertion of object's row into the database.",
    )
    modified = sa.Column(
        sa.DateTime,
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
        doc="UTC time the object's row was last modified in the database.",
    )

    @declared_attr
    def __tablename__(cls):
        """The name of this class's mapped database table."""
        return cls.__name__.lower() + "s"

    __mapper_args__ = {"confirm_deleted_rows": False}

    def __str__(self):
        return to_json(self)

    def __repr__(self):
        attr_list = [
            f"{c.name}={getattr(self, c.name)}" for c in self.__table__.columns
        ]
        return f"<{type(self).__name__}({', '.join(attr_list)})>"

    def to_dict(self):
        """Serialize this object to a Python dictionary."""
        if sa.inspection.inspect(self).expired:
            self = DBSession().merge(self)
            DBSession().refresh(self)
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


Base = declarative_base(cls=BaseMixin)


def init_db(
    user,
    database,
    password=None,
    host=None,
    port=None,
    autoflush=True,
    engine_args={},
):
    """
    Parameters
    ----------
    engine_args : dict
        - `pool_size`:
          The number of connections maintained to the DB. Default 5.

        - `max_overflow`:
          The number of additional connections that will be made as needed.
           Once these extra connections have been used, they are discarded.
          Default 10.

        - `pool_recycle`:
           Prevent the pool from using any connection that is older than this
           (specified in seconds).
           Default 3600.

    """
    url = "postgresql://{}:{}@{}:{}/{}"
    url = url.format(user, password or "", host or "", port or "", database)

    default_engine_args = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 3600,
    }
    conn = sa.create_engine(
        url,
        client_encoding="utf8",
        executemany_mode="values",
        executemany_values_page_size=EXECUTEMANY_PAGESIZE,
        **{**default_engine_args, **engine_args},
    )

    DBSession.configure(bind=conn, autoflush=autoflush, future=True)
    Base.metadata.bind = conn

    return conn
