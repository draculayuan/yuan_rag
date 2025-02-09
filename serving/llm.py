import vertexai
from vertexai.language_models import ChatModel, TextGenerationModel
from typing import List, Dict, Any, Optional

class LLMHandler:
    def __init__(
        self,
        project_id: str,
        location: str,
        model_name: str = "gemini-1.0-pro",
        temperature: float = 0.7,
        max_output_tokens: int = 1024,
    ):
        vertexai.init(project=project_id, location=location)
        self.chat_model = ChatModel.from_pretrained(model_name)
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    def generate_prompt(self, query: str, context: List[str]) -> str:
        """Generate RAG prompt with context."""
        context_str = "\n\n".join(context)
        
        prompt = f"""You are a helpful AI assistant. Use the following context to answer the question. 
If you cannot find the answer in the context, say so - do not make up information.

Context:
{context_str}

Question: {query}

Answer:"""
        
        return prompt

    def generate_response(
        self,
        query: str,
        context: List[str],
        safety_settings: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate response using the LLM."""
        prompt = self.generate_prompt(query, context)
        
        chat = self.chat_model.start_chat(
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            safety_settings=safety_settings,
        )
        
        response = chat.send_message(prompt)
        return response.text

    def get_default_safety_settings(self) -> List[Dict[str, Any]]:
        """Get default safety settings for the model."""
        return [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ] 