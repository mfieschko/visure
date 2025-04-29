"""
visure.specification
====================

This module defines the VisureSpecification class for interacting with
Visure ALM specifications via the REST API.
"""

from __future__ import annotations
import asyncio
from pprint import pprint
import sys
from types import NoneType
from typing import TYPE_CHECKING, Union

from visure.attribute import VisureAttribute
from visure.element import VisureElement
from visure.primatives.REST.element import create_element_in_specification
from visure.primatives.REST.specification import get_elements_in_specification, get_attributes_in_specification
from visure.primatives.visure_object import VisureObject
from visure.utils import ResponseObject

if TYPE_CHECKING:
    from visure.visure import Visure
    from visure.project import VisureProject


class VisureSpecification(VisureObject):
    """
    Represents a specification within a Visure ALM project.

    Provides methods to fetch, create, and manage elements and attributes
    within the specification.
    """

    @classmethod
    def fromData(
        cls,
        visure_client: Visure,
        visure_project: VisureProject,
        **kwargs
    ) -> VisureSpecification:
        """
        Instantiate a VisureSpecification from raw API data.

        :param visure_client: Authenticated Visure client.
        :param visure_project: Parent VisureProject instance.
        :param kwargs: Raw specification data fields.
        :return: VisureSpecification instance populated with data.
        """
        spec = cls(visure_client, visure_project)
        for key, value in kwargs.items():
            setattr(spec, key, value)
        return spec

    def __init__(
        self,
        visure_client: Visure,
        project: VisureProject,
        id: int = None
    ):
        """
        Initialize a VisureSpecification instance.

        :param visure_client: Authenticated Visure client.
        :param project: Parent VisureProject instance.
        :param id: Optional specification ID.
        """
        super().__init__(visure_client, project, id)
        self.name: str | None = None
        self.elements: list[VisureElement] = []

    def __repr__(self) -> str:
        return f'Specification {self.id} ({self.name})'

    def getElements(
        self,
        ignoreActiveFilters: bool = True,
        search: str = None,
        deep: bool = False
    ) -> list[VisureElement]:
        """
        Fetch elements within this specification.

        :param ignoreActiveFilters: If True, ignore any active filters in the project.
        :param search: Optional search string to filter elements.
        :param deep: If True, fetch attributes for all elements asynchronously.
        :return: List of VisureElement instances.
        """
        self._project._set_target_project()
        self.elements = []
        raw_data = get_elements_in_specification(
            self._visure_client._authoring_url,
            self.id,
            self._visure_client._access_token,
            ignoreActiveFilters,
            search
        )
        for index, raw in enumerate(raw_data):
            # Skip metadata entry at index 0
            if index == 0:
                continue
            element = VisureElement.fromData(
                self._visure_client,
                self._project,
                **raw
            )
            self.elements.append(element)

        if deep:
            asyncio.run(self._fetch_attributes_async())

        return self.elements

    def createElement(
        self,
        parent: Union[VisureElement, NoneType] = None,
        asChildren: bool = False,
        count: int = 1
    ) -> Union[VisureElement, list[VisureElement]]:
        """
        Create one or more new elements under this specification.

        :param parent: Parent VisureElement instance or element ID, or None for root.
        :param asChildren: If True, create new elements as children of the parent.
        :param count: Number of elements to create.
        :return: A single VisureElement if count == 1, otherwise a list of VisureElement.
        """
        self._project._set_target_project()
        parent_id = parent.id if isinstance(parent, VisureElement) else (parent or self.id)
        new_elements: list[VisureElement] = []
        raw_data = create_element_in_specification(
            self._visure_client._authoring_url,
            self.id,
            self._visure_client._access_token,
            parent_id,
            asChildren,
            count
        )
        for raw in raw_data:
            element = VisureElement.fromData(
                self._visure_client,
                self._project,
                **raw
            )
            self.elements.append(element)
            new_elements.append(element)
        if len(new_elements) == 1:
            return new_elements[0]
        return new_elements

    async def _fetch_attributes_async(self) -> None:
        """
        Asynchronously fetch attributes for all elements in this specification.

        Used internally by getElements when deep=True.
        """
        tasks = [element.getAttributesAsync() for element in self.elements]
        await asyncio.gather(*tasks)

    def getAttributes(self) -> list[VisureAttribute]:
        """
        Fetch all attributes defined on this specification.

        :return: List of VisureAttribute instances.
        """
        self.attributes = []
        raw_data = get_attributes_in_specification(
            self._visure_client._authoring_url,
            self.id,
            self._visure_client._access_token
        )
        for raw in raw_data:
            attribute = VisureAttribute.fromData(
                self._visure_client,
                self._project,
                owner=self,
                **raw
            )
            self.attributes.append(attribute)
        return self.attributes
