from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional
from .config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        
    async def connect(self):
        """Connect to MongoDB database"""
        try:
            self.client = MongoClient(settings.MONGODB_URI)
            self.database = self.client[settings.MONGODB_DATABASE]
            
            # Test the connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Create indexes for better performance
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB database"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Messages collection indexes
            messages_collection = self.database.messages
            messages_collection.create_index("user_id")
            messages_collection.create_index("timestamp")
            messages_collection.create_index("tone")
            
            # Users collection indexes
            users_collection = self.database.users
            users_collection.create_index("email", unique=True)
            users_collection.create_index("username", unique=True)
            
            # Feedback collection indexes
            feedback_collection = self.database.feedback
            feedback_collection.create_index("message_id")
            feedback_collection.create_index("user_id")
            feedback_collection.create_index("timestamp")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a MongoDB collection"""
        if not self.database:
            raise Exception("Database not connected")
        return self.database[collection_name]

# Global database manager instance
db_manager = DatabaseManager()
