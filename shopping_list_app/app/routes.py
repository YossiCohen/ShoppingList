from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Household, ShoppingList, ShoppingItem # Added ShoppingItem
from .forms import (LoginForm, RegistrationForm, CreateHouseholdForm,
                    CreateShoppingListForm, AddShoppingItemForm, EditShoppingItemForm) # Added item forms
from .extensions import db

# Using a blueprint named 'main' for these routes.
# If you have auth-specific routes and other main routes, you might split them.
# For this task, one blueprint should suffice.
bp = Blueprint('main', __name__) # 'main' can be used in url_for e.g. url_for('main.index')

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'): # Basic security: ensure next_page is local
            next_page = url_for('main.index')
        flash('Login successful!', 'success')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/create_household', methods=['GET', 'POST'])
@login_required
def create_household():
    form = CreateHouseholdForm()
    if form.validate_on_submit():
        household = Household(name=form.name.data)
        household.users.append(current_user) # Add current user to the household
        db.session.add(household)
        db.session.commit()
        flash(f'Household "{household.name}" created successfully!', 'success')
        return redirect(url_for('main.view_households')) # Or redirect to the specific household page
    return render_template('create_household.html', title='Create Household', form=form)

@bp.route('/households')
@login_required
def view_households():
    # Fetch households directly associated with the current user.
    # The .all() executes the query and gets the list.
    households = current_user.households.all()
    return render_template('view_households.html', title='My Households', households=households)

@bp.route('/household/<int:household_id>/new_list', methods=['GET', 'POST'])
@login_required
def create_shopping_list(household_id):
    household = Household.query.get_or_404(household_id)
    if current_user not in household.users.all(): # Check membership
        abort(403) # Forbidden

    form = CreateShoppingListForm()
    if form.validate_on_submit():
        shopping_list = ShoppingList(name=form.name.data,
                                     date=form.date.data,
                                     household_id=household.id)
        db.session.add(shopping_list)
        db.session.commit()
        flash(f'Shopping list "{shopping_list.name}" created for household "{household.name}"!', 'success')
        return redirect(url_for('main.view_household_lists', household_id=household.id))
    return render_template('create_shopping_list.html', title='Create Shopping List', form=form, household=household)

@bp.route('/household/<int:household_id>/lists')
@login_required
def view_household_lists(household_id):
    household = Household.query.get_or_404(household_id)
    if current_user not in household.users.all(): # Check membership
        abort(403)

    # shopping_lists relation is lazy='dynamic', so it's a query object
    shopping_lists = household.shopping_lists.order_by(ShoppingList.date.desc())
    return render_template('view_household_lists.html', title=f'Lists for {household.name}', household=household, shopping_lists=shopping_lists)

@bp.route('/shopping_list/<int:list_id>/delete', methods=['POST'])
@login_required
def delete_shopping_list(list_id):
    shopping_list = ShoppingList.query.get_or_404(list_id)
    household = shopping_list.household
    if current_user not in household.users.all(): # Check membership
        abort(403)

    db.session.delete(shopping_list)
    db.session.commit()
    flash(f'Shopping list "{shopping_list.name}" has been deleted.', 'success')
    return redirect(url_for('main.view_household_lists', household_id=household.id))

# Shopping Item Routes
@bp.route('/shopping_list/<int:list_id>/add_item', methods=['GET', 'POST'])
@login_required
def add_item_to_list(list_id):
    shopping_list = ShoppingList.query.get_or_404(list_id)
    if current_user not in shopping_list.household.users.all():
        abort(403)

    form = AddShoppingItemForm()
    if form.validate_on_submit():
        item = ShoppingItem(name=form.name.data,
                            category=form.category.data,
                            amount=form.amount.data,
                            free_text=form.free_text.data,
                            shopping_list_id=list_id)
        db.session.add(item)
        db.session.commit()
        flash(f'Item "{item.name}" added to list "{shopping_list.name}".', 'success')
        return redirect(url_for('main.view_list_items', list_id=list_id))
    return render_template('add_item.html', title='Add Item', form=form, shopping_list=shopping_list)

@bp.route('/shopping_list/<int:list_id>/items')
@login_required
def view_list_items(list_id):
    shopping_list = ShoppingList.query.get_or_404(list_id)
    if current_user not in shopping_list.household.users.all():
        abort(403)

    # items relation is lazy='dynamic', can order it here if needed
    items = shopping_list.items.order_by(ShoppingItem.bought.asc(), ShoppingItem.name.asc())
    return render_template('view_list_items.html', title=f'Items for {shopping_list.name}', shopping_list=shopping_list, items=items)

@bp.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = ShoppingItem.query.get_or_404(item_id)
    shopping_list = item.shopping_list
    if current_user not in shopping_list.household.users.all():
        abort(403)

    form = EditShoppingItemForm(obj=item) # Pre-populate form with item data
    if form.validate_on_submit():
        item.name = form.name.data
        item.category = form.category.data
        item.amount = form.amount.data
        item.free_text = form.free_text.data
        item.bought = form.bought.data
        db.session.commit()
        flash(f'Item "{item.name}" updated successfully.', 'success')
        return redirect(url_for('main.view_list_items', list_id=shopping_list.id))
    return render_template('edit_item.html', title='Edit Item', form=form, item=item)

@bp.route('/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    item = ShoppingItem.query.get_or_404(item_id)
    shopping_list_id = item.shopping_list_id
    shopping_list_name = item.shopping_list.name # For flash message

    if current_user not in item.shopping_list.household.users.all():
        abort(403)

    db.session.delete(item)
    db.session.commit()
    flash(f'Item "{item.name}" deleted from list "{shopping_list_name}".', 'success')
    return redirect(url_for('main.view_list_items', list_id=shopping_list_id))

@bp.route('/item/<int:item_id>/toggle_bought', methods=['POST'])
@login_required
def toggle_item_bought(item_id):
    item = ShoppingItem.query.get_or_404(item_id)
    if current_user not in item.shopping_list.household.users.all():
        abort(403)

    item.bought = not item.bought
    db.session.commit()
    status = "bought" if item.bought else "not bought"
    flash(f'Item "{item.name}" marked as {status}.', 'info')
    return redirect(url_for('main.view_list_items', list_id=item.shopping_list_id))
