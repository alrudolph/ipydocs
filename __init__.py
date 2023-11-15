import importlib
import inspect
from inspect import getmembers, isfunction
from typing import Callable, Optional, Sequence

import toml
from numpydoc.docscrape import FunctionDoc


class ExpandedFunctionDoc(FunctionDoc):
    sections = {
        "Signature": "",
        "Summary": [""],
        "Extended Summary": [],
        "Parameters": [],
        "Returns": [],
        "Yields": [],
        "Receives": [],
        "Raises": [],
        "Warns": [],
        "Other Parameters": [],
        "Attributes": [],
        "Methods": [],
        "See Also": [],
        "Notes": [],
        "Warnings": [],
        "References": "",
        "Examples": "",
        "index": {},
        "Ipydoc": [],
    }


class Example:
    def __init__(self, description: str, code: str, result: str):
        self.description = description
        self.code = code
        self.result = result


class FunctionDocumentation:
    def __init__(self, function: Callable):
        self._function = function
        self._doc = ExpandedFunctionDoc(function)
        self._config = toml.loads("\n".join(self._doc["Ipydoc"]))

    @property
    def name(self):
        return self._function.__name__

    @property
    def summary(self):
        return self._doc["Summary"]

    @property
    def extended_summary(self):
        return self._doc["Extended Summary"]

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
    def examples(self):
        examples = []

        new_example = True

        description = []
        code = []
        result = []

        for line in self._doc["Examples"]:
            if line == "":
                new_example = True
                examples.append(Example(description, code, result))
                description = []
                code = []
                result = []
                continue

            if line.startswith(">>> "):
                new_example = False
                code.append(line.replace(">>> ", ""))
            elif new_example:
                description.append(line)
            else:
                result.append(line)

        if len(code) > 0:
            examples.append(Example(description, code, result))

        return examples

    # TODO: deprecate:
    @property
    def doc_string(self):
        return self._function.__doc__

    @property
    def source(self):
        return inspect.getsource(self._function)

    @property
    def signature(self):
        return self.name + str(inspect.signature(self._function))


class Link:
    def __init__(self, text: str, url: str):
        self.text = text
        self.url = url

    def as_html(self):
        return f'<a href="{self.url}">{self.text}</a>'


class Section:
    def __init__(self, links: Sequence[Link], title: Optional[str] = None):
        self.links = links
        self.title = title

    def as_html(self):
        return (
            f'<h3 class="text-xl font-bold">{self.title}</h3>' if self.title else ""
        ) + "".join([link.as_html() for link in self.links])


def side_bar(title: str, sections: Sequence[Section]) -> str:
    sections_html = "".join([section.as_html() for section in sections])

    return f"""
        <aside >
            <div>
                <a href="https://www.github.com/alrudolph/ipydocs">
                    <h1 class="text-3xl">{title}</h1>
                </a>
                {sections_html}
            </div>
        </aside>
    """


def parameter_var_type(param):
    return f"""
        <div class="flex text-lg">
            <p class="italic">{param.name}</p><p class="pl-2 text-blue-400">{param.type}</p>
        </div>
        <p class="text-md pl-4">
            {"".join(param.desc)}
        </p>
        """


def parameters_section(function: FunctionDocumentation):
    items = "".join([parameter_var_type(param) for param in function.parameters])

    return f"""
        
        <div class="w-full py-4">
            <h5 class="text-lg font-bold">Parameters</h5>
            {items}
        </div>

        """


def returns_section(function: FunctionDocumentation):
    print(function.returns)
    items = "".join([parameter_var_type(param) for param in function.returns])

    return f"""
        
        <div class="w-full py-4">
            <h5 class="text-lg font-bold">Returns</h5>
            {items}
        </div>

        """


def example_section(example: Example):
    return f"""
        <div>
            <p class="py-2">{"".join(example.description)}</p>
            <div>
                <py-repl id="my-repl">{"".join(example.code)}</py-repl>
            </div>
            <pre class="w-full flex bg-gray-100 px-4">
                <code class="language-py table w-full">
>>> {"".join(example.result)}
                </code>
            </pre>
        </div>
    """


def examples_section(function: FunctionDocumentation):
    items = "".join([example_section(example) for example in function.examples])

    return f"""
        
        <div class="w-full py-4">
            <h5 class="text-lg font-bold">Examples</h5>
            {items}
        </div>

    """


def generate_html(functions: Sequence[FunctionDocumentation]):
    head = (
        "<title>Docs!</title>"
        + '<link href="https://unpkg.com/tailwindcss@^1.0/dist/tailwind.min.css" rel="stylesheet">'
        + """
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/default.min.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
            <script>hljs.highlightAll();</script>
            <style>
                .hljs {
                    background: #00000000 !important;
                }
                pre code.hljs {
                    padding: 0 !important;
                }
            </style>
        """
        + """<link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css" />
        <script defer src="https://pyscript.net/latest/pyscript.js"></script>"""
    )
    function = functions[0]
    body = functions[0].doc_string
    signature = functions[0].signature
    source = (
        functions[0].source  # .source.replace("\n", "<br />")
        # .replace("   ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    )

    return (
        f"<html>\n"
        + f"  <head>\n"
        + head
        + f"  </head>\n"
        + f'  <body class="flex justify-center">\n'
        # + "<code>"
        # + body
        # + "</code>"
        + '<main class="max-w-4xl w-full flex">'
        + side_bar(
            "Rcheck", [Section([Link("Basic Types", "/basic-types")], "Assertions")]
        )
        + f"""
            <div class="w-full py-2 px-8">
                <section>
                    <pre class="w-full flex">
                        <code class="language-py text-xl">
{signature}
                        </code>
                    </pre>
                    <p>
                        {"".join(function.summary)}
                    </p>
                    <p>
                        {"".join(function.extended_summary)}
                    </p>
                </section>
                <section>
                    {parameters_section(function)}
                    {returns_section(function)}
                    {examples_section(function)}
                </section>
                <section>
                    <h5 class="text-lg font-bold">Source Code</h5>
                    <pre class="w-full flex bg-gray-100 px-4">
                        <code class="language-py table w-full">
{source}
                        </code>
                    </pre>
                </section>
            </div>
        """
        + "</main>"
        # + """   <py-config>
        #             plugins = [
        #               "https://pyscript.net/latest/plugins/python/py_tutor.py"
        #             ]
        #         </py-config>
        #         <div style="margin-right: 3rem">
        #             <py-repl id="my-repl">1+2</py-repl>
        #         </div>
        # """
        + f"  </body>\n"
        f"</html>"
    )


def main(module_path: str):
    module = importlib.import_module(module_path)
    module_functions = getmembers(module, isfunction)

    my_func = FunctionDocumentation(module_functions[0][1])

    print(my_func.signature)
    print(my_func.returns)
    print(my_func._config)

    fd = ExpandedFunctionDoc(module_functions[0][1])

    html = generate_html([my_func])

    with open("./output.html", "w") as file:
        file.write(html)


if __name__ == "__main__":
    main("proj")
