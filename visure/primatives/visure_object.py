class VisureObject(object):
    def __init__(self, visure_client, project, id=None):
        self._visure_client = visure_client
        self._project = project
        self._id = id

    def _reload(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError
