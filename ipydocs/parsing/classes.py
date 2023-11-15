import inspect
from typing import Callable, List

from numpydoc.docscrape import ClassDoc

from ipydocs.parsing.examples import Example, parse_examples
from ipydocs.parsing.functions import FunctionDocumentation


class ClassDocumentation:
    def __init__(self, cls: Callable):
        self._cls = cls
        self._doc = ClassDoc(cls)

        method_names = [
            func
            for func in dir(cls)
            if callable(getattr(cls, func)) and not func.startswith("_")
        ]

        self._methods = [
            FunctionDocumentation(getattr(cls, method_name))
            for method_name in method_names
        ]

    @property
    def name(self) -> str:
        return self._cls.__name__

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
        return self._methods

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
        return inspect.getsource(self._cls)

    @property
    def signature(self) -> str:
        return self.name + str(inspect.signature(self._cls))
