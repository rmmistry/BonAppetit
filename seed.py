""" file to seed categories into database"""

"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import Category, connect_to_db, db
from server import app


def load_categories():
    """Load categories into database."""

    categories = ['Appetizers',
                  'Bread',
                  'Breakfast',
                  'Desserts',
                  'Drinks',
                  'Main Dish',
                  'Salad',
                  'Side Dish',
                  'Soups, Stews and Chili',
                  'Marinades and Sauces',
                  'Other']

    for category in categories:

        add_category = Category(category_name=category)

        # We need to add to the session or it won't ever be stored
        db.session.add(add_category)

    # Once we're done, we should commit our work
    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    load_categories()
