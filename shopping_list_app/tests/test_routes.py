from .base import BaseTestCase # Adjusted import
from shopping_list_app.app.models import User, Household, ShoppingList, ShoppingItem
from shopping_list_app.app.extensions import db
from flask import url_for

class TestRoutes(BaseTestCase):

    def setUp(self):
        super().setUp()
        # Create a user and log them in for most route tests
        self.user = self.create_user(username="routetester", email="route@example.com", password="password")
        self.login_user(email="route@example.com", password="password")

    def test_index_page_access(self):
        response = self.client.get('/') # or '/index'
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Shopping List App!', response.data)
        self.assertIn(b'routetester', response.data) # Check if username is displayed

    def test_create_household_get(self):
        response = self.client.get('/create_household')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Household', response.data)

    def test_create_household_post(self):
        response = self.client.post('/create_household', data=dict(
            name="Test House 1"
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Should redirect to view_households
        self.assertIn(b'Test House 1', response.data) # Check if new household name is on page

        household = Household.query.filter_by(name="Test House 1").first()
        self.assertIsNotNone(household)
        self.assertIn(self.user, household.users.all())

    def test_view_households_page(self):
        # First create a household for the user
        self.client.post('/create_household', data=dict(name="Viewable House"), follow_redirects=True)

        response = self.client.get('/households')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Viewable House', response.data)

    def test_create_shopping_list_get_and_post(self):
        # Create a household first
        household_response = self.client.post('/create_household', data=dict(name="List House"), follow_redirects=True)
        household = Household.query.filter_by(name="List House").first()
        self.assertIsNotNone(household)

        # Test GET for create shopping list form
        response_get = self.client.get(f'/household/{household.id}/new_list')
        self.assertEqual(response_get.status_code, 200)
        self.assertIn(b'Create New Shopping List for List House', response_get.data)

        # Test POST to create shopping list
        response_post = self.client.post(f'/household/{household.id}/new_list', data=dict(
            name="Groceries for List House",
            date="2024-01-01" # Assuming YYYY-MM-DD format
        ), follow_redirects=True)
        self.assertEqual(response_post.status_code, 200) # Redirects to view_household_lists
        self.assertIn(b'Groceries for List House', response_post.data)

        slist = ShoppingList.query.filter_by(name="Groceries for List House").first()
        self.assertIsNotNone(slist)
        self.assertEqual(slist.household_id, household.id)

    def test_add_item_to_list_get_and_post(self):
        # Create household and list
        self.client.post('/create_household', data=dict(name="Item House"), follow_redirects=True)
        household = Household.query.filter_by(name="Item House").first()
        self.client.post(f'/household/{household.id}/new_list', data=dict(name="Item List", date="2024-01-02"), follow_redirects=True)
        slist = ShoppingList.query.filter_by(name="Item List").first()
        self.assertIsNotNone(slist)

        # Test GET for add item form
        response_get = self.client.get(f'/shopping_list/{slist.id}/add_item')
        self.assertEqual(response_get.status_code, 200)
        self.assertIn(b'Add Item to: Item List', response_get.data)

        # Test POST to add item
        response_post = self.client.post(f'/shopping_list/{slist.id}/add_item', data=dict(
            name="Milk",
            category="Dairy",
            amount="1 Gallon"
        ), follow_redirects=True)
        self.assertEqual(response_post.status_code, 200) # Redirects to view_list_items
        self.assertIn(b'Milk', response_post.data)
        self.assertIn(b'Dairy', response_post.data)

        item = ShoppingItem.query.filter_by(name="Milk").first()
        self.assertIsNotNone(item)
        self.assertEqual(item.shopping_list_id, slist.id)

    def test_access_household_lists_unauthorized(self):
        # Create another user and their household
        other_user = self.create_user(username="otheruser", email="other@example.com", password="password")
        other_household = Household(name="Other's House")
        other_household.users.append(other_user)
        db.session.add(other_household)
        db.session.commit()

        # Try to access other_household's list creation page as self.user
        response = self.client.get(f'/household/{other_household.id}/new_list')
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_delete_shopping_list(self):
        # Create household and list
        self.client.post('/create_household', data=dict(name="HouseToDeleteListFrom"), follow_redirects=True)
        household = Household.query.filter_by(name="HouseToDeleteListFrom").first()
        self.client.post(f'/household/{household.id}/new_list', data=dict(name="ListToDelete", date="2024-01-03"), follow_redirects=True)
        slist = ShoppingList.query.filter_by(name="ListToDelete").first()
        self.assertIsNotNone(slist)
        slist_id = slist.id

        # Delete the list
        response = self.client.post(f'/shopping_list/{slist_id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Shopping list &quot;ListToDelete&quot; has been deleted.', response.data) # Check flash message (HTML escaped)

        deleted_list = ShoppingList.query.get(slist_id)
        self.assertIsNone(deleted_list)

    def test_toggle_item_bought(self):
        # Create household, list, and item
        self.client.post('/create_household', data=dict(name="ToggleHouse"), follow_redirects=True)
        household = Household.query.filter_by(name="ToggleHouse").first()
        self.client.post(f'/household/{household.id}/new_list', data=dict(name="ToggleList", date="2024-01-04"), follow_redirects=True)
        slist = ShoppingList.query.filter_by(name="ToggleList").first()
        self.client.post(f'/shopping_list/{slist.id}/add_item', data=dict(name="ToggleItem"), follow_redirects=True)
        item = ShoppingItem.query.filter_by(name="ToggleItem").first()
        self.assertIsNotNone(item)
        self.assertFalse(item.bought) # Initially not bought

        # Toggle to bought
        response_bought = self.client.post(f'/item/{item.id}/toggle_bought', follow_redirects=True)
        self.assertEqual(response_bought.status_code, 200)
        self.assertIn(b'marked as bought', response_bought.data)
        db.session.refresh(item) # Refresh item state from DB
        self.assertTrue(item.bought)

        # Toggle to unbought
        response_unbought = self.client.post(f'/item/{item.id}/toggle_bought', follow_redirects=True)
        self.assertEqual(response_unbought.status_code, 200)
        self.assertIn(b'marked as not bought', response_unbought.data)
        db.session.refresh(item) # Refresh item state from DB
        self.assertFalse(item.bought)
