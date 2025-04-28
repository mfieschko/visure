

# get_elements_in_specification

from __future__ import annotations
import asyncio
from pprint import pprint
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
    
    @classmethod
    def fromData(cls, visure_client : Visure, visure_project : VisureProject, **kwargs):
        target = cls(visure_client, visure_project)
        for k, v in kwargs.items():
            if isinstance(v, Dict):
                ResponseObject({k : v}, target._visure_client, target._project, target)
            else:
                setattr(target, k, v)
        return target

    def __init__(self, visure_client, project, id=None):
        super().__init__(visure_client, project, id)
        self.attributes = []

    def getAttributes(self) -> list[VisureAttribute]:
        from visure.primatives.REST.element import get_element_attributes
        self.attributes = []
        raw_data = get_element_attributes(self._visure_client._authoring_url, self.id, self._visure_client._access_token)
        for raw_attribute in raw_data:
            attribute = VisureAttribute.fromData(self._visure_client, self._project, owner=self, **raw_attribute)
            self.attributes.append(attribute)
        return self.attributes
    
    async def getAttributesAsync(self):
        from visure.primatives.REST.element import get_element_attributes_async
        self.attributes = []
        raw_data = await get_element_attributes_async(self._visure_client._authoring_url, self.id, self._visure_client._access_token)
        for raw_attribute in raw_data:
            attribute = VisureAttribute.fromData(self._visure_client, self._project, owner=self, **raw_attribute)
            self.attributes.append(attribute)
        return self.attributes
    
    def setName(self, text : str):
        set_name(self._visure_client._authoring_url, self.id, self._visure_client._access_token, text)

    def setCode(self, text : str):
        set_code(self._visure_client._authoring_url, self.id, self._visure_client._access_token, text)

    def setDescription(self, text : str):
        set_description(self._visure_client._authoring_url, self.id, self._visure_client._access_token, text)
        
    def getAvailableRelationships(self, target_element: Union[VisureElement, int]) -> List[Dict]:
        """
        Get available relationship types with another element.
        
        Args:
            target_element: Target VisureElement or element ID
            
        Returns:
            List of available relationship types with format:
            [{"sourceID": int, "targetID": int, "id": int, "name": str}]
        """
        target_id = target_element.id if isinstance(target_element, VisureElement) else target_element
        
        return get_available_relationships(
            self._visure_client._authoring_url,
            self.id,
            target_id,
            self._visure_client._access_token
        )
    
    def createLink(self, target_element: Union[VisureElement, int], relationship_type: Optional[Dict] = None, 
                  is_suspect: bool = False, reason: Optional[str] = None) -> Dict:
        """
        Create a link from this element to another element.
        
        Args:
            target_element: Target VisureElement or element ID
            relationship_type: Dictionary with 'id' and 'name' of the relationship type
                              (if None, will use the first available relationship type)
            is_suspect: Whether the link is suspect (default: False)
            reason: Reason for creating the link (default: None)
            
        Returns:
            API response
        """
        target_id = target_element.id if isinstance(target_element, VisureElement) else target_element
        
        # If relationship_type is not provided, get available relationship types
        if relationship_type is None:
            available_relationships = self.getAvailableRelationships(target_id)
            if not available_relationships:
                raise ValueError(f"No available relationship types between elements {self.id} and {target_id}")
            relationship_type = available_relationships[0]
        
        # Create the relationship
        relationship = {
            "id": relationship_type["id"],
            "sourceID": self.id,
            "targetID": target_id,
            "isSuspect": is_suspect,
            "projectID": self._project.id,
            "targetProjectID": self._project.id,  # Assuming same project, can be overridden if needed
            "motiveName": relationship_type["name"]
        }
        
        if reason:
            relationship["reason"] = reason
            
        return create_relationships(
            self._visure_client._authoring_url,
            [relationship],
            self._visure_client._access_token
        )
    
    def createLinks(self, target_elements: List[Union[VisureElement, int]], relationship_type: Optional[Dict] = None,
                   is_suspect: bool = False, reason: Optional[str] = None) -> Dict:
        """
        Create links from this element to multiple elements.
        
        Args:
            target_elements: List of target VisureElements or element IDs
            relationship_type: Dictionary with 'id' and 'name' of the relationship type
                              (if None, will use the first available relationship type for each target)
            is_suspect: Whether the links are suspect (default: False)
            reason: Reason for creating the links (default: None)
            
        Returns:
            API response
        """
        relationships = []
        
        for target_element in target_elements:
            target_id = target_element.id if isinstance(target_element, VisureElement) else target_element
            
            # If relationship_type is not provided, get available relationship types
            current_relationship_type = relationship_type
            if current_relationship_type is None:
                available_relationships = self.getAvailableRelationships(target_id)
                if not available_relationships:
                    raise ValueError(f"No available relationship types between elements {self.id} and {target_id}")
                current_relationship_type = available_relationships[0]
            
            # Create the relationship
            relationship = {
                "id": current_relationship_type["id"],
                "sourceID": self.id,
                "targetID": target_id,
                "isSuspect": is_suspect,
                "projectID": self._project.id,
                "targetProjectID": self._project.id,  # Assuming same project, can be overridden if needed
                "motiveName": current_relationship_type["name"]
            }
            
            if reason:
                relationship["reason"] = reason
                
            relationships.append(relationship)
            
        return create_relationships(
            self._visure_client._authoring_url,
            relationships,
            self._visure_client._access_token
        )
    
    def setType(self, type : Union[VisureBaseRequirementsType, str]):
        if isinstance(type, VisureBaseRequirementsType):
            type = type.value

        if len(self.attributes) == 0:
            asyncio.run(self.getAttributesAsync())

        if len(self._project.attribute_types) == 0:
            asyncio.run(self._project.getAttributeTypesAsync())

        # Get attribute that holds type
        type_attribute = next((x for x in self.attributes if x.name == "isRequirement"))

        # Get values to validate against
        valid_types_raw = type_attribute.getEnumValues()
        valid_types = [entry['name'] for entry in valid_types_raw]

        if type not in valid_types:
            raise Exception(f"Type not valid. Valid types: {valid_types}")

        self.modifyAttribute(type_attribute, VisureBaseType.ENUMERATED, False, [type])

    def modifyAttribute(self, attribue : Union[int, VisureAttribute], basetype : Union[VisureBaseType, str], isMultivalued: bool, values: list):
        type = basetype
        if isinstance(basetype, VisureBaseType):
            type = basetype.value

        attribute_id = attribue
        if isinstance(attribue, VisureAttribute):
            attribute_id = attribue.id
        modify_element_attribute(self._visure_client._authoring_url, self._visure_client._access_token, self.id, attribute_id, type, isMultivalued, values)

    def __repr__(self):
        return f"VisureElement({self.name})"