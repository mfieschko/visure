from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from visure.visure import Visure
    from visure.project import VisureProject

class VisureObject(object):
    def __init__(self, visure_client : Visure, project : VisureProject, id=None):
        self._visure_client : Visure = visure_client
        self._project : VisureProject = project
        self.id = id

    def _reload(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError
