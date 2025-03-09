import ollama

class Generator:

    def gen_response_oll(self, gen_model_name: str, query: str, context: list[str]) -> str:

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
                "temperature": 0.7,
                "top_p": 0.95
            }
        )

        return response['message']['content'].strip()

    def gen_response_oll_stream(self, gen_model_name: str, query: str, context: list[str]):
        """Streaming version of gen_response_oll that yields tokens as they're generated"""
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

        stream = ollama.chat(
            model=gen_model_name,
            messages=messages,
            options={
                "temperature": 0.7,
                "top_p": 0.95
            },
            stream=True  # Enable streaming
        )

        for chunk in stream:
            if 'message' in chunk and 'content' in chunk['message']:
                yield chunk['message']['content']