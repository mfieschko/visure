from __future__ import annotations
import asyncio
from pprint import pprint
import sys
from types import NoneType
from typing import TYPE_CHECKING, Union

from visure.element import VisureElement
from visure.primatives.REST.element import create_element_in_specification
from visure.primatives.visure_object import VisureObject
from visure.utils import ResponseObject

if TYPE_CHECKING:
    from visure.visure import Visure
    from visure.project import VisureProject

class VisureSpecification(VisureObject):

    @classmethod
    def fromData(cls, visure_client : Visure, visure_project : VisureProject, **kwargs):
        target = cls(visure_client, visure_project)
        for k, v in kwargs.items():
            setattr(target, k, v)
        return target
    
    def __init__(self, visure_client, project, id=None):
        super().__init__(visure_client, project, id)
        self.name = None
        self.elements = []

    def __repr__(self):
        return f'Specification {self.id} ({self.name})'
    
    def getElements(self, ignoreActiveFilters : bool = True, search : str = None, deep : bool = False):
        """Gets the elements inside the specification

        Args:
            ignoreActiveFilters (bool, optional): Ignore any active filters in the project. Defaults to True.
            search (str, optional): String to search for. Defaults to None.
            deep (bool, optional): If set to True, fetch all information about the elements. Defaults to False. This performs asynchronously under the hood with aiohttp.

        Returns:
            _type_: _description_
        """
        self._project._set_target_project()
        from visure.primatives.REST.specification import get_elements_in_specification
        self.elements = []
        raw_data = get_elements_in_specification(self._visure_client._authoring_url, self.id, self._visure_client._access_token, ignoreActiveFilters, search)
        for i, raw_element in enumerate(raw_data):
            # The first element is metadata for the document
            # TODO: Verify this assumption
            if i == 0:
                continue
            element = VisureElement.fromData(self._visure_client, self._project, **raw_element)
            self.elements.append(element)
        
        # If deep=True, fetch attributes for all elements asynchronously
        # TODO: Evaluate if any other information needs to be fetched, such as description
        if deep:
            asyncio.run(self._fetch_attributes_async())
            
        return self.elements
    
    def createElement(self, parent : Union[VisureElement, NoneType] = None, asChildren = False, count = 1) -> Union[VisureElement, list[VisureElement]]:
        self._project._set_target_project()
        parent_id = self.id
        if isinstance(parent, VisureElement):
            parent_id = parent.id
        elif parent == None:
            parent_id = self.id
        else:
            # Passing a number maybe?
            parent_id = parent

        new_elements = []
        raw_data = create_element_in_specification(self._visure_client._authoring_url, self.id, self._visure_client._access_token, parent_id, asChildren, count)

        for raw_element in raw_data:
            element = VisureElement.fromData(self._visure_client, self._project, **raw_element)
            self.elements.append(element)
            new_elements.append(element)
        
        if len(new_elements) == 1:
            return new_elements[0]
        return new_elements

    async def _fetch_attributes_async(self):
        """
        Asynchronously fetch attributes for all elements in the specification.
        This is used internally by getElements when deep=True.
        """
        tasks = [element.getAttributesAsync() for element in self.elements]
        await asyncio.gather(*tasks)
