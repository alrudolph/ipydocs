from typing import Any, Dict, Optional, Sequence, Tuple

from jinja2 import BaseLoader, Environment

from ipydocs.parsing.classes import ClassDocumentation
from ipydocs.parsing.functions import FunctionDocumentation


class Link:
    def __init__(self, text: str, url: str, anchor: str = ""):
        self.text = text
        self.url = url.lower()
        self.anchor = anchor

    def as_html(self):
        anchor = ""

        if self.anchor != "":
            anchor = f"#{self.anchor}"

        return f'<a href="/docs/{self.url}{anchor}">{self.text}</a>'


class ClassLink:
    def __init__(self, cls: ClassDocumentation, url: str):
        self.cls = cls
        self.url = url.lower()

    def as_html(self):
        output = f'<a href="/docs/{self.url}"><h4>{self.cls.name}</h4></a>'

        methods = [
            Link(method.name, self.url, method.name).as_html()
            for method in self.cls.methods
        ]

        li_cls = 'class="pl-2 italic"'

        joined_methods = f"</li><li {li_cls}>".join(methods)
        output += f"<ul><li {li_cls}>{joined_methods}</li></ul>"

        return output


class Section:
    def __init__(self, links: Sequence[Link], title: Optional[str] = None):
        self.links = links
        self.title = title


def examples_section(project_import_name: str, function: FunctionDocumentation):
    html = """
    <div class="py-4">
        <h5 class="text-lg font-bold">Examples</h5>
        <ol>
            {% for example in function.examples %}
            <li id="{{ function_name}}-example-{{ loop.index }}">
                <div>
                    <p class="py-2">{{ example.description_combined }}</p>
                    <div>
                        <!-- <py-repl output="pandas-output-inner"> -->
                        <py-repl style="width: 100%; display: inline-block !important; ">
from {{ project_import_name }} import *

{{ example.code_combined }}
                        </py-repl>
                    </div>

                    <pre class="w-full flex bg-gray-100 px-4">
                        <code class="language-py table w-full whitespace-pre-wrap">
>>> {{ example.result_combined }}
                        </code>
                        <!-- <code class="language-py table w-full whitespace-pre-wrap" id="pandas-output-inner"></code> -->
                    </pre>
                </div>
            </li>
            {% endfor %}
        </ol>
    </div>
    """

    rtemplate = Environment(loader=BaseLoader).from_string(html)
    return rtemplate.render(
        function=function,
        project_import_name=project_import_name,
        function_name=function.name,
    )


def function_sub_section(project_import_name: str, function: FunctionDocumentation):
    html = """
        {% macro parameter_var_type(param) %}
            <div class="flex text-lg">
                <p>{{ param.name }}</p>
                <p class="{{ "pl-2" if param.name|length > 0 else "" }}italic">
                    {{ param.type }}
                </p>
            </div>
            <p class="text-md pl-4">
                {{ param.desc|join("") }}
            </p>
        {% endmacro %}

        <section>
            <pre class="w-full flex">
                <code class="language-py text-xl code-wrap">
{{ function.signature }}
                </code>
            </pre>
            <p>{{ function.summary_combined }}</p>
            <p>{{ function.extended_summary_combined }}</p>
        </section>
        <section>
            <!-- parameters_section -->
            <div class="w-full py-4">
                <h5 class="text-lg font-bold">Parameters</h5>
                <ol>
                    {% for param in function.parameters %}
                    <li>
                        {{ parameter_var_type(param) }}
                    </li>               
                    {% endfor %}
                </ol>
            </div>

            <!-- returns -->
            <div class="w-full py-4">
                <h5 class="text-lg font-bold">Returns</h5>
                <ol>
                    {% for param in function.returns %}
                    <li>
                        {{ parameter_var_type(param) }}
                    </li>               
                    {% endfor %}
                </ol>
            </div>
            
            <!-- raises section -->
            <div class="w-full py-4">
                <h5 class="text-lg font-bold">Raises</h5>
                <ol>
                    {% for param in function.raises %}
                    <li>
                        {{ parameter_var_type(param) }}
                    </li>               
                    {% endfor %}
                </ol>
            </div>

            <!-- examples section -->
            {{ examples_section }}
        </section>
        """

    rtemplate = Environment(loader=BaseLoader).from_string(html)
    return rtemplate.render(
        function=function,
        project_import_name=project_import_name,
        examples_section=examples_section(project_import_name, function),
    )


def function_section(project_import_name: str, function: FunctionDocumentation):
    html = """
        {{ sub_section }}
        <section>
            <h5 class="text-lg font-bold">Source Code</h5>
            <pre class="w-full flex bg-gray-100 px-4">
                <code class="language-py table w-full">
{{ function.source }}
                </code>
            </pre>
        </section>
        """

    rtemplate = Environment(loader=BaseLoader).from_string(html)
    return rtemplate.render(
        function=function,
        project_import_name=project_import_name,
        sub_section=function_sub_section(project_import_name, function),
    )


