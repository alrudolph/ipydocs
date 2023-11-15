from typing import List


class Example:
    def __init__(self, description: str, code: str, result: str):
        self._description = description
        self._code = code
        self._result = result

    @property
    def description_combined(self):
        return "".join(self._description)

    @property
    def code_combined(self):
        return "\n".join(self._code)

    @property
    def result_combined(self):
        return "".join(self._result)


def parse_examples(examples: List[str]) -> List[Example]:
    examples_result = []

    new_example = True

    description = []
    code = []
    result = []

    for line in examples:
        if line == "":
            new_example = True
            examples_result.append(Example(description, code, result))
            description = []
            code = []
            result = []
            continue

        if line.strip().startswith(">>> "):
            new_example = False
            code.append(line.replace(">>> ", ""))
        elif line.strip() == ">>>":
            new_example = False
            code.append("")
        elif new_example:
            description.append(line)
        else:
            result.append(line)

    if len(code) > 0:
        examples_result.append(Example(description, code, result))

    return examples_result
