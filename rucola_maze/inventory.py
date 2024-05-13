from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    session,
    request,
    url_for,
)
from .models import *
from . import auth

from .extensions import db
from .forms import IngredientForm, MenuItemForm, RecipeRequirementForm, PurchaseForm
from sqlalchemy.sql import func
from flask_login import login_required  # login_user, logout_user, current_user

bp = Blueprint("inventory", __name__)


@bp.route("/")
@login_required
def home():
    # Count revenue

    revenue_cents = 0
    for p in Purchase.query.all():
        menu_item_price_cents = (
            p.menu_item.price_dollars * 100 + p.menu_item.price_cents
        )
        revenue_cents += menu_item_price_cents

    # Total cost of all purchases (sum of cost of all ingredients used)
    cost_of_ingredients_cents = 0

    for p in Purchase.query.all():
        for rr in p.menu_item.in_recipe_requirements.all():
            unit_price_cents = (
                rr.ingredient.unit_price_dollars * 100 + rr.ingredient.unit_price_cents
            )
            cost_of_ingredients_cents += unit_price_cents * rr.quantity_required

    revenue = revenue_cents / 100
    cost_of_ingredients = cost_of_ingredients_cents / 100
    profit = revenue - cost_of_ingredients

    return render_template(
        "inventory/home.html",
        cost_of_ingredients=cost_of_ingredients,
        revenue=revenue,
        profit=profit,
    )


@bp.route("/ingredients/")
@login_required
def ingredients():
    ingredients = Ingredient.query.order_by(Ingredient.name)
    return render_template("inventory/ingredients.html", ingredients=ingredients)


@bp.route("/ingredients/new", methods=["GET", "POST"])
@login_required
def ingredient_new():
    form = IngredientForm(request.form)
    if form.validate_on_submit():
        ingredient = Ingredient(
            name=form.name.data,
            quantity_available=form.quantity_available.data,
            unit=form.unit.data,
            unit_price_dollars=form.unit_price_dollars.data,
            unit_price_cents=form.unit_price_cents.data,
        )
        db.session.add(ingredient)

        try:
            db.session.commit()
            flash(
                f"Вы добавили ингредиент '{ingredient}', ${ingredient.unit_price_dollars}.{ingredient.unit_price_cents} за {ingredient.unit}!"
            )
        except:
            db.session.rollback()
            flash(
                f"Ингредиент '{form.name.data}' уже существует! Хотите отредактировать его?"
            )
            return render_template(
                "inventory/ingredient_new.html",
                form=form,
                name=form.name.data,
            )
        return redirect(url_for("inventory.ingredients"))
    return render_template("inventory/ingredient_new.html", form=form)


@bp.route("/ingredients/<int:ingredient_id>/edit", methods=["GET", "POST"])
@login_required
def ingredient_edit(ingredient_id):
    ingredient = Ingredient.query.get(ingredient_id)
    form = IngredientForm()
    if form.validate_on_submit():
        ingredient.name = form.name.data
        ingredient.quantity_available = form.quantity_available.data
        ingredient.unit = form.unit.data
        ingredient.unit_price_dollars = form.unit_price_dollars.data
        ingredient.unit_price_cents = form.unit_price_cents.data
        try:
            db.session.commit()
            flash(
                f"Вы отредактировали инредиент '{ingredient}', {ingredient.unit_price_dollars}.{ingredient.unit_price_cents} руб. за {ingredient.unit}!"
            )
            return redirect(url_for("inventory.ingredients"))
        except:
            flash(f"Ингредиент '{form.name.data}' уже существует! Хотите отредактировать его?")
            db.session.rollback()
    form = IngredientForm(obj=ingredient)
    return render_template(
        "inventory/ingredient_edit.html",
        form=form,
        ingredient=ingredient,
    )


@bp.route("/ingredients/<int:ingredient_id>/delete", methods=["GET", "POST"])
@login_required
def ingredient_delete(ingredient_id):
    ingredient = Ingredient.query.get(ingredient_id)
    if request.method == "POST":
        if "yes" in request.form:
            db.session.delete(ingredient)
            db.session.commit()
            flash(f"Вы удалили ингредиент '{ingredient}'.")
        return redirect(url_for("inventory.ingredients"))
    return render_template("inventory/ingredient_delete.html", ingredient=ingredient)


