from typing import Optional
from datetime import datetime, timedelta
from bson import ObjectId
import logging
from passlib.context import CryptContext
from jose import JWTError, jwt
from ..database import db_manager
from ..models import UserCreate, UserResponse, UserInDB, TokenData
from ..config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self):
        self.collection_name = "users"
    
    def _get_collection(self):
        return db_manager.get_collection(self.collection_name)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return TokenData(username=username)
        except JWTError:
            return None
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        try:
            collection = self._get_collection()
            
            # Check if user already exists
            existing_user = collection.find_one({
                "$or": [
                    {"email": user_data.email},
                    {"username": user_data.username}
                ]
            })
            
            if existing_user:
                raise ValueError("User with this email or username already exists")
            
            # Hash password
            hashed_password = self.get_password_hash(user_data.password)
            
            # Create user document
            user_doc = {
                "username": user_data.username,
                "email": user_data.email,
                "hashed_password": hashed_password,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
            
            # Insert into database
            result = collection.insert_one(user_doc)
            
            # Create response
            user_response = UserResponse(
                id=str(result.inserted_id),
                username=user_data.username,
                email=user_data.email,
                created_at=user_doc["created_at"],
                is_active=True
            )
            
            logger.info(f"User created successfully: {result.inserted_id}")
            return user_response
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Get user by username"""
        try:
            collection = self._get_collection()
            user_doc = collection.find_one({"username": username})
            
            if not user_doc:
                return None
            
            return UserInDB(
                id=str(user_doc["_id"]),
                username=user_doc["username"],
                email=user_doc["email"],
                hashed_password=user_doc["hashed_password"],
                created_at=user_doc["created_at"],
                is_active=user_doc.get("is_active", True)
            )
            
        except Exception as e:
            logger.error(f"Failed to get user by username: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        try:
            collection = self._get_collection()
            user_doc = collection.find_one({"email": email})
            
            if not user_doc:
                return None
            
            return UserInDB(
                id=str(user_doc["_id"]),
                username=user_doc["username"],
                email=user_doc["email"],
                hashed_password=user_doc["hashed_password"],
                created_at=user_doc["created_at"],
                is_active=user_doc.get("is_active", True)
            )
            
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            collection = self._get_collection()
            user_doc = collection.find_one({"_id": ObjectId(user_id)})
            
            if not user_doc:
                return None
            
            return UserResponse(
                id=str(user_doc["_id"]),
                username=user_doc["username"],
                email=user_doc["email"],
                created_at=user_doc["created_at"],
                is_active=user_doc.get("is_active", True)
            )
            
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            raise
    
    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """Authenticate a user"""
        try:
            user = await self.get_user_by_username(username)
            if not user:
                return None
            
            if not self.verify_password(password, user.hashed_password):
                return None
            
            if not user.is_active:
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to authenticate user: {e}")
            raise
    
    async def update_user(self, user_id: str, update_data: dict) -> Optional[UserResponse]:
        """Update user information"""
        try:
            collection = self._get_collection()
            
            # Remove sensitive fields from update data
            update_data.pop("hashed_password", None)
            update_data.pop("_id", None)
            update_data["updated_at"] = datetime.utcnow()
            
            result = collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                return None
            
            # Return updated user
            return await self.get_user_by_id(user_id)
            
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            raise
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account"""
        try:
            collection = self._get_collection()
            result = collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to deactivate user: {e}")
            raise
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            # Get current user
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            # Verify old password
            user_with_password = await self.get_user_by_username(user.username)
            if not self.verify_password(old_password, user_with_password.hashed_password):
                return False
            
            # Hash new password
            new_hashed_password = self.get_password_hash(new_password)
            
            # Update password
            collection = self._get_collection()
            result = collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "hashed_password": new_hashed_password,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to change password: {e}")
            raise

# Global user service instance
user_service = UserService()
