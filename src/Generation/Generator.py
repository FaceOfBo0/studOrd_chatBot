from typing import Iterator
import ollama
import lmstudio as lms
from openai import OpenAI
from llama_cpp import Llama
from transformers import AutoTokenizer, AutoModelForCausalLM

def gen_response_oll(gen_model_name: str, query: str, context: list[str]) -> str:

        context_text = "\n".join(context)
        messages = [
            {
                "role": "system",
                "content": """Du bist ein hilfreicher KI-Assistent, der auf die Beantwortung von Fragen basierend auf bereitgestelltem Kontext spezialisiert ist.
                Befolge diese Regeln:
                1. Verwende ausschließlich Informationen aus dem bereitgestellten Kontext.
                2. Wenn du die Antwort im Kontext nicht findest, sage es direkt.
                3. Sei präzise und direkt in deinen Antworten.
                4. Wenn du aus dem Kontext zitierst, erwähne dies.
                5. Antworte in der gleichen Sprache wie die Frage gestellt wurde."""
            },
            {
                "role": "user",
                "content": f"""Hier ist der Kontext für die Beantwortung:

                {context_text}

                Beantworte auf Grundlage des Kontexts folgende Frage: {query}"""
            }
        ]

        response = ollama.chat(
            model=gen_model_name,
            messages=messages,
            options={
                "temperature": 0.6,
                "top_p": 0.95
            }
        )

        return response['message']['content'].strip()

def gen_response_oll_stream(gen_model_name: str, query: str, context: list[str]):
    """Streaming version of gen_response_oll that yields tokens as they're generated"""
    context_text = "\n".join(context)

    messages = [
        {
            "role": "system",
            "content": """Du bist ein hilfreicher KI-Assistent einer Universität, der darauf spezialisiert ist, die Fragen von Studierenden zu Ihrer Studienordnung auf Grundlage von bereitgestellten Abschnitten der Studienordnung zu Beantworten.
            Befolge diese Regeln:
            1. Verwende ausschließlich Informationen aus den bereitgestellten Abschnitten der Studienordnung.
            2. Wenn du die Antwort in den bereitgestellten Abschnitten nicht findest, sage es direkt.
            3. Sei präzise und direkt in deinen Antworten und benutze nur diejenigen Abschnitte, die relevant für die Beantwortung der Frage sind.
            4. Wenn du aus der Studienordnung zitierst, erwähne dies, indem du die den Paragraphen und gegebenenfalls Absatz und Punkt (falls vorhanden) am Ende deiner Antwort in Klammern angibst.
            5. Antworte in der gleichen Sprache, in der die Frage gestellt wurde."""
        },
        {
            "role": "user",
            "content": f"""Hier sind die Abschnitte für die Beantwortung:

            {context_text}

            Beantworte auf Grundlage der Abschnitte folgende Frage: {query}"""
        }
    ]

    stream = ollama.chat(
        model=gen_model_name,
        messages=messages,
        options={
            "temperature": 0.5,
            "top_p": 0.95
        },
        stream=True
    )

    for chunk in stream:
        if 'message' in chunk and 'content' in chunk['message']:
            yield chunk['message']['content']

def gen_response_lms_stream(model_name: str, query: str, context: list[str]):
    context_text = "\n".join(context)
    model = lms.llm(model_name)

    chat = lms.Chat("""Du bist ein hilfreicher KI-Assistent einer Universität, der darauf spezialisiert ist, die Fragen von Studierenden zu Ihrer Studienordnung auf Grundlage von bereitgestellten Abschnitten der Studienordnung zu Beantworten.

    Befolge diese Regeln:
    1. Verwende ausschließlich Informationen aus den bereitgestellten Abschnitten der Studienordnung.
    2. Wenn du die Antwort in den bereitgestellten Abschnitten nicht findest, sage es direkt.
    3. Sei präzise und direkt in deinen Antworten und benutze nur diejenigen Abschnitte, die relevant für die Beantwortung der Frage sind.
    4. Wenn du aus der Studienordnung zitierst, erwähne dies, indem du gegebenfalls den Abschnitt, Paragraph und Absatz kurz nennst.
    5. Antworte in der gleichen Sprache, in der die Frage gestellt wurde.""")

    chat.add_user_message(f"""Hier sind die Abschnitte der Studienordnung für die Beantwortung:

    {context_text}

    Beantworte auf Grundlage der vorliegenden Abschnitte der Studienordnung folgende Frage: {query}""")

    response_stream = model.respond_stream(chat, config={
        "temperature": 0.5,
        "topPSampling": 0.95
    })

    for fragment in response_stream:
        yield fragment.content

