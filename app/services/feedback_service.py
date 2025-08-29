from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import logging
from ..database import db_manager
from ..models import FeedbackCreate, FeedbackResponse

logger = logging.getLogger(__name__)

class FeedbackService:
    def __init__(self):
        self.collection_name = "feedback"
    
    def _get_collection(self):
        return db_manager.get_collection(self.collection_name)
    
    async def create_feedback(self, feedback_data: FeedbackCreate) -> FeedbackResponse:
        """Create new feedback"""
        try:
            # Prepare feedback document
            feedback_doc = {
                "message_id": feedback_data.message_id,
                "user_id": feedback_data.user_id,
                "tone_accuracy": feedback_data.tone_accuracy,
                "suggestion_helpfulness": feedback_data.suggestion_helpfulness,
                "comments": feedback_data.comments,
                "created_at": datetime.utcnow()
            }
            
            # Insert into database
            collection = self._get_collection()
            result = collection.insert_one(feedback_doc)
            
            # Create response
            feedback_response = FeedbackResponse(
                id=str(result.inserted_id),
                message_id=feedback_data.message_id,
                user_id=feedback_data.user_id,
                tone_accuracy=feedback_data.tone_accuracy,
                suggestion_helpfulness=feedback_data.suggestion_helpfulness,
                comments=feedback_data.comments,
                created_at=feedback_doc["created_at"]
            )
            
            logger.info(f"Feedback created successfully: {result.inserted_id}")
            return feedback_response
            
        except Exception as e:
            logger.error(f"Failed to create feedback: {e}")
            raise
    
    async def get_feedback(self, feedback_id: str) -> Optional[FeedbackResponse]:
        """Get feedback by ID"""
        try:
            collection = self._get_collection()
            feedback_doc = collection.find_one({"_id": ObjectId(feedback_id)})
            
            if not feedback_doc:
                return None
            
            return FeedbackResponse(
                id=str(feedback_doc["_id"]),
                message_id=feedback_doc["message_id"],
                user_id=feedback_doc["user_id"],
                tone_accuracy=feedback_doc["tone_accuracy"],
                suggestion_helpfulness=feedback_doc["suggestion_helpfulness"],
                comments=feedback_doc["comments"],
                created_at=feedback_doc["created_at"]
            )
            
        except Exception as e:
            logger.error(f"Failed to get feedback: {e}")
            raise
    
    async def get_feedback_by_message(self, message_id: str) -> List[FeedbackResponse]:
        """Get all feedback for a specific message"""
        try:
            collection = self._get_collection()
            cursor = collection.find({"message_id": message_id}).sort("created_at", -1)
            
            feedback_list = []
            for feedback_doc in cursor:
                feedback = FeedbackResponse(
                    id=str(feedback_doc["_id"]),
                    message_id=feedback_doc["message_id"],
                    user_id=feedback_doc["user_id"],
                    tone_accuracy=feedback_doc["tone_accuracy"],
                    suggestion_helpfulness=feedback_doc["suggestion_helpfulness"],
                    comments=feedback_doc["comments"],
                    created_at=feedback_doc["created_at"]
                )
                feedback_list.append(feedback)
            
            return feedback_list
            
        except Exception as e:
            logger.error(f"Failed to get feedback by message: {e}")
            raise
    
    async def get_user_feedback(self, user_id: str, limit: int = 50) -> List[FeedbackResponse]:
        """Get feedback submitted by a specific user"""
        try:
            collection = self._get_collection()
            cursor = collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
            
            feedback_list = []
            for feedback_doc in cursor:
                feedback = FeedbackResponse(
                    id=str(feedback_doc["_id"]),
                    message_id=feedback_doc["message_id"],
                    user_id=feedback_doc["user_id"],
                    tone_accuracy=feedback_doc["tone_accuracy"],
                    suggestion_helpfulness=feedback_doc["suggestion_helpfulness"],
                    comments=feedback_doc["comments"],
                    created_at=feedback_doc["created_at"]
                )
                feedback_list.append(feedback)
            
            return feedback_list
            
        except Exception as e:
            logger.error(f"Failed to get user feedback: {e}")
            raise
    
    async def get_feedback_stats(self) -> dict:
        """Get overall feedback statistics"""
        try:
            collection = self._get_collection()
            
            # Total feedback count
            total_feedback = collection.count_documents({})
            
            # Average tone accuracy
            pipeline = [
                {"$group": {
                    "_id": None,
                    "avg_tone_accuracy": {"$avg": "$tone_accuracy"},
                    "avg_suggestion_helpfulness": {"$avg": "$suggestion_helpfulness"}
                }}
            ]
            
            stats_result = list(collection.aggregate(pipeline))
            avg_tone_accuracy = stats_result[0]["avg_tone_accuracy"] if stats_result else 0.0
            avg_suggestion_helpfulness = stats_result[0]["avg_suggestion_helpfulness"] if stats_result else 0.0
            
            # Feedback distribution by rating
            tone_accuracy_distribution = {}
            suggestion_helpfulness_distribution = {}
            
            for rating in range(1, 6):
                tone_count = collection.count_documents({"tone_accuracy": rating})
                suggestion_count = collection.count_documents({"suggestion_helpfulness": rating})
                
                tone_accuracy_distribution[str(rating)] = tone_count
                suggestion_helpfulness_distribution[str(rating)] = suggestion_count
            
            return {
                "total_feedback": total_feedback,
                "average_tone_accuracy": avg_tone_accuracy,
                "average_suggestion_helpfulness": avg_suggestion_helpfulness,
                "tone_accuracy_distribution": tone_accuracy_distribution,
                "suggestion_helpfulness_distribution": suggestion_helpfulness_distribution
            }
            
        except Exception as e:
            logger.error(f"Failed to get feedback stats: {e}")
            raise
    
    async def update_feedback(self, feedback_id: str, user_id: str, update_data: dict) -> Optional[FeedbackResponse]:
        """Update feedback (only by the owner)"""
        try:
            collection = self._get_collection()
            
            # Remove immutable fields
            update_data.pop("message_id", None)
            update_data.pop("user_id", None)
            update_data.pop("_id", None)
            update_data["updated_at"] = datetime.utcnow()
            
            result = collection.update_one(
                {
                    "_id": ObjectId(feedback_id),
                    "user_id": user_id
                },
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                return None
            
            # Return updated feedback
            return await self.get_feedback(feedback_id)
            
        except Exception as e:
            logger.error(f"Failed to update feedback: {e}")
            raise
    
    async def delete_feedback(self, feedback_id: str, user_id: str) -> bool:
        """Delete feedback (only by the owner)"""
        try:
            collection = self._get_collection()
            result = collection.delete_one({
                "_id": ObjectId(feedback_id),
                "user_id": user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to delete feedback: {e}")
            raise

# Global feedback service instance
feedback_service = FeedbackService()
