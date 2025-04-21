from __future__ import annotations
import atexit
from pprint import pprint
from visure.primatives.REST.auth import authenticate, logout
from visure.primatives.REST.project import get_project_info, get_projects
from visure.project import VisureProject

class Visure:
    def __init__(self, url, username, password, auto_close_sessions = True):
        self._url = url
        self._authoring_url = f'{url}/visureauthoring8/api/v1'
        self._username = username
        self._password = password

        self._current_project_id = None # Used to facilitate interacting with the correct project
        self._authenticated = False
        self.projects : list[VisureProject] = None

        if auto_close_sessions:
            atexit.register(self.logout) # To prevent sessions from being "stuck open" when the program closes without a logout
        raw_project_data = self._authenticate_client()
        self._process_project_info(raw_project_data)

    def _authenticate_client(self):
        authentication_result = authenticate(self._authoring_url, self._username, self._password)
        access_token = authentication_result.get('accessToken')
        
        if access_token == None:
            self._authenticated = False
            raise Exception(f"Could not retrieve access token from {self._authoring_url}")
        
        self._access_token = access_token['token']
        self._refresh_token = access_token['refreshToken']

        self.email = authentication_result.get("email")
        self.firstName = authentication_result.get("firstName")
        self.lastName = authentication_result.get("lastName")
        self.id = authentication_result.get("id")
        self.username = authentication_result.get("username")

        self._authenticated = True

        return authentication_result.get("projects")

    def _process_project_info(self, project_data):
        self.projects = []
        for project in project_data:
            project_inst = VisureProject.fromData(self, **project)
            # project_inst._reload()
            self.projects.append(project_inst)
        return self.projects

    def logout(self):
        if self._authenticated:
            logout(self._authoring_url, self._access_token)
            self._authenticated = False

    def get_projects(self, deep = False) -> list:
        self.projects = []
        for project in get_projects(self._authoring_url, self._access_token):
            project_inst = VisureProject.fromData(self, **project)
            if deep:
                project_inst.refreshDetails()
            self.projects.append(project_inst)
        return self.projects