from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
import logging
from ..database import db_manager
from ..models import MessageCreate, MessageResponse, ToneAnalysisResponse, UserStatsResponse
from .tone_analyzer import tone_analyzer

logger = logging.getLogger(__name__)

class MessageService:
    def __init__(self):
        self.collection_name = "messages"
    
    def _get_collection(self):
        return db_manager.get_collection(self.collection_name)
    
    async def create_message(self, message_data: MessageCreate) -> MessageResponse:
        """Create a new message with tone analysis"""
        try:
            # Analyze tone
            tone_analysis = await tone_analyzer.analyze_tone(message_data.text)
            
            # Prepare message document
            message_doc = {
                "text": message_data.text,
                "user_id": message_data.user_id,
                "context": message_data.context,
                "tone_analysis": tone_analysis.dict(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert into database
            collection = self._get_collection()
            result = collection.insert_one(message_doc)
            
            # Create response
            message_response = MessageResponse(
                id=str(result.inserted_id),
                text=message_data.text,
                user_id=message_data.user_id,
                tone_analysis=tone_analysis,
                created_at=message_doc["created_at"],
                updated_at=message_doc["updated_at"]
            )
            
            logger.info(f"Message created successfully: {result.inserted_id}")
            return message_response
            
        except Exception as e:
            logger.error(f"Failed to create message: {e}")
            raise
    
    async def get_message(self, message_id: str) -> Optional[MessageResponse]:
        """Get a message by ID"""
        try:
            collection = self._get_collection()
            message_doc = collection.find_one({"_id": ObjectId(message_id)})
            
            if not message_doc:
                return None
            
            return MessageResponse(
                id=str(message_doc["_id"]),
                text=message_doc["text"],
                user_id=message_doc["user_id"],
                tone_analysis=ToneAnalysisResponse(**message_doc["tone_analysis"]),
                created_at=message_doc["created_at"],
                updated_at=message_doc["updated_at"]
            )
            
        except Exception as e:
            logger.error(f"Failed to get message: {e}")
            raise
    
    async def get_user_messages(self, user_id: str, limit: int = 50, skip: int = 0) -> List[MessageResponse]:
        """Get messages for a specific user"""
        try:
            collection = self._get_collection()
            cursor = collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).skip(skip).limit(limit)
            
            messages = []
            for message_doc in cursor:
                message = MessageResponse(
                    id=str(message_doc["_id"]),
                    text=message_doc["text"],
                    user_id=message_doc["user_id"],
                    tone_analysis=ToneAnalysisResponse(**message_doc["tone_analysis"]),
                    created_at=message_doc["created_at"],
                    updated_at=message_doc["updated_at"]
                )
                messages.append(message)
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get user messages: {e}")
            raise
    
    async def get_messages_by_tone(self, tone: str, limit: int = 50) -> List[MessageResponse]:
        """Get messages filtered by tone"""
        try:
            collection = self._get_collection()
            cursor = collection.find(
                {"tone_analysis.detected_tone": tone}
            ).sort("created_at", -1).limit(limit)
            
            messages = []
            for message_doc in cursor:
                message = MessageResponse(
                    id=str(message_doc["_id"]),
                    text=message_doc["text"],
                    user_id=message_doc["user_id"],
                    tone_analysis=ToneAnalysisResponse(**message_doc["tone_analysis"]),
                    created_at=message_doc["created_at"],
                    updated_at=message_doc["updated_at"]
                )
                messages.append(message)
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get messages by tone: {e}")
            raise
    
    async def get_user_stats(self, user_id: str) -> UserStatsResponse:
        """Get statistics for a user"""
        try:
            collection = self._get_collection()
            
            # Total messages
            total_messages = collection.count_documents({"user_id": user_id})
            
            # Messages this week
            week_ago = datetime.utcnow() - timedelta(days=7)
            messages_this_week = collection.count_documents({
                "user_id": user_id,
                "created_at": {"$gte": week_ago}
            })
            
            # Most common tone
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$tone_analysis.detected_tone",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 1}
            ]
            
            tone_result = list(collection.aggregate(pipeline))
            most_common_tone = tone_result[0]["_id"] if tone_result else None
            
            # Average confidence
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": None,
                    "avg_confidence": {"$avg": "$tone_analysis.confidence_score"}
                }}
            ]
            
            confidence_result = list(collection.aggregate(pipeline))
            average_confidence = confidence_result[0]["avg_confidence"] if confidence_result else 0.0
            
            # Favorite suggestions (most used)
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$unwind": "$tone_analysis.suggestions"},
                {"$group": {
                    "_id": "$tone_analysis.suggestions",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            
            suggestions_result = list(collection.aggregate(pipeline))
            favorite_suggestions = [item["_id"] for item in suggestions_result]
            
            return UserStatsResponse(
                total_messages=total_messages,
                most_common_tone=most_common_tone,
                average_confidence=average_confidence,
                messages_this_week=messages_this_week,
                favorite_suggestions=favorite_suggestions
            )
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            raise
    
    async def delete_message(self, message_id: str, user_id: str) -> bool:
        """Delete a message (only by the owner)"""
        try:
            collection = self._get_collection()
            result = collection.delete_one({
                "_id": ObjectId(message_id),
                "user_id": user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            raise
    
    async def search_messages(self, user_id: str, query: str, limit: int = 20) -> List[MessageResponse]:
        """Search messages by text content"""
        try:
            collection = self._get_collection()
            cursor = collection.find({
                "user_id": user_id,
                "text": {"$regex": query, "$options": "i"}
            }).sort("created_at", -1).limit(limit)
            
            messages = []
            for message_doc in cursor:
                message = MessageResponse(
                    id=str(message_doc["_id"]),
                    text=message_doc["text"],
                    user_id=message_doc["user_id"],
                    tone_analysis=ToneAnalysisResponse(**message_doc["tone_analysis"]),
                    created_at=message_doc["created_at"],
                    updated_at=message_doc["updated_at"]
                )
                messages.append(message)
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to search messages: {e}")
            raise

# Global message service instance
message_service = MessageService()