def gen_response_lcpp_stream(repoid: str, file_name: str, query: str, context: list[str]):
    context_text = "\n".join(context)

    model = Llama.from_pretrained(repo_id=repoid, filename=file_name, n_ctx=4096, chat_format="gemma", n_gpu_layers=-1)
    response_stream = model.create_chat_completion(
        messages= [
        {
            "role": "system",
            "content": """Du bist ein hilfreicher KI-Assistent einer Universität, der darauf spezialisiert ist, die Fragen von Studierenden zu Ihrer Studienordnung auf Grundlage von bereitgestellten Abschnitten der Studienordnung zu Beantworten.
            Befolge diese Regeln:
            1. Verwende ausschließlich Informationen aus den bereitgestellten Abschnitten der Studienordnung.
            2. Wenn du die Antwort in den bereitgestellten Abschnitten nicht findest, sage es direkt.
            3. Sei präzise und direkt in deinen Antworten und benutze nur diejenigen Abschnitte, die relevant für die Beantwortung der Frage sind.
            4. Wenn du aus der Studienordnung zitierst, erwähne dies, indem du die den Paragraphen und gegebenenfalls Absatz und Punkt (falls vorhanden) am Ende deiner Antwort in Klammern angibst.
            5. Antworte in der gleichen Sprache, in der die Frage gestellt wurde."""
        },
        {
            "role": "user",
            "content": f"""Hier sind die Abschnitte für die Beantwortung:

            {context_text}

            Beantworte auf Grundlage der Abschnitte folgende Frage: {query}"""
        }
    ],
    stream=True,
    temperature=0.5,
    top_p=0.95,
    )

    if isinstance(response_stream, Iterator):
        for chunk in response_stream:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]

def gen_response_or_stream(model_name: str, query: str, context: list[str]):
    client = OpenAI(base_url="https://openrouter.ai/api/v1",
        api_key="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")

    context_text = "\n".join(context)


    completion = client.chat.completions.create(model=model_name,
        messages=[
        {
            "role": "system",
            "content": """Du bist ein hilfreicher KI-Assistent einer Universität, der darauf spezialisiert ist, die Fragen von Studierenden zu Ihrer Studienordnung auf Grundlage von bereitgestellten Abschnitten der Studienordnung zu Beantworten.
            Befolge diese Regeln:
            1. Verwende ausschließlich Informationen aus den bereitgestellten Abschnitten der Studienordnung.
            2. Wenn du die Antwort in den bereitgestellten Abschnitten nicht findest, sage es direkt.
            3. Sei präzise und direkt in deinen Antworten und benutze nur diejenigen Abschnitte, die relevant für die Beantwortung der Frage sind.
            4. Wenn du aus der Studienordnung zitierst, erwähne dies, indem du die den Paragraphen und gegebenenfalls Absatz und Punkt (falls vorhanden) am Ende deiner Antwort in Klammern angibst.
            5. Antworte in der gleichen Sprache, in der die Frage gestellt wurde."""
        },
        {
            "role": "user",
            "content": f"""Hier sind die Abschnitte für die Beantwortung:

            {context_text}

            Beantworte auf Grundlage der Abschnitte folgende Frage: {query}"""
        }
    ], stream = True,
    temperature=0.5)

    for chunk in completion:
        yield chunk.choices[0].delta.content
