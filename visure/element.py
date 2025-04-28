

# get_elements_in_specification

from __future__ import annotations
from pprint import pprint
from typing import TYPE_CHECKING, Dict, List

from visure.attribute import VisureAttribute
from visure.primatives.REST.element import set_code, set_description, set_name
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

    def getAttributes(self):
        from visure.primatives.REST.element import get_element_attributes
        self.attributes = []
        raw_data = get_element_attributes(self._visure_client._authoring_url, self.id, self._visure_client._access_token)
        pprint(raw_data)
        for raw_attribute in raw_data:
            attribute = VisureAttribute.fromData(self._visure_client, self._project, **raw_attribute)
            self.attributes.append(attribute)
        return self.attributes
    
    async def getAttributesAsync(self):
        from visure.primatives.REST.element import get_element_attributes_async
        self.attributes = []
        raw_data = await get_element_attributes_async(self._visure_client._authoring_url, self.id, self._visure_client._access_token)
        for raw_attribute in raw_data:
            attribute = VisureAttribute.fromData(self._visure_client, self._project, **raw_attribute)
            self.attributes.append(attribute)
        return self.attributes
    
    def setName(self, text : str):
        set_name(self._visure_client._authoring_url, self.id, self._visure_client._access_token, text)

    def setCode(self, text : str):
        set_code(self._visure_client._authoring_url, self.id, self._visure_client._access_token, text)

    def setDescription(self, text : str):
        set_description(self._visure_client._authoring_url, self.id, self._visure_client._access_token, text)
