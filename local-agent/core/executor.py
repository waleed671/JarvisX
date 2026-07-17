from core.registry import get


class Executor:

    def execute(self, action):
        tool_name = action.get("tool")
        tool = get(tool_name)

        if tool is None:
            return {
                "success": False,
                "message": f"Tool '{tool_name}' not found",
                "tool": tool_name,
            }

        try:
            result = tool.execute(action.get("parameters", {}))
        except Exception as exc:
            return {
                "success": False,
                "message": str(exc),
                "tool": tool_name,
            }

        if isinstance(result, tuple):
            success, message = result
            return {
                "success": success,
                "message": message,
                "tool": tool_name,
            }

        result.setdefault("tool", tool_name)
        return result
