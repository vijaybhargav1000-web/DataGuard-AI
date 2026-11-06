import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"


def ask_llm(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()
    return response.json()["response"]


if __name__ == "__main__":
    answer = ask_llm(
        "Explain why missing customer IDs affect transaction analytics."
    )
    print(answer)