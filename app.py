import os
from flask import Flask, render_template,request,jsonify
from models import db,connect_db,WishList,Notification
from auth import auth_bp,add_user_to_global,is_user_auth
from wishlist import wishlist_bp
from notification import notification_bp
from config import SQLALCHEMY_DATABASE_URI,SECRET_KEY
from sqlalchemy.exc import IntegrityError
import requests
import schedule
import threading
from sqlalchemy.exc import IntegrityError
import json

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

with app.app_context():
    connect_db(app)
    db.create_all()

app.register_blueprint(auth_bp)
app.register_blueprint(wishlist_bp)
app.register_blueprint(notification_bp)

@app.before_request
def before_request():
    add_user_to_global()

@app.template_filter('has_unread_notification')
def has_unread_notification(notifications):
    return any(notify.is_read==False for notify in notifications)

@app.template_filter('get_store_name')
def get_store_name(storeID):
    stores = show_store()

    return next((store['storeName'] for store in stores if storeID == store['storeID']), None)

@app.template_filter('get_store_icon')
def get_store_icon(storeID):
    stores = show_store()
    icon= next((store['images']['icon']for store in stores if storeID == store['storeID']), None)
    return f"https://www.cheapshark.com/{icon}"

@app.route("/stores")
def show_store():
    file_path = os.path.join(app.static_folder, 'data', "stores.json")
    with open(file_path,"r") as file:
        data =json.load(file)
    return data
    
@app.route("/")
def show_index():
    resp = requests.get("https://www.cheapshark.com/api/1.0/deals?pageSize=60&pageNumber=0")
    return render_template('index.html',deals=resp.json())

@app.route("/search")
def search():
    query = request.args.get('search')
    resp  = requests.get(f"https://www.cheapshark.com/api/1.0/games?title={query}&limit=60")
    data = resp.json()
    return render_template("search.html",data=data)

@app.route("/load_more")
def load_more():   
    page_number = request.args.get('page', default=0, type=int)
    resp = requests.get(f"https://www.cheapshark.com/api/1.0/deals?pageSize=60&pageNumber={page_number}")
    data = resp.json()
    next_page = page_number + 1
    return jsonify(data=data, nextPage=next_page)

@app.route("/gameInfo/<int:game_id>")
def game_info(game_id):
    resp = requests.get(f"https://www.cheapshark.com/api/1.0/games?id={game_id}")
    data = resp.json()
    return jsonify(data)
    
def check_price():
    with app.app_context():
        try: 
            games = WishList.query.all()
            cheapest_prices = {}

            for game in games:
                resp = requests.get(f"https://www.cheapshark.com/api/1.0/games?id={game.game_id}")
                data = resp.json()

                # Check if 'deals' key exists in the response data
                if 'deals' in data:
                    deals = data['deals']
                else:
                    print(f"No 'deals' key found in response data for game {game.game_id}")
                    continue

                cheapest_price_from_deals = game.price
                cheapest_store_id_from_deals = None

                for deal in deals:
                    price = float(deal['price'])

                    if price < cheapest_price_from_deals:
                        cheapest_price_from_deals = price
                        cheapest_store_id_from_deals = deal['storeID']

                if cheapest_store_id_from_deals is not None and game.store_id != int(cheapest_store_id_from_deals):

                    store_name = get_store_name(cheapest_store_id_from_deals)
                    
                    content = f"We have found that {game.game_title} in your wishlist is has become at a better price of ${cheapest_price_from_deals} on the store {store_name}."
                    
                    try:
                        notify  = Notification(user_id=game.user_id,
                                            content=content,
                                            game_id=game.game_id,
                                            store_id=int(cheapest_store_id_from_deals),
                                            price=float(cheapest_price_from_deals),
                                            )
                        db.session.add(notify)
                        db.session.commit()
                    except IntegrityError as e:
                        db.session.rollback()
                        print("Failed to insert notification due to unique constraint violation.")
      
                    #testing purpose it will be removed after deployed
                    cheapest_prices[game.game_id] = {
                    'cheapest_price': cheapest_price_from_deals,
                    'cheapest_store_id': cheapest_store_id_from_deals,
                    'current_price': game.price,
                    'current_store': game.store_id
                }
            db.session.commit()
            print("notifications are pushedc")
            return jsonify(cheapest_prices)
        except Exception as e:
            print(f"Error in check_price: {e}")

#testing purpose it will be removed after deployed
@app.route("/trigger-check")
def trigger_check():
    return check_price()

schedule.every().day.at("00:00").do(check_price)


# Function to run Flask app in a separate thread
def run_flask_app():
       app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Main loop for scheduler and printing
    while True:
        schedule.run_pending()