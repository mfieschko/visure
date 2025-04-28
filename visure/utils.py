from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List
from typing import Any, Callable, Dict, List, Type

if TYPE_CHECKING:
    from visure.project import VisureProject
    from visure.visure import Visure

class ResponseObject:
    """
    Turns a dict into an object whose keys are attributes.
    You can register per-field parsers via @register_parser.
    """
    # Registry mapping field names → parser functions
    _parsers: Dict[str, Callable[[Any], Any]] = {}

    def __init__(self, data: Dict[str, Any], visure_client : Visure, visure_project : VisureProject, target = None):
        for key, raw in data.items():
            if key in self._parsers:
                # custom parser
                parsed = self._parsers[key](raw, visure_client, visure_project, target)
            else:
                # default behavior
                parsed = self._default_parse(raw)
            
            if target == None:
                target = self

            setattr(target, key, parsed)

    def _default_parse(self, value: Any) -> Any:
        """
        - dicts → recursively make ResponseObject
        - lists → parse each element
        - primitives → leave as is
        """
        if isinstance(value, dict):
            return ResponseObject(value, None, None)
        elif isinstance(value, list):
            return [self._default_parse(item) for item in value]
        else:
            return value

    @classmethod
    def register_parser(cls, field_name: str) -> Callable[[Callable[[Any], Any]], Callable[[Any], Any]]:
        """
        Decorator to register a custom parser for a given top‑level field.
        """
        def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
            cls._parsers[field_name] = func
            return func
        return decorator

    def __repr__(self):
        # pretty repr so you can inspect it easily
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"<{self.__class__.__name__} {attrs}>"


class AttributableList(list):
    def __init__(self, *args):
        super().__init__(*args)
        for arg in args:
            if hasattr(arg, "name"):
                setattr(self, arg.name, arg)
