

from enum import Enum


class VisureLicenseType(Enum):
    AUTHORING = "AUTHORING"

class VisureBaseType(Enum):
    ENUMERATED  = "ENUMERATED"
    INTEGER     = "INTEGER"
    FLOAT       = "FLOAT"
    DATE        = "DATE"
    TEXT        = "TEXT"
    BOOLEAN     = "BOOLEAN"
    USER        = "USER"

class VisureBaseRequirementsType(Enum):
    HEADING  = "Heading"
    ITEM     = "Item"
    TEXT     = "Text"