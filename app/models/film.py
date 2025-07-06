"""
SQLAlchemy model for Star Wars films
"""
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.starship import starship_film_association
from app.models.character import character_film


class Film(Base):
    """
    SQLAlchemy model representing a film
    """
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    episode_id = Column(Integer)
    opening_crawl = Column(String)
    director = Column(String)
    producer = Column(String)
    release_date = Column(String)

    starships = relationship("Starship", secondary=starship_film_association, back_populates="films")
    characters = relationship("Character", secondary=character_film, back_populates="films")
