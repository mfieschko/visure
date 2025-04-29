"""
visure.element
==============

This module defines the VisureElement class for interacting with Visure ALM
elements via the REST API.
"""

from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Dict, List, Union, Optional

from visure.attribute import VisureAttribute
from visure.primatives.REST.element import (
    modify_element_attribute,
    set_code,
    set_description,
    set_name,
    get_available_relationships,
    create_relationships
)
from visure.primatives.enums import VisureBaseRequirementsType, VisureBaseType
from visure.utils import ResponseObject
from visure.primatives.visure_object import VisureObject

if TYPE_CHECKING:
    from visure.visure import Visure
    from visure.project import VisureProject


class VisureElement(VisureObject):
    """
    Represents an element within a VisureSpecification.

    Provides methods to fetch and modify element attributes, set metadata,
    and manage relationships between elements.

    Attributes:
        id (int): Unique identifier of the element.
        name (str): Name of the element.
        code (str): Code of the element.
        description (str): Rich-text description (HTML) of the element.
        attributes (List[VisureAttribute]): List of attribute objects for this element.
    """

    @classmethod
    def fromData(
        cls,
        visure_client: Visure,
        visure_project: VisureProject,
        **kwargs
    ) -> VisureElement:
        """
        Instantiate a VisureElement from raw API data.

        :param visure_client: Authenticated Visure client.
        :param visure_project: Parent VisureProject instance.
        :param kwargs: Raw element data fields (must include 'id', 'name', etc.).
        :return: VisureElement instance populated with data.
        """
        element = cls(visure_client, visure_project)
        for key, value in kwargs.items():
            if isinstance(value, Dict):
                ResponseObject({key: value}, element._visure_client, element._project, element)
            else:
                setattr(element, key, value)
        return element

    def __init__(
        self,
        visure_client: Visure,
        project: VisureProject,
        id: int = None
    ):
        """
        Initialize a VisureElement instance.

        :param visure_client: Authenticated Visure client.
        :param project: Parent VisureProject instance.
        :param id: Optional element ID.
        """
        super().__init__(visure_client, project, id)
        self.attributes: List[VisureAttribute] = []

    def getAttributes(self) -> List[VisureAttribute]:
        """
        Fetch and return all attributes for this element.

        :return: List of VisureAttribute instances.
        """
        from visure.primatives.REST.element import get_element_attributes
        self.attributes = []
        raw_data = get_element_attributes(
            self._visure_client._authoring_url,
            self.id,
            self._visure_client._access_token
        )
        for raw in raw_data:
            attr = VisureAttribute.fromData(
                self._visure_client,
                self._project,
                owner=self,
                **raw
            )
            self.attributes.append(attr)
        return self.attributes

    async def getAttributesAsync(self) -> List[VisureAttribute]:
        """
        Asynchronously fetch and return all attributes for this element.

        :return: List of VisureAttribute instances.
        """
        from visure.primatives.REST.element import get_element_attributes_async
        self.attributes = []
        raw_data = await get_element_attributes_async(
            self._visure_client._authoring_url,
            self.id,
            self._visure_client._access_token
        )
        for raw in raw_data:
            attr = VisureAttribute.fromData(
                self._visure_client,
                self._project,
                owner=self,
                **raw
            )
            self.attributes.append(attr)
        return self.attributes

    def setName(self, text: str) -> None:
        """
        Update the element's name.

        :param text: New name for the element.
        """
        set_name(
            self._visure_client._authoring_url,
            self.id,
            self._visure_client._access_token,
            text
        )

    def setCode(self, text: str) -> None:
        """
        Update the element's code.

        :param text: New code for the element.
        """
        set_code(
            self._visure_client._authoring_url,
            self.id,
            self._visure_client._access_token,
            text
        )

    def setDescription(self, text: str) -> None:
        """
        Update the element's description.

        :param text: New HTML-formatted description.
        """
        set_description(
            self._visure_client._authoring_url,
            self.id,
            self._visure_client._access_token,
            text
        )

    def getAvailableRelationships(
        self,
        target_element: Union[VisureElement, int]
    ) -> List[Dict]:
        """
        Retrieve available relationship types between this element and another.

        :param target_element: Target VisureElement or element ID.
        :return: List of dicts representing relationship types, each with keys:
                 'sourceID', 'targetID', 'id', and 'name'.
        """
        target_id = target_element.id if isinstance(target_element, VisureElement) else target_element
        return get_available_relationships(
            self._visure_client._authoring_url,
            self.id,
            target_id,
            self._visure_client._access_token
        )

    def createLink(
        self,
        target_element: Union[VisureElement, int],
        relationship_type: Optional[Dict] = None,
        is_suspect: bool = False,
        reason: Optional[str] = None
    ) -> Dict:
        """
        Create a single relationship link from this element to another.

        :param target_element: Target VisureElement or element ID.
        :param relationship_type: Dict with 'id' and 'name'; if None, uses first available type.
        :param is_suspect: Whether the link should be marked as suspect.
        :param reason: Optional reason/motive for creating the link.
        :return: API response dict from create_relationships.
        :raises ValueError: If no available relationship types exist.
        """
        target_id = target_element.id if isinstance(target_element, VisureElement) else target_element
        rel_type = relationship_type
        if rel_type is None:
            available = self.getAvailableRelationships(target_id)
            if not available:
                raise ValueError(f"No available relationship types between {self.id} and {target_id}")
            rel_type = available[0]
        payload = {
            "id": rel_type["id"],
            "sourceID": self.id,
            "targetID": target_id,
            "isSuspect": is_suspect,
            "projectID": self._project.id,
            "targetProjectID": self._project.id,
            "motiveName": rel_type["name"]
        }
        if reason:
            payload["reason"] = reason
        return create_relationships(
            self._visure_client._authoring_url,
            [payload],
            self._visure_client._access_token
        )

    def createLinks(
        self,
        target_elements: List[Union[VisureElement, int]],
        relationship_type: Optional[Dict] = None,
        is_suspect: bool = False,
        reason: Optional[str] = None
    ) -> Dict:
        """
        Create relationship links from this element to multiple targets.

        :param target_elements: List of VisureElement or element IDs.
        :param relationship_type: Dict with 'id' and 'name'; if None, uses first available per target.
        :param is_suspect: Whether links should be marked as suspect.
        :param reason: Optional reason/motive for creating links.
        :return: API response dict from create_relationships.
        :raises ValueError: If no available relationship types exist for any target.
        """
        relationships: List[Dict] = []
        for target in target_elements:
            tgt_id = target.id if isinstance(target, VisureElement) else target
            rel_type = relationship_type
            if rel_type is None:
                available = self.getAvailableRelationships(tgt_id)
                if not available:
                    raise ValueError(f"No available relationship types between {self.id} and {tgt_id}")
                rel_type = available[0]
            entry = {
                "id": rel_type["id"],
                "sourceID": self.id,
                "targetID": tgt_id,
                "isSuspect": is_suspect,
                "projectID": self._project.id,
                "targetProjectID": self._project.id,
                "motiveName": rel_type["name"]
            }
            if reason:
                entry["reason"] = reason
            relationships.append(entry)
        return create_relationships(
            self._visure_client._authoring_url,
            relationships,
            self._visure_client._access_token
        )

    def setType(self, type: Union[VisureBaseRequirementsType, str]) -> None:
        """
        Set the built-in 'isRequirement' attribute enum value on this element.

        :param type: Requirement type as VisureBaseRequirementsType or its string value.
        :raises Exception: If provided type is not among valid enumeration names.
        """
        if isinstance(type, VisureBaseRequirementsType):
            type = type.value
        if not self.attributes:
            asyncio.run(self.getAttributesAsync())
        if not self._project.attribute_types:
            asyncio.run(self._project.getAttributeTypesAsync())
        type_attr = next((a for a in self.attributes if a.name == "isRequirement"), None)
        if type_attr is None:
            raise Exception("Type attribute 'isRequirement' not found on element.")
        valid = [e["name"] for e in type_attr.getEnumValues()]
        if type not in valid:
            raise Exception(f"Type not valid. Valid types: {valid}")
        self.modifyAttribute(type_attr, VisureBaseType.ENUMERATED, False, [type])

    def modifyAttribute(
        self,
        attribute: Union[int, VisureAttribute],
        basetype: Union[VisureBaseType, str],
        isMultivalued: bool,
        values: list
    ) -> None:
        """
        Modify an attribute value on this element.

        :param attribute: VisureAttribute instance or attribute ID.
        :param basetype: Attribute data type as VisureBaseType or its string value.
        :param isMultivalued: Whether multiple values are allowed.
        :param values: List of values to set for the attribute.
        """
        btype = basetype.value if isinstance(basetype, VisureBaseType) else basetype
        attr_id = attribute.id if isinstance(attribute, VisureAttribute) else attribute
        modify_element_attribute(
            self._visure_client._authoring_url,
            self._visure_client._access_token,
            self.id,
            attr_id,
            btype,
            isMultivalued,
            values
        )

    def getInLineLink(self, representation : Union[str, int, VisureAttribute] = "Code"):
        '''
        Gets the in-line link representation of this item. Used for global parameters.

        :param representation: Field to use for representation, can be the name of the parameter (Code, Name, Description), the index of the attribute, or the attribute object itself, defaults to "Code"
        :type representation: Union[str, int, VisureAttribute], optional
        :raises ValueError: _description_
        :raises ValueError: _description_
        :return: _description_
        :rtype: _type_
        '''
        # HREF format is #BM_VR_000547_-000001
        # What happens if the ID exceeds 6 digits? TODO find out
        # What does BM_VR_ mean? does it change? TODO find out
        id_field = f"{self.id:0{6}d}"
        attribute_index = None
        attribute_name = None

        if isinstance(representation, VisureAttribute):
            attribute_index = representation.id
            attribute_name = representation.name
        elif isinstance(representation, int):
            attribute_index = representation
            attribute_name = self.attributes[attribute_index].name
        elif isinstance(representation, str):
            attribute_name = representation
            match representation:
                case "Code":
                    attribute_index = 1
                case "Name":
                    attribute_index = 2
                case "Description":
                    attribute_index = 3
                case _:
                    raise ValueError()
        else:
            raise ValueError()
        
        attribute_index_field = f"{attribute_index:0{6}d}"

        return f'<a href="#BM_VR_{id_field}_{attribute_index_field}" target="_blank" rel="nofollow noopener noreferrer">{self.id} ({attribute_name})</a>'

    def __repr__(self) -> str:
        return f"VisureElement({self.name})"
