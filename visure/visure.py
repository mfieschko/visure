"""
visure.visure
=============

This module defines the Visure class for authenticating with and interacting
with the Visure ALM system via its REST API.
"""

from __future__ import annotations
import atexit
from pprint import pprint
from visure.primatives.REST.auth import authenticate, logout
from visure.primatives.REST.project import get_project_info, get_projects
from visure.project import VisureProject


class Visure:
    """
    Main client class for interacting with the Visure ALM REST API.

    Handles authentication, session token management, and provides access
    to VisureProject instances for working with Visure ALM projects.
    """

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        auto_close_sessions: bool = True
    ):
        """
        Initialize and authenticate a Visure client.

        :param url: Base URL of the Visure ALM server (e.g. "https://visure.example.com").
        :param username: Username for Visure ALM authentication.
        :param password: Password for Visure ALM authentication.
        :param auto_close_sessions: If True, register an atexit hook to logout when the Python
                                    process exits, preventing dangling sessions.
        """
        self._url = url
        self._authoring_url = f'{url}/visureauthoring8/api/v1'
        self._username = username
        self._password = password

        self._current_project_id: int | None = None
        self._authenticated: bool = False
        self.projects: list[VisureProject] | None = None

        if auto_close_sessions:
            atexit.register(self.logout)
        raw_project_data = self._authenticate_client()
        self._process_project_info(raw_project_data)

    def _authenticate_client(self) -> list[dict]:
        """
        Perform authentication against the Visure ALM server and retrieve project metadata.

        :returns: A list of project metadata dictionaries from the server.
        :raises Exception: If the server does not return a valid access token.
        """
        authentication_result = authenticate(
            self._authoring_url, self._username, self._password
        )
        access_token = authentication_result.get('accessToken')
        if access_token is None:
            self._authenticated = False
            raise Exception(
                f"Could not retrieve access token from {self._authoring_url}"
            )

        self._access_token = access_token['token']
        self._refresh_token = access_token['refreshToken']
        self.email = authentication_result.get("email")
        self.firstName = authentication_result.get("firstName")
        self.lastName = authentication_result.get("lastName")
        self.id = authentication_result.get("id")
        self.username = authentication_result.get("username")

        self._authenticated = True
        return authentication_result.get("projects", [])

    def _process_project_info(self, project_data: list[dict]) -> list[VisureProject]:
        """
        Instantiate VisureProject objects from the raw project metadata.

        :param project_data: List of project metadata dictionaries.
        :returns: List of VisureProject instances representing each project.
        """
        self.projects = []
        for project in project_data:
            project_inst = VisureProject.fromData(self, **project)
            self.projects.append(project_inst)
        return self.projects

    def logout(self) -> None:
        """
        Invalidate the current session by calling the logout endpoint.

        Will only perform logout if the client is currently authenticated.
        """
        if self._authenticated:
            logout(self._authoring_url, self._access_token)
            self._authenticated = False

    def get_projects(self, deep: bool = False) -> list[VisureProject]:
        """
        Fetch and return the list of projects accessible by the authenticated user.

        :param deep: If True, refresh detailed project information for each project.
        :returns: List of VisureProject instances.
        """
        self.projects = []
        for project in get_projects(self._authoring_url, self._access_token):
            project_inst = VisureProject.fromData(self, **project)
            if deep:
                project_inst.refreshDetails()
            self.projects.append(project_inst)
        return self.projects
