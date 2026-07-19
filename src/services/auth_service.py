from datetime import timedelta

from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.logger import setup_logger
from src.core.security import create_access_token, get_password_hash, verify_password
from src.models.user import User
from src.schemas.user import UserCreate

logger = setup_logger(__name__)


def create_user(db: Session, user_data: UserCreate) -> User:
    """Register a new user. Raises ValueError if email already exists."""
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise ValueError("User with this email already exists")

    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Created user: {user.email}")
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Verify email/password and return the user, or None if invalid."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_token_for_user(user: User) -> str:
    """Generate a JWT access token for a user."""
    return create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
