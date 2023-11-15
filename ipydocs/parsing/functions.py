import inspect
from typing import Callable, List

import toml
from numpydoc.docscrape import FunctionDoc

from ipydocs.parsing.examples import Example, parse_examples


class ExpandedFunctionDoc(FunctionDoc):
    sections = {
        **FunctionDoc.sections,
        "Ipydoc": [],
    }


class FunctionDocumentation:
    def __init__(self, function: Callable):
        self._function = function
        self._doc = ExpandedFunctionDoc(function)
        self._config = toml.loads("\n".join(self._doc["Ipydoc"]))

    @property
    def name(self) -> str:
        return self._function.__name__

    @property
    def summary_combined(self):
        return "".join(self._doc["Summary"])

    @property
    def extended_summary_combined(self):
        return "".join(self._doc["Extended Summary"])

    @property
    def parameters(self):
        return self._doc["Parameters"]

    @property
    def returns(self):
        return self._doc["Returns"]

    @property
    def yields(self):
        return self._doc["Yields"]

    @property
    def receives(self):
        return self._doc["Receives"]

    @property
    def raises(self):
        return self._doc["Raises"]

    @property
    def warns(self):
        return self._doc["Warns"]

    @property
    def other_parameters(self):
        return self._doc["Other Parameters"]

    @property
    def attributes(self):
        return self._doc["Attributes"]

    @property
    def methods(self):
        return self._doc["Methods"]

    @property
    def see_also(self):
        return self._doc["See Also"]

    @property
    def notes(self):
        return self._doc["Notes"]

    @property
    def warnings(self):
        return self._doc["Warnings"]

    @property
    def references(self):
        return self._doc["References"]

    @property
    def examples(self) -> List[Example]:
        return parse_examples(self._doc["Examples"])

    @property
    def source(self) -> str:
        return inspect.getsource(self._function)

    @property
    def signature(self) -> str:
        return self.name + str(inspect.signature(self._function))
