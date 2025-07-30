from sqlmodel import Session

# Global engine variable
engine = None


def get_session():
    """Get a database session"""
    with Session(engine) as session:
        yield session
