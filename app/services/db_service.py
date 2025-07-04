import motor.motor_asyncio
from loguru import logger
from pymongo.errors import PyMongoError
from app.core.config import settings


class MongoDBService:
    """Serviço para interagir com o MongoDB."""

    def __init__(self, mongo_url: str = None):
        """Inicializa a conexão com o MongoDB."""
        self.mongo_url = mongo_url or settings.MONGODB_URL
        self.client = None
        self.db = None

    async def connect(self):
        """Conecta ao MongoDB."""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_url)
            self.db = self.client.chat_db
            logger.info("Conectado ao MongoDB com sucesso!")
            return True
        except PyMongoError as e:
            logger.error(f"Erro ao conectar ao MongoDB: {str(e)}")
            return False

    async def disconnect(self):
        """Desconecta do MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Desconectado do MongoDB")

    async def save_chat_interaction(self, chat_data: dict) -> bool:
        """
        Salva uma interação de chat no MongoDB.

        Args:
            chat_data (dict): Dados do chat a serem salvos

        Returns:
            bool: True se o salvamento foi bem-sucedido, False caso contrário
        """
        try:
            if not self.db:
                await self.connect()

            await self.db.chat_interactions.insert_one(chat_data)
            logger.info(f"Chat salvo com sucesso: {chat_data.get('id')}")
            return True
        except PyMongoError as e:
            logger.error(f"Erro ao salvar o chat no MongoDB: {str(e)}")
            return False

    async def get_chat_by_id(self, chat_id: str) -> dict:
        """Recupera um chat pelo ID."""
        try:
            if not self.db:
                await self.connect()

            chat = await self.db.chat_interactions.find_one({"id": chat_id})
            return chat
        except PyMongoError as e:
            logger.error(f"Erro ao recuperar o chat: {str(e)}")
            return None

    async def get_chats_by_user(self, user_id: str) -> list:
        """Recupera os chats de um usuário específico."""
        try:
            if not self.db:
                await self.connect()

            cursor = self.db.chat_interactions.find({"userId": user_id})
            chats = await cursor.to_list(length=100)  # Limitar a 100 resultados
            return chats
        except PyMongoError as e:
            logger.error(f"Erro ao recuperar os chats do usuário: {str(e)}")
            return []
