import os
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForQuestionAnswering, BitsAndBytesConfig
import torch


class Generator:

    def gen_resp_pipeline(self, model_name: str, query: str, context: list[str]) -> str:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        quantization_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0,
        llm_int8_has_fp16_weight=True,
    )
        model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

        context_text = " ".join(context)
        prompt = f"""
        Kontext:
        {context_text}

        Frage: {query}
        """
        
        messages = [
            {"role": "system", "content": """
             Du bist ein hilfreicher Assistent. Beantworte die Frage basierend auf dem gegebenen Kontext 
             undzwar indem du zuerst den relevanten Paragraphen für die Beantwortung der Frage nennst und 
             dann die Antwort auf die Frage gibst. Falls die Antwort nicht im Kontext zu finden ist, sage
             'Basierend auf dem Kontext kann ich diese Frage nicht beantworten.'
             """},
            {"role": "user", "content": prompt}
        ]

        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            )

        model_inputs = tokenizer([prompt], return_tensors="pt").to(model.device)

        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return response
    

    """def gen_resp_janus_pro(self, query: str, context: list[str]) -> str:
        model_path = "deepseek-ai/Janus-Pro-1B"
        vl_chat_processor: VLChatProcessor = VLChatProcessor.from_pretrained(model_path)
        tokenizer = vl_chat_processor.tokenizer

        vl_gpt: MultiModalityCausalLM = AutoModelForCausalLM.from_pretrained(
            model_path, trust_remote_code=True, device_map="auto",
        )
        vl_gpt = vl_gpt.to(torch.bfloat16)

        context_text = " ".join(context)

        conversation = [
            {
                "role": "<|User|>",
                "content": prompt,
            },
            {"role": "<|System|>", "content": "Du bist ein hilfreicher Assistent. Beantworte die Frage basierend auf dem gegebenen Kontext, aber halte dich dabei so kurz wie möglich. Falls die Antwort nicht im Kontext zu finden ist, sage 'Basierend auf dem Kontext kann ich diese Frage nicht beantworten.'"},
        ]

        prepare_inputs = vl_chat_processor(
            conversations=conversation, force_batchify=True
        ).to(vl_gpt.device)

        inputs_embeds = vl_gpt.prepare_inputs_embeds(**prepare_inputs)

        outputs = vl_gpt.language_model.generate(
            inputs_embeds=inputs_embeds,
            max_new_tokens=256,
        )

        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return answer
        """

    def _parse_deepseek_response(self, response: str) -> str:
        # Try to find the solution between specific markers
        if "<|begin_of_solution|>" in response and "<|end_of_solution|>" in response:
            solution = response.split("<|begin_of_solution|>")[1].split("<|end_of_solution|>")[0]
            return solution.strip()
    
        # If no markers found, return everything after the last newline
        # (as deepseek often puts the final answer there)
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        if lines:
            return lines[-1]
    
        return response.strip()

    def gen_resp_deepseek(self, query: str, context: list[str]) -> str:
        model_name = "prithivMLmods/QwQ-R1-Distill-1.5B-CoT"

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        #if torch.cuda.is_available():
        #    self.model = self.model.to('cuda')

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        context_text = " ".join(context)
        prompt = f"""
        context:
        {context_text}

        question: {query}

        """

        messages = [
            {"role": "system", "content": "You are a helpful and harmless assistant that should help students with their questions. Please answer the question with regard to the given context and translate your solution into german."},
            {"role": "user", "content": prompt}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return self._parse_deepseek_response(response)




    def gen_resp_tinyLama(self, query: str, context: list[str]) -> str:
        self.tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        self.model = AutoModelForCausalLM.from_pretrained(
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            torch_dtype="auto",  # Use float16 for efficiency
        )
        if torch.cuda.is_available():
            self.model = self.model.to('cuda')

        # Combine context passages into a single string
        context_text = " ".join(context)
        
        # Create prompt template optimized for TinyLlama
        prompt = f"""<|system|>
        Du bist ein hilfreicher Assistent. Beantworte die Frage basierend auf dem gegebenen Kontext, aber halte dich dabei so kurz wie möglich. Falls die Antwort nicht im Kontext zu finden ist, sage "Basierend auf dem Kontext kann ich diese Frage nicht beantworten."

        <|user|>
        Kontext:
        {context_text}

        Frage: {query}

        <|assistant|>"""

        # Tokenize and generate
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=512,  # Reduced from 512 for faster generation
            temperature=0.7,
            top_p=0.95,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the model's response (after the prompt)
        response = response.split("<|assistant|>")[-1].strip()
        
        return response
    
class Generator_v2:
    def __init__(self, model_name="distilbert/distilbert-base-uncased-distilled-squad"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        if torch.cuda.is_available():
            self.model = self.model.to('cuda')

    def generate_response(self, query: str, contexts: list[str]) -> str:
        # Combine all contexts into one text
        context = " ".join(contexts)

        # Encode the input
        inputs = self.tokenizer(
            query,
            context,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True
        )

        # Move inputs to GPU if available
        if torch.cuda.is_available():
            inputs = {k: v.to('cuda') for k, v in inputs.items()}

        # Get model outputs
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Get the most likely answer span
        answer_start = torch.argmax(outputs.start_logits)
        answer_end = torch.argmax(outputs.end_logits)

        # Convert token positions to string indices
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        answer = tokens[answer_start:answer_end + 1]
        
        # Convert answer tokens to string, removing special tokens
        answer = self.tokenizer.convert_tokens_to_string(answer)

        # If no good answer is found, return a default message
        if not answer or answer.isspace() or answer == "[CLS]" or answer == "[SEP]":
            return "Basierend auf dem Kontext kann ich diese Frage nicht beantworten."

        return answer