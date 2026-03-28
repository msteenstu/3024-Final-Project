from app import db
from app.models import Book

def populate_book_inventory():
    print("Made it to function")
    #If no books exist in the database,
    #populate it with books.
    if not Book.query.first():
        print("Books added")
        db.session.add_all([
            Book(
                title = "The Hobbit",
                author = "J.R.R. Tolkien",
                genre = "fantasy",
                page_count = 310,
                quantity = 10,
                price = 15.00),
            Book(
                title = "A Wrinkle in Time",
                author = "Madeleine L'Engle",
                genre = "science fiction",
                page_count = 256,
                quantity = 4,
                price = 11.50),            
            Book(
                title = "Project Hail Mary",
                author = "Andy Weir",
                genre = "science fiction",
                page_count = 496,
                quantity = 1,
                price = 16.99),
            Book(
                title = "Misery",
                author = "Stephen King",
                genre = "thriller",
                page_count = 310,
                quantity = 3,
                price = 12.00),
            Book(
                title = "Murder on the Orient Express",
                author = "Agatha Christie",
                genre = "mystery",
                page_count = 256,
                quantity = 7,
                price = 13.49),
            Book(
                title = "Falling Leaves",
                author = "Adeline Yen Mah",
                genre = "biography",
                page_count = 278,
                quantity= 3,
                price = 12.99),
            Book(
                title = "Around the World in Eighty Days",
                author = "Jules Verne",
                genre = "action",
                page_count = 252,
                quantity = 2,
                price = 10.58),
            Book(
                title = "Pride and Prejudice",
                author = "Jane Austen",
                genre = "romance",
                page_count = 435,
                quantity = 5,
                price = 22.00)
        ])
        db.session.commit()
    else:
        return

