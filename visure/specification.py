from __future__ import annotations
from pprint import pprint
from typing import TYPE_CHECKING

from visure.primatives.visure_object import VisureObject

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

    def __repr__(self):
        return f'Specification {self._id} ({self.name})'