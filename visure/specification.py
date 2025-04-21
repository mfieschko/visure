from __future__ import annotations
import asyncio
from pprint import pprint
from typing import TYPE_CHECKING

from visure.element import VisureElement
from visure.primatives.visure_object import VisureObject
from visure.utils import ResponseObject

if TYPE_CHECKING:
    from visure.visure import Visure
    from visure.project import VisureProject

class VisureSpecification(VisureObject):

    @classmethod
    def fromData(cls, visure_client : Visure, visure_project : VisureProject, data : dict):
        id = data.get("id")
        if id == None:
            raise Exception("ID not valid for specification")
        
        target = cls(visure_client, visure_project, id)
        target.name = data.get("name")
        target.author = data.get("author")
        target.prefix = data.get("prefix")
        target.docType = data.get("docType")
        target.elementType = data.get("elementType")
        target.checkInStatus = data.get("checkInStatus")
        target.parentId = data.get("parentId")
        return target
    
    def __init__(self, visure_client, project, id=None):
        super().__init__(visure_client, project, id)
        self.name = None
        self.elements = None

    def __repr__(self):
        return f'Specification {self.id} ({self.name})'
    
    def getElements(self, ignoreActiveFilters : bool = True, search : str = None, deep : bool = False):
        from visure.primatives.REST.specification import get_elements_in_specification
        self.elements = []
        raw_data = get_elements_in_specification(self._visure_client._authoring_url, self.id, self._visure_client._access_token, ignoreActiveFilters, search)
        for raw_element in raw_data:
            element = VisureElement.fromData(self._visure_client, self._project, **raw_element)
            self.elements.append(element)
        
        # If deep=True, fetch attributes for all elements asynchronously
        if deep:
            asyncio.run(self._fetch_attributes_async())
            
        return self.elements
    
    async def _fetch_attributes_async(self):
        """
        Asynchronously fetch attributes for all elements in the specification.
        This is used internally by getElements when deep=True.
        """
        tasks = [element.getAttributesAsync() for element in self.elements]
        await asyncio.gather(*tasks)