@bp.route("/menu_items/")
@login_required
def menu_items():
    menu_items = MenuItem.query.order_by(MenuItem.title)
    available_menu_items = [m for m in MenuItem.query.all() if m.is_available()]
    return render_template(
        "inventory/menu_items.html",
        menu_items=menu_items,
        available_menu_items=available_menu_items,
    )


@bp.route("/menu_items/new", methods=["GET", "POST"])
@login_required
def menu_item_new():
    form = MenuItemForm()
    error = None
    if form.validate_on_submit():
        menu_item = MenuItem(
            title=form.title.data,
            price_dollars=form.price_dollars.data,
            price_cents=form.price_cents.data,
        )
        db.session.add(menu_item)
        try:
            db.session.commit()
            flash(
                f"Вы отредактировали блюдо '{menu_item}', стоимость: {menu_item.price_dollars}.{menu_item.price_cents} руб."
            )
        except:
            db.session.rollback()
            flash(f"Блюдо '{form.title.data}' уже существует!")
            return render_template(
                "inventory/menu_item_new.html", form=form, error=error
            )
        return redirect(url_for("inventory.menu_items"))
    return render_template("inventory/menu_item_new.html", form=form)


@bp.route("/menu_items/<int:menu_item_id>/edit", methods=["GET", "POST"])
@login_required
def menu_item_edit(menu_item_id):
    menu_item = MenuItem.query.get(menu_item_id)
    form = MenuItemForm()
    if form.validate_on_submit():
        try:
            menu_item.title = form.title.data
            menu_item.price_dollars = form.price_dollars.data
            menu_item.price_cents = form.price_cents.data
            db.session.commit()
            flash(
                f"Вы отредактировали блюдо '{menu_item}, стоимость: {menu_item.price_dollars}.{menu_item.price_cents} руб."
            )
            return redirect(url_for("inventory.menu_items"))
        except:
            flash(f"Блюдо '{form.title.data}' уже существует!")
            db.session.rollback()
    return render_template(
        "inventory/menu_item_edit.html",
        form=MenuItemForm(obj=menu_item),
        menu_item=menu_item,
    )


@bp.route("/menu_items/<int:menu_item_id>/delete", methods=["GET", "POST"])
@login_required
def menu_item_delete(menu_item_id):
    menu_item = MenuItem.query.get(menu_item_id)
    if request.method == "POST":
        if "yes" in request.form:
            flash(f"Вы удалили блюдо '{menu_item}'.")
            db.session.delete(menu_item)
            db.session.commit()
        return redirect(url_for("inventory.menu_items"))
    return render_template("inventory/menu_item_delete.html", menu_item=menu_item)


@bp.route("/recipe_requirements/")
@login_required
def recipe_requirements():
    recipe_requirements = (
        db.session.query(RecipeRequirement)
        .join(RecipeRequirement.menu_item)
        .order_by(MenuItem.title)
    )

    return render_template(
        "inventory/recipe_requirements.html", recipe_requirements=recipe_requirements
    )


@bp.route("/recipe_requirements/new", methods=["GET", "POST"])
@login_required
def recipe_requirement_new():
    form = RecipeRequirementForm()
    form.all_ingredients_possible.query = Ingredient.query
    form.all_menu_items_possible.query = MenuItem.query
    if form.validate_on_submit():
        ingredient = form.all_ingredients_possible.data
        menu_item = form.all_menu_items_possible.data
        # Check if recipe req. with the same ingred/menu item pair already exists
        if not RecipeRequirement.query.filter(
            RecipeRequirement.menu_item_id == menu_item.id,
            RecipeRequirement.ingredient_id == ingredient.id,
        ).all():
            recipe_requirement = RecipeRequirement(
                quantity_required=form.quantity_required.data,
                ingredient_id=ingredient.id,
                menu_item_id=menu_item.id,
            )
            db.session.add(recipe_requirement)
            db.session.commit()
            flash(
                f"Вы добавили требование рецепта для блюда: {menu_item} ({recipe_requirement})."
            )
            return redirect(url_for("inventory.recipe_requirements"))
        flash(
            f"Требование рецепта '{ingredient} для {menu_item}' уже существует! Хотите отредактировать его?"
        )

    return render_template("inventory/recipe_requirement_new.html", form=form)


