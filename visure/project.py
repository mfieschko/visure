from __future__ import annotations
from pprint import pprint
from typing import TYPE_CHECKING

import requests

from visure.primatives.REST.project import get_project_info, set_active_project
from visure.primatives.REST.specification import get_specifications

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