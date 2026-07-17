TOOLS = {}


def register(tool):
    TOOLS[tool.name] = tool


def get(name):
    return TOOLS.get(name)


def list_tools():
    return [
        {
            "name": tool.name,
            "description": tool.description,
        }
        for tool in TOOLS.values()
    ]
