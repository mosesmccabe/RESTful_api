import json

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Cafe {self.name}>'


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route('/random', methods=['GET'])
def random_cafe():
    # Because our server is now acting as an API, we want to return a JSON containing the necessary data.
    with app.app_context():
        all_cafes = db.session.query(Cafe).all()
        # Read a single random data for all_cafes
        rand_cafe = random.choice(all_cafes)
        cafe_list = {
            # Optional: Omit the id from the response
            # "id": rand_cafe.id,
            "name": rand_cafe.name,
            "map_url": rand_cafe.map_url,
            "img_url": rand_cafe.img_url,
            "location": rand_cafe.location,
            "seats": rand_cafe.seats,
            "coffee_price": rand_cafe.coffee_price,

            # Optional: Group the Boolean properties into a subsection called amenities
            "amenities": {
                "has_toilet": rand_cafe.has_toilet,
                "has_wifi": rand_cafe.has_wifi,
                "has_sockets": rand_cafe.has_sockets,
                "can_take_calls": rand_cafe.can_take_calls
            }
        }
    return jsonify(cafe_list)


@app.route('/all')
def all():
    all_cafes_list = []
    # fitch all the data a response
    with app.app_context():
        all_cafes = db.session.query(Cafe).all()
        for cafe in all_cafes:
            cafe_dic = {
                # Optional: Omit the id from the response
                # "id": rand_cafe.id,
                "name": cafe.name,
                "map_url": cafe.map_url,
                "img_url": cafe.img_url,
                "location": cafe.location,
                "seats": cafe.seats,
                "coffee_price": cafe.coffee_price,

                # Optional: Group the Boolean properties into a subsection called amenities
                "amenities": {
                    "has_toilet": cafe.has_toilet,
                    "has_wifi": cafe.has_wifi,
                    "has_sockets": cafe.has_sockets,
                    "can_take_calls": cafe.can_take_calls
                }
            }
            all_cafes_list.append(cafe_dic)

    return jsonify(all_cafes_list)


@app.route('/search')
def search():
    location = request.args.get("loc")  # get loc value for /search?loc=Peckham
    with app.app_context():
        find_by_location = db.session.execute(db.select(Cafe).where(Cafe.location == location)).scalar()
        if not find_by_location:
            cafe_list = {
                "error": {
                    "Not found": "Sorry we don't have a cafe at the location."
                }
            }
        else:
            cafe_list = {
                # Optional: Omit the id from the response
                # "id": rand_cafe.id,
                "name": find_by_location.name,
                "map_url": find_by_location.map_url,
                "img_url": find_by_location.img_url,
                "location": find_by_location.location,
                "seats": find_by_location.seats,
                "coffee_price": find_by_location.coffee_price,

                # Optional: Group the Boolean properties into a subsection called amenities
                "amenities": {
                    "has_toilet": find_by_location.has_toilet,
                    "has_wifi": find_by_location.has_wifi,
                    "has_sockets": find_by_location.has_sockets,
                    "can_take_calls": find_by_location.can_take_calls
                }
            }

    return jsonify(cafe_list)


## HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add():
    data = request.form
    with app.app_context():
        new_cafe = Cafe(name=data['name'],
                        map_url=data['map_url'],
                        img_url=data["img_url"],
                        location=data["location"],
                        seats=data['seats'],
                        has_toilet=json.loads(data['has_toilet'].lower()),
                        has_wifi=json.loads(data['has_wifi'].lower()),
                        has_sockets=json.loads(data["has_sockets"].lower()),
                        can_take_calls=json.loads(data["can_take_calls"].lower()),
                        coffee_price=data["coffee_price"])

        db.session.add(new_cafe)  # add record to database
        db.session.commit()  # commit add request

    return jsonify(response={"success": "Successfully add new data"})


## HTTP PUT/PATCH - Update Record

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    cafe_find_by_id = db.session.query(Cafe).get(cafe_id)
    if cafe_find_by_id:
        cafe_find_by_id.coffee_price = request.args.get("coffee_price")
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}),200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}),404

    # update price field


## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=['DELETE'])
def delete(cafe_id):
    cafe_to_be_deleted = db.session.query(Cafe).get(cafe_id)
    if cafe_to_be_deleted and request.args.get("api-key") == "TopSecretAPIKey":
        db.session.delete(cafe_to_be_deleted)
        db.session.commit()
        return jsonify(response={"success": "Cafe successfully deleted."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry that's not allow. make sure you have the correct api-key."}), 404




if __name__ == '__main__':
    app.run(debug=True)
