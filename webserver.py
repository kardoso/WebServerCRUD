# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
# importar operações CRUD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# importar classes do arquivo "database_setup"
from database_setup import Restaurant, Base, MenuItem, User

from flask import (Flask, render_template,
                   request, redirect, url_for, flash, jsonify)
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

import hashlib

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu App"

# selecionar banco de dados
engine = create_engine('sqlite:///restaurantmenu.db')
# estabelecer conexão
DBSession = sessionmaker(bind=engine)
session = DBSession()


#Token antifraude
@app.route('/login')
def showLogin():
    #state = ''.join(random.choice(string.ascii_uppercase + string.digits)
     #               for x in range(32))
    #login_session['state'] = state
    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    login_session['state'] = state
    return render_template('login.html', STATE=state)
    #return "The current session state is %s" % login_session['state']


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print('invalid state')
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print('failed authorization')
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    #result = json.loads(h.request(url, 'GET')[1])
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    #data = answer.json()
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check if user exists, if not create a new one
    if not getUserID(login_session['email']):
        login_session['user_id'] = createUser(login_session)

    flash("You are now logged in as %s" % login_session['username'])
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


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

    pageToLoad = ''
    if getUserID(login_session.get('email')):
        pageToLoad = "main_restaurants.html"
    else:
        pageToLoad = "public_restaurants.html"

    session.close()

    return render_template(pageToLoad, restaurants=restaurants)


@app.route('/restaurants/new', methods=['GET', 'POST'])
def newRestaurant():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            newEntry = Restaurant(name=request.form['name'],
                user_id=login_session['user_id'])
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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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

    creator = getUserInfo(restaurant.user_id)
    
    pageToLoad = ''
    if login_session.get('email') == creator.email:
        pageToLoad = "menu.html"
    else:
        pageToLoad = "public_menu.html"

    session.close()

    return render_template(pageToLoad,
                            menu_items=items,
                            restaurant=restaurant,
                            restaurant_id=restaurant_id,
                            creator=creator)


@app.route('/restaurants/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(
        Restaurant).filter_by(
        id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            newEntry = MenuItem(name=request.form['name'],
                                description=request.form['description'],
                                course=request.form['course'],
                                price=request.form['price'],
                                restaurant=restaurant,
                                user_id=restaurant.user_id)

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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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
