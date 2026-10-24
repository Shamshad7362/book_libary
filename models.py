from sqlalchemy import ForeignKey, String, create_engine, select, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship,sessionmaker


class Base(DeclarativeBase):
    pass
engine = create_engine("sqlite:///books.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100),nullable=False)
    country: Mapped[str] = mapped_column(String(100),nullable=False)

    # One author can have many books
    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    __tablename__ = "books"                                                                                        

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100),nullable=False)

    # This foreign key links a book to its author
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"),nullable=False)

    # Each book belongs to one author
    author: Mapped["Author"] = relationship(back_populates="books")

class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100),nullable=False,unique=True)
    password_hash: Mapped[str] = mapped_column(String(100),nullable=False)
    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False
    )

Base.metadata.create_all(engine)
