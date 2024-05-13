from .extensions import db, login_manager
from datetime import datetime
from sqlalchemy.orm import mapped_column
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin, db.Model):
    id = mapped_column(db.Integer, primary_key=True)
    username = mapped_column(db.String(64), unique=True, index=True)
    email = mapped_column(db.String(128), index=True, unique=True)
    password_hash = mapped_column(db.String(128))
    joined_at = mapped_column(db.DateTime(), index=True, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return f"{self.username}"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Ingredient(db.Model):
    id = mapped_column(db.Integer, primary_key=True)
    name = mapped_column(db.String(96), unique=True, index=True)
    quantity_available = mapped_column(
        db.Numeric(precision=2, asdecimal=False, decimal_return_scale=None), default=0
    )
    unit = mapped_column(db.String(16))
    unit_price_dollars = mapped_column(db.Integer, default=0)
    unit_price_cents = mapped_column(db.Integer, default=0)
    in_recipe_requirements = db.relationship(
        "RecipeRequirement",
        backref="ingredient",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
    )

    def __str__(self):
        return self.name


class MenuItem(db.Model):
    id = mapped_column(db.Integer, primary_key=True)
    title = mapped_column(db.String(128), unique=True, index=True)
    price_dollars = mapped_column(db.Integer)
    price_cents = mapped_column(db.Integer, default=0)
    in_recipe_requirements = db.relationship(
        "RecipeRequirement",
        backref="menu_item",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
    )
    purchases = db.relationship(
        "Purchase",
        backref="menu_item",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
    )

    def __str__(self):
        return self.title

    def is_available(self):
        if self.in_recipe_requirements.all():
            # list of booleans - whether each recipe_requirement is in stock
            rr_availability_list = [
                rr.in_stock() for rr in self.in_recipe_requirements.all()
            ]
            # check whether all the booleans in this list are "true"
            #  - if yes, then Menu_item.is_available() returns "true"
            return all(rr_availability_list)
        return False


class RecipeRequirement(db.Model):
    id = mapped_column(db.Integer, primary_key=True)
    ingredient_id = mapped_column(db.Integer, db.ForeignKey("ingredient.id"))
    menu_item_id = mapped_column(db.Integer, db.ForeignKey("menu_item.id"))
    quantity_required = mapped_column(
        db.Numeric(precision=2, asdecimal=False, decimal_return_scale=None)
    )

    def __str__(self):
        return f"{self.ingredient}: {self.quantity_required} {self.ingredient.unit}"

    def in_stock(self):
        ingredient = Ingredient.query.get(self.ingredient_id)  # the ing object
        return self.quantity_required <= ingredient.quantity_available


class Purchase(db.Model):
    id = mapped_column(db.Integer, primary_key=True)
    menu_item_id = mapped_column(db.Integer, db.ForeignKey("menu_item.id"))
    time = mapped_column(db.DateTime(), default=datetime.utcnow, index=True)

    def __str__(self):
        return f"purchase {self.id}: {self.menu_item}"
