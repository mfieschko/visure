from __future__ import annotations
from pprint import pprint
from typing import TYPE_CHECKING, List, Dict, Union, Optional

import requests

from visure.primatives.REST.project import get_project_info, set_active_project
from visure.primatives.REST.specification import get_specifications
from visure.primatives.REST.element import create_relationships

if TYPE_CHECKING:
    from visure.visure import Visure
    from visure.specification import VisureSpecification

class VisureProject:

    @classmethod
    def fromData(cls, visure_client : Visure, **kwargs):
        id = kwargs.get("id")
        if id == None:
            raise Exception("Project ID not valid")
        target = cls(visure_client, id)
        for k, v in kwargs.items():
            setattr(target, k, v)
        return target

    def __init__(self, visure_client : Visure, project_id : int):
        self.visure = visure_client
        self.id = project_id
        self.name = None
        self.specifications = None

    def _set_target_project(self, role = None):
        if self.id != self.visure._current_project_id:
            # Fetch the first appropriate role if one is not given
            if role == None:
                role = self.groups[0]["id"]
            
            set_active_project(self.visure._authoring_url, self.id, role, self.visure._access_token) # TODO: Groups are stored in project info, maybe validate against that?
            
            self.visure._current_project_id = self.id

    def _reload(self):
        pprint(get_project_info(self.visure._authoring_url, self.id, self.visure._access_token))

    def __repr__(self):
        return f"Visure Project {self.id} ({self.name})"
    
    def getSpecifications(self) -> list[VisureSpecification]:
        from visure.specification import VisureSpecification
        self._set_target_project()
        self.specifications = []
        for specification_data in get_specifications(self.visure._authoring_url, self.visure._access_token):
            target = VisureSpecification.fromData(self.visure, self, **specification_data)
            self.specifications.append(target)
        return self.specifications
    
    def createLinks(self, relationships: List[Dict]) -> Dict:
        """
        Create multiple relationships between elements in the project.
        
        Args:
            relationships: List of dictionaries with:
                - source: Source VisureElement or element ID
                - target: Target VisureElement or element ID
                - relationship_type: Dictionary with 'id' and 'name' of the relationship type
                                    (if None, will use the first available relationship type)
                - is_suspect: Whether the link is suspect (default: False)
                - reason: Reason for creating the link (optional)
                - target_project_id: ID of the target project (default: same as source project)
                
        Returns:
            API response
        """
        from visure.element import VisureElement
        
        # Ensure we're in the correct project context
        self._set_target_project()
        
        # Format the relationships for the API
        formatted_relationships = []
        
        for relationship in relationships:
            source = relationship.get("source")
            target = relationship.get("target")
            relationship_type = relationship.get("relationship_type")
            is_suspect = relationship.get("is_suspect", False)
            reason = relationship.get("reason")
            target_project_id = relationship.get("target_project_id", self.id)
            
            if source is None or target is None:
                raise ValueError("Both source and target must be provided for each relationship")
            
            source_id = source.id if isinstance(source, VisureElement) else source
            target_id = target.id if isinstance(target, VisureElement) else target
            
            # If relationship_type is not provided, get available relationship types
            if relationship_type is None:
                # Create a temporary element to get available relationships
                from visure.element import VisureElement
                temp_element = VisureElement(self.visure, self, source_id)
                available_relationships = temp_element.getAvailableRelationships(target_id)
                if not available_relationships:
                    raise ValueError(f"No available relationship types between elements {source_id} and {target_id}")
                relationship_type = available_relationships[0]
            
            # Create the relationship
            formatted_rel = {
                "id": relationship_type["id"],
                "sourceID": source_id,
                "targetID": target_id,
                "isSuspect": is_suspect,
                "projectID": self.id,
                "targetProjectID": target_project_id,
                "motiveName": relationship_type["name"]
            }
            
            if reason:
                formatted_rel["reason"] = reason
                
            formatted_relationships.append(formatted_rel)
        
        # Create the relationships
        return create_relationships(
            self.visure._authoring_url,
            formatted_relationships,
            self.visure._access_token
        )
