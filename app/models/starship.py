"""
SQLAlchemy model for Star Wars starships, along with many-to-many association tables
"""
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.character import character_starship


# Association table for many-to-many relationship between Starships and Films
starship_film_association = Table(
    "starship_film",
    Base.metadata,
    Column("starship_id", Integer, ForeignKey("starships.id")),
    Column("film_id", Integer, ForeignKey("films.id")),
)

class Starship(Base):
    """
    SQLAlchemy model representing a starship
    """
    __tablename__ = "starships"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model = Column(String)
    starship_class = Column(String)

    films = relationship("Film", secondary=starship_film_association, back_populates="starships")
    characters = relationship("Character", secondary=character_starship, back_populates="starships")