def class_section(project_import_name: str, cls: ClassDocumentation):
    html = """
        <h2 class="text-4xl">{{cls_name}}</h2>

        {{ cls_summary }}

        {{ examples_section }}

        <h3 class="text-3xl font-bold">Methods</h3>
        <ul>
            {% for func in cls.methods %}
            <li class="my-2" id="{{ func.name }}">
                <h4 class="text-2xl font-bold">
                    {{func.name}}
                </h4>
                {{ function_sub_section(project_import_name, func) }}
            </li>
            {% endfor %}
        </ul>
        <section class="">
            <h5 class="text-3xl font-bold">Source Code</h5>
            <pre class="w-full flex bg-gray-100 whitespace-pre-wrap px-2">
                <code class="language-py table w-full">
{{cls_source}}
                </code>
            </pre>
        </section>
        """

    rtemplate = Environment(loader=BaseLoader).from_string(html)
    return rtemplate.render(
        cls=cls,
        cls_name=cls.name,
        cls_source=cls.source,
        cls_summary=cls.summary_combined,
        project_import_name=project_import_name,
        function_sub_section=function_sub_section,
        examples_section=examples_section(project_import_name, cls),
    )


def generate_html(
    project_import_name: str,
    classes: Sequence[ClassDocumentation],
    functions: Sequence[FunctionDocumentation],
    whl_location: str,
    config: Dict[str, Any],
    select: Tuple[str, int],
):
    side_bar_sections = [Section([Link("About", "")], "General")]

    if len(classes) > 0:
        side_bar_sections.append(
            Section(
                [ClassLink(cls, cls.name + ".html") for cls in classes],
                "Classes",
            )
        )

    if len(functions) > 0:
        side_bar_sections.append(
            Section(
                [Link(func.name, func.name + ".html") for func in functions],
                "Functions",
            )
        )

    if select[0] == "function":
        content = function_section(project_import_name, functions[select[1]])
    elif select[0] == "class":
        content = class_section(project_import_name, classes[select[1]])
    elif select[0] == "page":
        with open(config["layout"][select[1]]["path"], "r") as file:
            content = file.read()
    else:
        raise Exception()
    
    print("whl loc:", whl_location)

    html = """
    <html>
        <head>
            <title>{{ title }}</title>

            <!-- Tailwind -->
            <link href="https://unpkg.com/tailwindcss@^1.0/dist/tailwind.min.css" rel="stylesheet">

            <!-- Highlightjs -->
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
                pre code.code-wrap {
                    white-space: pre-wrap;
                }
                .cm-content {}
            </style>
            
            <!-- Pyscript -->
            <link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css" />
            <script defer src="https://pyscript.net/latest/pyscript.js"></script>
        </head>
        <body class="flex flex-col items-center">
            <py-config>
                name = "Freedom Units"
                description = "A testing app"
                version = "0.0.1"
                terminal = false

                packages = [
                    "{{ whl_location }}",
                ]
            </py-config>
            <main class="max-w-6xl w-full">
                <!-- sidebar -->
                <div class="flex w-full">
                    <div>
                        <aside class="sticky top-0 h-min">
                            <a href="https://www.github.com/alrudolph/ipydocs">
                                <h1 class="text-3xl">{{ project_import_name }}</h1>
                            </a>
                            <ol>
                                {% for section in side_bar_sections %}
                                <li>    
                                    <h3 class="text-xl font-bold">{{ section.title }}</h3>
                                    <ol>
                                        {% for link in section.links %}
                                        <li>
                                            {{ link.as_html() }}
                                        </li>
                                        {% endfor %}
                                    </ol>
                                </li>   
                                {% endfor %}
                            </ol>
                        </aside>
                    </div>

                    <!-- main content -->
                    <div class="w-full py-2 px-8">
                        {{ content }}
                        <a class="py-8 text-gray-500 flex justify-end" href="https://www.github.com/alrudolph/ipydocs">
                            Created with ipydocs
                        </a>
                    </div>
                </div>
            </main>
            <script defer>
                // const sheet = new CSSStyleSheet;
                // sheet.replaceSync( `.cm-content { white-space: pre-wrap }`);
                // host.shadowRoot.adoptedStyleSheets.push(sheet);
                setTimeout(() => {
                    const repls = document.querySelectorAll("py-repl div div div");
                                        
                    const sheet = new CSSStyleSheet();
                    sheet.replaceSync(`.cm-content { white-space: pre-wrap }`);

                    repls.forEach((repl, i) => {
                        repls[i].shadowRoot.querySelector('div[role=textbox]').style = "white-space: pre-wrap !important;";
                        repls[i].shadowRoot.querySelector('div[role=textbox] .cm-line').style = "width: 100%; overflow-x: hidden;";
                    });
                }, 5000);
            </script>
        </body>
    </html>
    """

    rtemplate = Environment(loader=BaseLoader).from_string(html)
    return rtemplate.render(
        title=f"{project_import_name} documentation",
        whl_location=whl_location,
        side_bar_sections=side_bar_sections,
        project_import_name=project_import_name,
        content=content,
    )