@bp.route(
    "/recipe_requirements/<int:recipe_requirement_id>/edit", methods=["GET", "POST"]
)
@login_required
def recipe_requirement_edit(recipe_requirement_id):
    recipe_requirement = RecipeRequirement.query.get(recipe_requirement_id)
    form = RecipeRequirementForm()
    if request.method == "POST":
        recipe_requirement.quantity_required = form.quantity_required.data
        db.session.commit()
        flash(
            f"Вы отредактировали требование рецепта для блюда {recipe_requirement.menu_item} ({recipe_requirement})."
        )
        return redirect(url_for("inventory.recipe_requirements"))

    menu_item = MenuItem.query.get(recipe_requirement.menu_item_id)
    ingredient = Ingredient.query.get(recipe_requirement.ingredient_id)
    return render_template(
        "inventory/recipe_requirement_edit.html",
        form=RecipeRequirementForm(obj=recipe_requirement),
        recipe_requirement=recipe_requirement,
        menu_item=menu_item,
        ingredient=ingredient,
    )


@bp.route(
    "/recipe_requirements/<int:recipe_requirement_id>/delete", methods=["GET", "POST"]
)
@login_required
def recipe_requirement_delete(recipe_requirement_id):
    recipe_requirement = RecipeRequirement.query.get(recipe_requirement_id)
    if request.method == "POST":
        if "yes" in request.form:
            flash(
                f"Вы удалили требование рецепта для {recipe_requirement.menu_item}."
            )
            db.session.delete(recipe_requirement)
            db.session.commit()

        return redirect(url_for("inventory.recipe_requirements"))
    return render_template(
        "inventory/recipe_requirement_delete.html",
        recipe_requirement=recipe_requirement,
    )


@bp.route("/purchases/")
@login_required
def purchases():
    purchases = Purchase.query.all()
    return render_template("inventory/purchases.html", purchases=purchases)


@bp.route("/purchases/new", methods=["GET", "POST"])
@login_required
def purchase_new():
    available_menu_items = [m for m in MenuItem.query.all() if m.is_available()]
    form = PurchaseForm()
    form.available_menu_items.query = available_menu_items
    if form.validate_on_submit():
        menu_item_id = form.available_menu_items.data.id
        purchase = Purchase(menu_item_id=menu_item_id)
        menu_item = MenuItem.query.get(menu_item_id)
        for mirr in menu_item.in_recipe_requirements.all():
            ingredient = Ingredient.query.get(mirr.ingredient_id)
            ingredient.quantity_available -= mirr.quantity_required
            db.session.commit()
        db.session.add(purchase)
        db.session.commit()
        flash(f"You've added {purchase}.")
        return redirect(url_for("inventory.purchases"))
    return render_template(
        "inventory/purchase_new.html",
        form=form,
        available_menu_items=available_menu_items,
    )


# Deleting a purchase only removes it from calculations, # but doesn't return the ingredients etc.
# so it's like if a customer got the order but refused to pay


@bp.route("/purchases/<int:purchase_id>/delete", methods=["GET", "POST"])
@login_required
def purchase_delete(purchase_id):
    purchase = Purchase.query.get(purchase_id)
    if request.method == "POST":
        if "yes" in request.form:
            db.session.delete(purchase)
            db.session.commit()
            flash(f"Вы удалили покупку из расчетов")
        return redirect(url_for("inventory.purchases"))
    return render_template("inventory/purchase_delete.html", purchase=purchase)


"""
Let's remove purchase edit because it doesn't make much sense in this context

@bp.route("/puchases/<int:purchase_id>/edit", methods=["GET", "POST"])
def purchase_edit(purchase_id):
    purchase = Purchase.query.get(purchase_id)
    form = PurchaseForm()
    available_menu_items = MenuItem.query.filter(MenuItem.is_available == True).all()
    form.available_menu_items.query = available_menu_items
    if request.method == "POST":
        menu_item_id = form.available_menu_items.data.id
        purchase.menu_item_id = menu_item_id
        db.session.commit()
        return redirect(url_for("inventory.purchases"))
    form = PurchaseForm(obj=purchase)
    form.available_menu_items.query = available_menu_items
    menu_item = MenuItem.query.get(purchase.menu_item_id)
    return render_template(
        "inventory/purchase_edit.html",
        form=form,
        purchase=purchase,
        menu_item=menu_item,
        available_menu_items=available_menu_items,
    )
"""
