import logging
logging.basicConfig(level=logging.DEBUG, format='### %(message)s (%(levelname)s %(asctime)s)')

import os
basedir = os.path.abspath(os.path.dirname(__file__))

from datetime import datetime
from flask import Flask
from flask import render_template, url_for, request, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Base model that for other models to inherit from
class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# Model for Restaurant
class Restaurant(Base):
    name = db.Column(db.String(200))
    menu = db.relationship('MenuItem', backref='restaurant', lazy=False)
    def __repr__(self):
        return self.name
    @property
    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name
        }

# Model for MenuItem
class MenuItem(Base):
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    name = db.Column(db.String(100))
    price = db.Column(db.String(10))
    description = db.Column(db.String(800))
    course = db.Column(db.String(800))
    def __repr__(self):
        return self.name
    @property
    def serialize(self):
        return {
            'id' : self.id,
            'restaurant_id' : self.restaurant_id,
            'name' : self.name,
            'price' : self.price,
            'description' : self.description,
            'course' : self.course,
        }

now = datetime.now()
currentYear = now.year
@app.context_processor
def inject_year():
    return dict(currentYear=currentYear)

#Fake Restaurants
#restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}
#restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'}, {'name':'Taco Hut', 'id':'3'}]

#Fake Menu Items
#items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$0.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
#item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

### INDEX / SHOW ALL RESTAURANTS

@app.route('/restaurants/')
@app.route('/')
def showAllRestaurants():
    restaurants = Restaurant.query.all()
    return render_template('restaurant/showAllRestaurants.html',restaurants=restaurants)

@app.route('/test/')
@app.route('/t/')
def showTestPage():
    return render_template('test.html')

### RESTAURANTS

@app.route('/restaurant/new/', methods=['GET', 'POST'])
def createRestaurant():
    if request.method == 'POST':
        newRestaurant = Restaurant (
            name = request.form['nameNewRestaurant']
        )
        db.session.add(newRestaurant)
        db.session.commit()
        flash("New restaurant created!")
        return redirect(url_for('showAllRestaurants'))
    else:
        return render_template('restaurant/createRestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        restaurant.name = request.form['nameEditRestaurant']
        db.session.add(restaurant)
        db.session.commit()
        flash("Changes in restaurant saved.")
        return redirect(url_for('showAllRestaurants'))
    else:
        return render_template('restaurant/editRestaurant.html',restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        db.session.delete(restaurant)
        db.session.commit()
        flash("Restaurant deleted.")
        return redirect(url_for('showAllRestaurants'))
    else:
        return render_template('restaurant/deleteRestaurant.html',restaurant=restaurant)

### MENUS

@app.route('/<int:restaurant_id>/')
@app.route('/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).one()
    items = restaurant.menu
    return render_template('menu/showMenu.html',restaurant=restaurant,items=items)

@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def createMenuItem(restaurant_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        newMenuItem = MenuItem(
            restaurant_id = restaurant_id,
            name = request.form['inputMenuItemName'],
            price = request.form['inputMenuItemPrice'],
            description = request.form['inputMenuItemDescription'],
            course = request.form['inputMenuItemCourse']
        )
        db.session.add(newMenuItem)
        db.session.commit()
        flash("New menu item for " + restaurant.name + " created!")
        return redirect(url_for('showMenu',restaurant_id=restaurant_id))
    else:
        return render_template('menu/newMenuItem.html',restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editMenuItem(restaurant_id,menu_id):
    item = MenuItem.query.filter_by(id=menu_id).one()
    restaurant = item.restaurant
    if request.method == 'POST':
        item.name = request.form['inputMenuItemName']
        item.price = request.form['inputMenuItemPrice']
        item.description = request.form['inputMenuItemDescription']
        item.course = request.form['inputMenuItemCourse']
        db.session.add(item)
        db.session.commit()
        flash("Changes for " + item.name + " saved.")
        return redirect(url_for('showMenu',restaurant_id=restaurant_id))
    else:
        return render_template('menu/editMenuItem.html',restaurant=restaurant,item=item)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id,menu_id):
    item = MenuItem.query.filter_by(id=menu_id).one()
    restaurant = item.restaurant
    if request.method == 'POST':
        db.session.delete(item)
        db.session.commit()
        flash("Menu item " + item.name + " deleted.")
        return redirect(url_for('showMenu',restaurant_id=restaurant_id))
    else:
        return render_template('menu/deleteMenuItem.html',restaurant=restaurant,item=item)

### API Endpoints (GET Request)

@app.route('/restaurants/json/')
def restaurantsAllJSON():
    restaurants = Restaurant.query.all()
    return jsonify(Restaurants=[r.serialize for r in restaurants])

@app.route('/restaurant/<int:restaurant_id>/menu/json/')
def restaurantJSON(restaurant_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).one()
    return jsonify(restaurant.serialize)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/json/')
def restaurantMenuJSON(restaurant_id, menu_id):
    menu = MenuItem.query.filter_by(id=menu_id).one()
    return jsonify(menu.serialize)

### ERROR CODES

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

### APP

if __name__ == '__main__':
    app.secret_key = 'cUAaQcXRdvsdvs5E8!fF<ad(g0!bYGoz&3XC*'
    app.run(debug=True, host='0.0.0.0', port=5000)

