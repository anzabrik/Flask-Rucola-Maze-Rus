from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    SubmitField,
    DateTimeField,
    BooleanField,
    PasswordField,
)
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired

from .models import *


class RegistrationForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired()])
    email = StringField("Имейл", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password2 = PasswordField(
        "Проверка пароля", validators=[DataRequired(), EqualTo("password")]
    )
    remember = BooleanField("Запомнить")


class LoginForm(FlaskForm):
    email = StringField("Имейл", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить")


class IngredientForm(FlaskForm):
    name = StringField("Название ингредиента", validators=[DataRequired()])
    quantity_available = StringField("Доступное количество", validators=[DataRequired()])
    unit = StringField("Единица измерения", validators=[DataRequired()], default="кг")
    unit_price_dollars = IntegerField(
        "Цена за единицу: рубли", validators=[InputRequired()], default=0
    )
    unit_price_cents = StringField("коп.", validators=[DataRequired()], default="00")
    submit = SubmitField("Сохранить")


class MenuItemForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    price_dollars = IntegerField("Цена, руб.:", validators=[InputRequired()])
    price_cents = StringField("коп.", validators=[DataRequired()], default="00")
    submit = SubmitField("Сохранить")


class RecipeRequirementForm(FlaskForm):  # INCLUDE ONLY AVAILABLE ITEMS
    quantity_required = StringField("Требуемое количество", validators=[DataRequired()])
    all_ingredients_possible = QuerySelectField(label="Ингредиент", allow_blank=False)
    all_menu_items_possible = QuerySelectField(label="Ингредиент", allow_blank=False)

    submit = SubmitField("Сохранить")


class PurchaseForm(FlaskForm):
    available_menu_items = QuerySelectField(label="Блюдо", allow_blank=False)
    submit = SubmitField("Сохранить")
    pass
