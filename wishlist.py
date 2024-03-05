from flask import Blueprint, render_template, redirect, flash,request, g
from models import db, WishList
from auth import is_user_auth
import requests
from sqlalchemy.exc import IntegrityError


wishlist_bp = Blueprint('whislist', __name__)


@wishlist_bp.route("/add_whislist")
def add_whislist():
    if is_user_auth():
        dealId = request.args.get("dealID")
        savings = request.args.get("savings")
        resp = requests.get(f"https://www.cheapshark.com/api/1.0/deals",params={"id":dealId})

        resJson = resp.json()

        if resJson:
            gameInfo = resJson['gameInfo']
           
            if not savings:
               percentage=  (1-(float(gameInfo['salePrice']))/float(gameInfo['retailPrice']))*100
               formated_value = "{:.2f}".format(percentage)
               savings = formated_value

            try:
                wish =  WishList(user_id=g.user.id,
                                game_id=gameInfo['gameID'],
                                game_title = gameInfo['name'],
                                game_thumb=gameInfo['thumb'],
                                store_id=gameInfo['storeID'],
                                price=gameInfo['salePrice'],
                                sales_price=gameInfo['retailPrice'],
                                savings=savings,
                                deal_id=dealId,
                                meta_critic_score=gameInfo['metacriticScore'],
                                meta_critic_link=gameInfo['metacriticLink'],
                                steam_app_id=gameInfo['steamAppID'],
                                steam_rating_count=gameInfo['steamRatingCount'],
                                steam_rating_percent=gameInfo['steamRatingPercent'],
                                steam_rating_text=gameInfo['steamRatingText'])
                db.session.add(wish)
                db.session.commit()
                flash(f"{wish.game_title} added to Whish List","success")
                return redirect("/")
            except IntegrityError:
                flash(f'This Already added to Whislists',"danger")
                return redirect("/")
        else:
            flash(f"{dealId} is not found")
            return redirect("/")
    else:
        return f"not able soo the game id"
    
@wishlist_bp.route("/wishlist")
def wishlist():
    return render_template("wish_list.html",current_page='/wishlist')


@wishlist_bp.route("/wishlist/remove/<int:game_id>")
def remove_game_wishlist(game_id):
    game = WishList.query.filter_by(game_id=game_id, user_id=g.user.id).first()
    game_name = game.game_title
    if game:
        db.session.delete(game)
        db.session.commit()
        flash(f"{game_name} is deleted","info")
        return redirect("/wishlist")
    else:
        flash("Game is not found or already deleted")
        return redirect("wish_list.html")