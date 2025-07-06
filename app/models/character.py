"""
SQLAlchemy model for Star Wars starships, along with many-to-many association tables
"""
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


# Association table for many-to-many relationship between Characters and Films
character_film = Table(
    "character_film",
    Base.metadata,
    Column("character_id", Integer, ForeignKey("characters.id")),
    Column("film_id", Integer, ForeignKey("films.id")),
)

# Association table for many-to-many relationship between Characters and Starships
character_starship = Table(
    "character_starship",
    Base.metadata,
    Column("character_id", Integer, ForeignKey("characters.id")),
    Column("starship_id", Integer, ForeignKey("starships.id")),
)

class Character(Base):
    """
    SQLAlchemy model representing a character
    """
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    height = Column(String)
    mass = Column(String)

    films = relationship("Film", secondary=character_film, back_populates="characters")
    starships = relationship("Starship", secondary=character_starship, back_populates="characters")