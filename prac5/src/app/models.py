from sqlalchemy import String, Column, BigInteger, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship, Mapped, selectinload

from core.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True)
    username = Column(String(50), index=True, unique=True, nullable=False)
    email = Column(String(75), index=True, unique=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

# # #

class Publisher(Base):
    __tablename__ = "publisher"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(150), nullable=False)

    books: Mapped[list["Book"]] = relationship("Book", back_populates="publisher", lazy="selectin")


writer_book = Table(
    "writer_book",
    Base.metadata,
    Column("writer_id", BigInteger, ForeignKey("writer.id"), primary_key=True),
    Column("book_id", BigInteger, ForeignKey("book.id"), primary_key=True)
)


class Writer(Base):
    __tablename__ = "writer"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)

    books: Mapped[list["Book"]] = relationship(
        "Book",
        secondary=writer_book,
        back_populates="writers",
        lazy="selectin"
    )


class Book(Base):
    __tablename__ = "book"

    id = Column(BigInteger, primary_key=True)
    title = Column(String(200), nullable=False)
    publisher_id = Column(BigInteger, ForeignKey("publisher.id"))

    publisher = relationship("Publisher", back_populates="books", lazy="selectin")
    writers: Mapped[list["Writer"]] = relationship(
        "Writer",
        secondary=writer_book,
        back_populates="books",
        lazy="selectin"
    )
