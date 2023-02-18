# This module acts as a placeholder for generated schema.  After
# `setup_schema` is run from `models`, each table will have an
# associated schema here.  E.g., `models.Dog` will be matched by `schema.Dog`.


# From
# https://marshmallow-sqlalchemy.readthedocs.io/en/latest/recipes.html#automatically-generating-schemas-for-sqlalchemy-models

from marshmallow_sqlalchemy import (
    ModelConversionError as _ModelConversionError,
    SQLAlchemyAutoSchema as _SQLAlchemyAutoSchema,
)

from marshmallow import (
    Schema as _Schema,
    fields,
    validate,
    post_load,
    pre_dump,
    ValidationError,
)
from marshmallow_enum import EnumField


from skyportal_mma_facility.models import Base as _Base, DBSession as _DBSession
from skyportal_mma_facility.utils.env import load_env

import sys
import inspect
import numpy as np
from enum import Enum

_, cfg = load_env()


class ApispecEnumField(EnumField):
    """See https://github.com/justanr/marshmallow_enum/issues/24#issue-335162592"""

    def __init__(self, enum, *args, **kwargs):
        super().__init__(enum, *args, **kwargs)
        self.metadata["enum"] = [e.name for e in enum]


class Response(_Schema):
    status = ApispecEnumField(Enum("status", ["error", "success"]), required=True)
    message = fields.String()
    data = fields.Dict()


class Error(Response):
    status = ApispecEnumField(Enum("status", ["error"]), required=True)


class newsFeedPrefs(_Schema):
    numItems = fields.String()


class UserPreferences(_Schema):
    newsFeed = fields.Nested(newsFeedPrefs)


class UpdateUserPreferencesRequestJSON(_Schema):
    preferences = fields.Nested(UserPreferences)


def success(schema_name, base_schema=None):
    schema_fields = {
        "status": ApispecEnumField(Enum("status", ["success"]), required=True),
        "message": fields.String(),
    }

    if base_schema is not None:
        if isinstance(base_schema, list):
            schema_fields["data"] = fields.List(
                fields.Nested(base_schema[0]),
            )
        else:
            schema_fields["data"] = fields.Nested(base_schema)

    return type(schema_name, (_Schema,), schema_fields)


def setup_schema():
    """For each model, install a marshmallow schema generator as
    `model.__schema__()`, and add an entry to the `schema`
    module.

    """
    # for class_ in _Base._decl_class_registry.values():
    for mapper in _Base.registry.mappers:
        class_ = mapper.class_
        if hasattr(class_, "__tablename__"):
            if class_.__name__.endswith("Schema"):
                raise _ModelConversionError(
                    "For safety, setup_schema can not be used when a"
                    "Model class ends with 'Schema'"
                )

            def add_schema(schema_class_name, exclude=[], add_to_model=False):
                """Add schema to module namespace, and, optionally, to model object.

                Parameters
                ----------
                schema_class_name : str
                    Name of schema.
                exclude : list of str, optional
                    List of model attributes to exclude from schema. Defaults to `[]`.
                add_to_model : bool, optional
                    Boolean indicating whether to install this schema generator
                    on the model as `model.__schema__`. Defaults to `False`.
                """
                schema_class_meta = type(
                    f"{schema_class_name}_meta",
                    (),
                    {
                        "model": class_,
                        "sqla_session": _DBSession,
                        "load_instance": True,
                        "ordered": True,
                        "exclude": [],
                        "include_fk": True,
                        "include_relationships": True,
                    },
                )
                for exclude_attr in exclude:
                    if (
                        hasattr(class_, exclude_attr)
                        and getattr(class_, exclude_attr) is not None
                    ):
                        schema_class_meta.exclude.append(exclude_attr)

                schema_class = type(
                    schema_class_name,
                    (_SQLAlchemyAutoSchema,),
                    {"Meta": schema_class_meta},
                )

                if add_to_model:
                    setattr(class_, "__schema__", schema_class)

                setattr(sys.modules[__name__], schema_class_name, schema_class())

            schema_class_name = class_.__name__
            add_schema(
                schema_class_name,
                exclude=["time_interval", "healpix", "created_at", "modified"],
                add_to_model=True,
            )
            add_schema(
                f"{schema_class_name}NoID",
                exclude=[
                    "created_at",
                    "id",
                    "modified",
                    "owner_id",
                    "last_modified_by_id",
                    "healpix",
                    "time_interval",
                ],
            )
            if schema_class_name == "Obj":
                add_schema(
                    f"{schema_class_name}Post",
                    exclude=[
                        "created_at",
                        "redshift_history",
                        "modified",
                        "internal_key",
                    ],
                )


def register_components(spec):
    print("Registering schemas with APISpec")

    schemas = inspect.getmembers(
        sys.modules[__name__], lambda m: isinstance(m, _Schema)
    )

    for (name, schema) in schemas:
        spec.components.schema(name, schema=schema)

        single = "Single" + name
        arrayOf = "ArrayOf" + name + "s"
        spec.components.schema(single, schema=success(single, schema))
        spec.components.schema(arrayOf, schema=success(arrayOf, [schema]))


# Replace schemas by instantiated versions
# These are picked up in `setup_schema` for the registry
Response = Response()
Error = Error()
Success = success("Success")
