"""
visure.project
==============

This module defines the VisureProject class for interacting with
Visure ALM projects via the REST API.
"""

from __future__ import annotations
from pprint import pprint
from typing import TYPE_CHECKING, List, Dict, Optional

import requests

from visure.attribute import VisureAttribute
from visure.primatives.REST.project import (
    get_attribute_types_in_project,
    get_project_info,
    set_active_project
)
from visure.primatives.REST.specification import get_specifications
from visure.primatives.REST.element import create_relationships

if TYPE_CHECKING:
    from visure.visure import Visure
    from visure.specification import VisureSpecification


class VisureProject:
    """
    Represents a Visure ALM project.

    Provides methods to retrieve specifications, attribute types, and
    to create relationships between elements within the project.

    Attributes:
        visure (Visure): Authenticated Visure client.
        id (int): Unique project identifier.
        name (str): Project name.
        specifications (list[VisureSpecification] | None): Cached specifications.
        attribute_types (list[VisureAttribute]): Cached attribute types.
    """

    @classmethod
    def fromData(cls, visure_client: Visure, **kwargs) -> VisureProject:
        """
        Instantiate a VisureProject from raw API data.

        :param visure_client: Authenticated Visure client.
        :param kwargs: Raw project data (must include "id" key).
        :return: VisureProject instance populated with data.
        :raises Exception: If "id" is missing in the raw data.
        """
        project_id = kwargs.get("id")
        if project_id is None:
            raise Exception("Project ID not valid")
        project = cls(visure_client, project_id)
        for key, value in kwargs.items():
            setattr(project, key, value)
        return project

    def __init__(self, visure_client: Visure, project_id: int):
        """
        Initialize a VisureProject instance.

        :param visure_client: Authenticated Visure client.
        :param project_id: ID of the Visure project.
        """
        self.visure = visure_client
        self.id = project_id
        self.name: Optional[str] = None
        self.specifications: Optional[List[VisureSpecification]] = None
        self.attribute_types: List[VisureAttribute] = []

    def _set_target_project(self, role: Optional[int] = None) -> None:
        """
        Set this project as the active context on the Visure server.

        :param role: Optional role/group ID to use when activating the project.
                     If None, uses the first available group in self.groups.
        """
        if self.id != self.visure._current_project_id:
            if role is None:
                role = self.groups[0]["id"]
            set_active_project(
                self.visure._authoring_url,
                self.id,
                role,
                self.visure._access_token
            )
            self.visure._current_project_id = self.id

    def _reload(self) -> None:
        """
        Reload and print detailed project information from the server.

        Intended for debugging; prints the API response.
        """
        pprint(get_project_info(
            self.visure._authoring_url,
            self.id,
            self.visure._access_token
        ))

    def __repr__(self) -> str:
        return f"Visure Project {self.id} ({self.name})"

    def getSpecifications(self) -> List[VisureSpecification]:
        """
        Fetch and return the specifications within this project.

        :return: List of VisureSpecification instances.
        """
        from visure.specification import VisureSpecification
        self._set_target_project()
        self.specifications = []
        for spec_data in get_specifications(
            self.visure._authoring_url,
            self.visure._access_token
        ):
            spec = VisureSpecification.fromData(
                self.visure,
                self,
                **spec_data
            )
            self.specifications.append(spec)
        return self.specifications

    def createLinks(self, relationships: List[Dict]) -> Dict:
        """
        Create multiple relationships between elements in this project.

        :param relationships: List of dicts, each containing:
            source: VisureElement or int ID of source element.
            target: VisureElement or int ID of target element.
            relationship_type: Dict with 'id' and 'name' (optional).
            is_suspect: bool flag marking link as suspect (default False).
            reason: Optional[str] motive for link.
            target_project_id: int ID of target project (default this project).
        :return: API response from create_relationships.
        :raises ValueError: If source or target is missing or no relationship types.
        """
        from visure.element import VisureElement

        self._set_target_project()
        formatted = []
        for rel in relationships:
            src = rel.get("source")
            tgt = rel.get("target")
            rel_type = rel.get("relationship_type")
            is_sus = rel.get("is_suspect", False)
            reason = rel.get("reason")
            tgt_proj = rel.get("target_project_id", self.id)

            if src is None or tgt is None:
                raise ValueError("Both source and target must be provided")
            src_id = src.id if isinstance(src, VisureElement) else src
            tgt_id = tgt.id if isinstance(tgt, VisureElement) else tgt

            if rel_type is None:
                temp = VisureElement(self.visure, self, src_id)
                types = temp.getAvailableRelationships(tgt_id)
                if not types:
                    raise ValueError(
                        f"No available relationship types between {src_id} and {tgt_id}"
                    )
                rel_type = types[0]

            entry = {
                "id": rel_type["id"],
                "sourceID": src_id,
                "targetID": tgt_id,
                "isSuspect": is_sus,
                "projectID": self.id,
                "targetProjectID": tgt_proj,
                "motiveName": rel_type["name"]
            }
            if reason:
                entry["reason"] = reason
            formatted.append(entry)

        return create_relationships(
            self.visure._authoring_url,
            formatted,
            self.visure._access_token
        )

    def getAttributeTypes(self) -> List[VisureAttribute]:
        """
        Fetch and return attribute types defined in this project.

        :return: List of VisureAttribute instances.
        """
        self._set_target_project()
        raw = get_attribute_types_in_project(
            self.visure._authoring_url,
            self.visure._access_token
        )
        self.attribute_types = [
            VisureAttribute.fromData(
                self.visure,
                self,
                owner=self,
                **attr
            ) for attr in raw
        ]
        return self.attribute_types

    async def getAttributeTypesAsync(self) -> List[VisureAttribute]:
        """
        Asynchronously fetch attribute types defined in this project.

        :return: List of VisureAttribute instances.
        """
        from visure.primatives.REST.project import \
            get_attribute_types_in_project_async
        self.attribute_types = []
        raw = await get_attribute_types_in_project_async(
            self.visure._authoring_url,
            self.id,
            self.visure._access_token
        )
        for attr in raw:
            self.attribute_types.append(
                VisureAttribute.fromData(
                    self.visure,
                    self,
                    owner=self,
                    **attr
                )
            )
        return self.attribute_types
