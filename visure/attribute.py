"""
visure.attribute
================

This module defines the VisureAttribute class and a parser for attribute
objects retrieved from the Visure ALM REST API.
"""

from __future__ import annotations
from pprint import pprint
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from visure.utils import ResponseObject
from visure.primatives.visure_object import VisureObject

if TYPE_CHECKING:
    from visure.visure import Visure
    from visure.project import VisureProject
    from visure.specification import VisureSpecification
    from visure.element import VisureElement


@ResponseObject.register_parser("attributes")
def parse_attributes(
    raw_list: List[Dict],
    visure_client: Visure,
    visure_project: VisureProject,
    owner: Optional[Union[VisureSpecification, VisureElement]] = None
) -> List[VisureAttribute]:
    """
    Parse a list of raw attribute dictionaries into VisureAttribute instances.

    :param raw_list: List of attribute dictionaries under the "attributes" key.
    :param visure_client: Authenticated Visure client.
    :param visure_project: Parent VisureProject instance.
    :param owner: Optional owner (VisureSpecification or VisureElement) of these attributes.
    :return: List of VisureAttribute instances.
    """
    return [
        VisureAttribute.fromData(visure_client, visure_project, owner=owner, **item)
        for item in raw_list
    ]


class VisureAttribute(VisureObject):
    """
    Represents an attribute of a specification or element in Visure ALM.

    Attributes:
        id (int): Unique identifier of the attribute.
        name (str): Name of the attribute.
        description (str, optional): Human-readable description.
        values (List[any], optional): Current value(s) of the attribute.
    """

    @classmethod
    def fromData(
        cls,
        visure_client: Visure,
        visure_project: VisureProject,
        owner: Optional[Union[VisureSpecification, VisureElement]] = None,
        **kwargs
    ) -> VisureAttribute:
        """
        Instantiate a VisureAttribute from raw API data.

        :param visure_client: Authenticated Visure client.
        :param visure_project: Parent VisureProject instance.
        :param owner: Optional owner object of the attribute.
        :param kwargs: Raw attribute data fields (must include 'id', 'name', etc.).
        :return: VisureAttribute instance populated with data.
        """
        target = cls(visure_client, visure_project, owner=owner, id=kwargs.get('id'))
        for key, value in kwargs.items():
            setattr(target, key, value)
        return target

    def __init__(
        self,
        visure_client: Visure,
        project: VisureProject,
        owner: Optional[Union[VisureSpecification, VisureElement]] = None,
        id: int = None
    ):
        """
        Initialize a VisureAttribute instance.

        :param visure_client: Authenticated Visure client.
        :param project: Parent VisureProject instance.
        :param owner: Optional owner (VisureSpecification or VisureElement).
        :param id: Unique identifier of the attribute.
        """
        super().__init__(visure_client, project, id)
        self._owner = owner

    def __repr__(self) -> str:
        base = f"({self.id}) {self.name}"
        if hasattr(self, "description"):
            base += f" - {self.description}"
        if hasattr(self, "values"):
            if hasattr(self, "isMultivalued") and not self.isMultivalued and len(self.values) > 0:
                base += f" - {self.values[0]}"
            else:
                base += f" - {self.values}"
        return base

    def getEnumValues(self) -> List[Dict]:
        """
        Retrieve enumeration values for this attribute type.

        Requires that project.getAttributeTypes() has been called to populate
        project.attribute_types before invoking.

        :return: List of dicts representing enum values, each with 'id' and 'name'.
        """
        reqtype = next(
            (x for x in self._project.attribute_types if x.name == self.name),
            None
        )
        if reqtype is None:
            raise Exception(
                "Attribute types not loaded; call project.getAttributeTypes() first."
            )
        return reqtype.enumValues
