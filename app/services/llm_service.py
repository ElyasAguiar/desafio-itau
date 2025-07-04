from openai import AsyncOpenAI, OpenAIError
from app.core.config import settings


class OpenAIClient:
    """Cliente para interagir com a API da OpenAI usando a biblioteca oficial, com suporte async e tratamento de erros."""

    def __init__(
        self,
        api_key: str = settings.OPENAI_API_KEY,
        model: str = "gpt-4o-mini",
    ):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def get_chat_completions(self, message: str) -> dict:
        try:
            response = await self.client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": message}]
            )
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
            }
        except OpenAIError as e:
            return {
                "content": f"Erro ao conectar com a OpenAI: {str(e)}",
                "model": self.model,
            }
        except Exception as e:
            return {"content": f"Erro inesperado: {str(e)}", "model": self.model}
