import ollama


def zero_shot(prompt:str, model:str) -> str:
    response = ollama.generate(model=model, prompt=prompt)
    return response["response"]

def few_shot(prompt:str, model:str) -> str:
    response = ollama.generate(model=model, prompt=prompt)
    return response["response"]