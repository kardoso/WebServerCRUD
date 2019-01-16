# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
# importar operações CRUD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# importar classes do arquivo "database_setup"
from database_setup import Restaurant, Base, MenuItem

from flask import (Flask, render_template,
                   request, redirect, url_for, flash, jsonify)
app = Flask(__name__)

# selecionar banco de dados
engine = create_engine('sqlite:///restaurantmenu.db')
# estabelecer conexão
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    session.close()
    return jsonify(Restaurants=[r.serialize for r in restaurants])


@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    session.close()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    session.close()
    return jsonify(MenuItems=[item.serialize])


@app.route('/')
@app.route('/restaurants')
def mainRestaurants():
    restaurants = session.query(Restaurant).all()
    session.close()
    return render_template("main_restaurants.html", restaurants=restaurants)


@app.route('/restaurants/new', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        if request.form['name']:
            newEntry = Restaurant(name=request.form['name'])
            session.add(newEntry)
            session.commit()
            session.close()

            flash("New restaurant registered!")
        return redirect(url_for('mainRestaurants'))
    else:
        session.close()
        return render_template('new_restaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurantToEdit = session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['newName']:
            restaurantToEdit.name = request.form['newName']
            session.add(restaurantToEdit)
            session.commit()
            session.close()

            flash("Restaurant edited!")
        return redirect(url_for('mainRestaurants'))
    else:
        session.close()
        return render_template('edit_restaurant.html',
                               restaurant_id=restaurant_id,
                               restaurant=restaurantToEdit)


@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurantToDelete = session.query(
        Restaurant).filter_by(
        id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        session.commit()
        session.close()

        flash("Restaurant deleted!")
        return redirect(url_for('mainRestaurants'))
    else:
        session.close()
        return render_template('delete_restaurant.html',
                               restaurant_id=restaurant_id,
                               restaurant=restaurantToDelete)


@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    restaurant = session.query(
        Restaurant).filter_by(
        id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    session.close()
    return render_template("menu.html",
                            menu_items=items,
                            restaurant=restaurant,
                            restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    restaurant = session.query(
        Restaurant).filter_by(
        id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            newEntry = MenuItem(name=request.form['name'],
                                description=request.form['description'],
                                course=request.form['course'],
                                price=request.form['price'],
                                restaurant=restaurant)

            session.add(newEntry)
            session.commit()
            session.close()

            flash("New item registered!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        session.close()
        return render_template('new_item.html', restaurant_id=restaurant_id, restaurant_name=restaurant.name)


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    restaurant = session.query(
        Restaurant).filter_by(
        id=restaurant_id).one()
    itemToEdit = session.query(
        MenuItem).filter_by(
        id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.name = request.form['name']
            itemToEdit.description = request.form['description']
            itemToEdit.course = request.form['course']
            itemToEdit.price = request.form['price']
            itemToEdit.restaurant = restaurant

            session.add(itemToEdit)
            session.commit()
            session.close()

            flash("Item edited!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        session.close()
        return render_template('edit_item.html', restaurant_id=restaurant_id, restaurant_name=restaurant.name, item=itemToEdit)


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    itemToDelete = session.query(
        MenuItem).filter_by(
        id=menu_id).one()
    restaurant = itemToDelete.restaurant
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        session.close()

        flash("Item deleted!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        session.close()
        return render_template('delete_item.html',
                               restaurant_id=restaurant_id,
                               restaurant_name=restaurant.name,
                               item=itemToDelete)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key'
    )
    app.debug = True
    app.run(host='0.0.0.0', port=port)
