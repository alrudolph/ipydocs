import importlib
from inspect import getmembers, isclass, isfunction
from pathlib import Path
from typing import Union

import yaml

from ipydocs.components import generate_html
from ipydocs.parsing.classes import ClassDocumentation
from ipydocs.parsing.functions import FunctionDocumentation


def generate_docs(module_name: str):
    with open("./ipydocs.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
        whl_location = config["project_location"]

    module = importlib.import_module(module_name)
    module_functions = getmembers(module, isfunction)

    funcs = [FunctionDocumentation(func[1]) for func in module_functions]
    classes = [ClassDocumentation(o) for o in module.__dict__.values() if isclass(o)]

    output_dir = Path("docs")
    output_dir.mkdir(exist_ok=True)

    def gen_html(page_type: str, index: Union[str, int]) -> str:
        return generate_html(
            config["title"],
            classes,
            funcs,
            whl_location,
            config,
            (page_type, index),
        )

    with open(output_dir / "index.html", "w") as file:
        file.write(gen_html("page", "home"))

    for i, class_ in enumerate(classes):
        output_path = output_dir / (class_.name.lower() + ".html")
        with open(output_path, "w") as file:
            file.write(gen_html("class", i))

    for i, func in enumerate(funcs):
        output_path = output_dir / (func.name.lower() + ".html")
        with open(output_path, "w") as file:
            file.write(gen_html("function", i))
