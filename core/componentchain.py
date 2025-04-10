from pydantic import BaseModel


class ComponentChain(BaseModel):
    def invoke(input, *funcs):
        for func in funcs:
            input = func.invoke(input)
        return input
