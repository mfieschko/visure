from __future__ import annotations
from pprint import pprint
from typing import TYPE_CHECKING, Dict, List

from visure.utils import ResponseObject
from visure.primatives.visure_object import VisureObject

if TYPE_CHECKING:
    from visure.visure import Visure
    from visure.project import VisureProject
    

@ResponseObject.register_parser("attributes")
def parse_attributes(raw_list: List[Dict], visure_client : Visure, visure_project : VisureProject) -> List[VisureAttribute]:
    # raw_list is the list of dicts under "attributes"
    return [VisureAttribute.fromData(visure_client, visure_project, **item) for item in raw_list]

class VisureAttribute(VisureObject):
    
    @classmethod
    def fromData(cls, visure_client : Visure, visure_project : VisureProject, **kwargs):
        target = cls(visure_client, visure_project)
        for k, v in kwargs.items():
            setattr(target, k, v)
        return target

    def __init__(self, visure_client, project, id=None):
        super().__init__(visure_client, project, id)

    def __repr__(self):
        base = f"({self.id}) {self.name}"
        if hasattr(self, "description"):
            base += f" - {self.description}"
        if hasattr(self, "values"):
            if hasattr(self, "isMultivalued") and not self.isMultivalued and len(self.values) > 0:
                base += f" - {self.values[0]}"
            else:
                base += f" - {self.values}"
        return base
    
    def getEnumValues(self):
        ''' This only works if project.getAttributeTypes() was already called '''
        reqtype_type =  next((x for x in self._project.attribute_types if x.name == self.name))
        return reqtype_type.enumValues