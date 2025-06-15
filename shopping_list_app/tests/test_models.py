from datetime import datetime
from .base import BaseTestCase # Adjusted import to be relative
from shopping_list_app.app.models import User, Household, ShoppingList, ShoppingItem
from shopping_list_app.app.extensions import db

class TestModelCreation(BaseTestCase):

    def test_user_creation(self):
        user = self.create_user(username="testuser1", email="test1@example.com", password="password123")
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "testuser1")
        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_household_creation(self):
        household = Household(name="Test Household")
        db.session.add(household)
        db.session.commit()
        self.assertIsNotNone(household.id)
        self.assertEqual(household.name, "Test Household")

    def test_shopping_list_creation(self):
        household = Household(name="Home")
        db.session.add(household)
        db.session.commit()

        slist = ShoppingList(name="Groceries", household_id=household.id, date=datetime.utcnow())
        db.session.add(slist)
        db.session.commit()

        self.assertIsNotNone(slist.id)
        self.assertEqual(slist.name, "Groceries")
        self.assertIsNotNone(slist.date)
        self.assertEqual(slist.household_id, household.id)

    def test_shopping_item_creation(self):
        household = Household(name="Home Items")
        db.session.add(household)
        db.session.commit()
        slist = ShoppingList(name="Electronics", household_id=household.id)
        db.session.add(slist)
        db.session.commit()

        item = ShoppingItem(name="Laptop", category="Electronics", amount="1", shopping_list_id=slist.id)
        db.session.add(item)
        db.session.commit()

        self.assertIsNotNone(item.id)
        self.assertEqual(item.name, "Laptop")
        self.assertEqual(item.category, "Electronics")
        self.assertFalse(item.bought) # Default value
        self.assertEqual(item.shopping_list_id, slist.id)

class TestModelRelationships(BaseTestCase):

    def test_user_household_relationship(self):
        user = self.create_user(username="user_rel", email="user_rel@example.com")
        household = Household(name="Shared House")
        db.session.add(household)
        db.session.commit()

        household.users.append(user)
        db.session.commit()

        self.assertIn(user, household.users.all())
        self.assertIn(household, user.households.all())

    def test_household_shopping_list_relationship(self):
        household = Household(name="Kitchen Supplies")
        db.session.add(household)
        db.session.commit()

        slist = ShoppingList(name="Weekly Groceries", household_id=household.id)
        db.session.add(slist)
        db.session.commit()

        self.assertIn(slist, household.shopping_lists.all())
        self.assertEqual(slist.household, household)

    def test_shopping_list_item_relationship(self):
        household = Household(name="Pantry")
        db.session.add(household)
        db.session.commit()
        slist = ShoppingList(name="Snacks", household_id=household.id)
        db.session.add(slist)
        db.session.commit()

        item = ShoppingItem(name="Chips", shopping_list_id=slist.id)
        db.session.add(item)
        db.session.commit()

        self.assertIn(item, slist.items.all())
        self.assertEqual(item.shopping_list, slist)

    def test_cascade_delete_household_to_shoppinglist(self):
        household = Household(name="Temp House")
        db.session.add(household)
        db.session.commit()
        slist = ShoppingList(name="Temp List", household_id=household.id)
        db.session.add(slist)
        db.session.commit()

        household_id = household.id
        slist_id = slist.id

        db.session.delete(household)
        db.session.commit()

        self.assertIsNone(Household.query.get(household_id))
        self.assertIsNone(ShoppingList.query.get(slist_id)) # Relies on cascade="all, delete-orphan"

    def test_cascade_delete_shoppinglist_to_items(self):
        household = Household(name="Another House")
        db.session.add(household)
        db.session.commit()
        slist = ShoppingList(name="Another List", household_id=household.id)
        db.session.add(slist)
        db.session.commit()
        item = ShoppingItem(name="Another Item", shopping_list_id=slist.id)
        db.session.add(item)
        db.session.commit()

        slist_id = slist.id
        item_id = item.id

        db.session.delete(slist)
        db.session.commit()

        self.assertIsNone(ShoppingList.query.get(slist_id))
        self.assertIsNone(ShoppingItem.query.get(item_id)) # Relies on cascade="all, delete-orphan"
