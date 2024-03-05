from flask import Blueprint, render_template, redirect, flash, g
from models import db, Notification
from auth import is_user_auth
from datetime import datetime

notification_bp = Blueprint('notification',__name__)

@notification_bp.route("/notifications")
def show_notifications():
    if is_user_auth():
        notifications  = Notification.query.filter(Notification.user_id==g.user.id)

        return render_template("notifications.html",notifications=notifications,current_page="/notifications")
    
@notification_bp.route("/notifications/mark/<int:not_id>")
def mark_notifications(not_id):
    if is_user_auth():
        notification  = Notification.query.filter(Notification.user_id==g.user.id,
                                                   Notification.id==not_id).first()
        
        if notification:
            if notification.is_read:
                notification.is_read = False
                notification.read_at = datetime.utcnow()
            else:
                notification.is_read = True
                notification.read_at = datetime.utcnow()

            db.session.commit()
            return redirect("/notifications")
        else:
            flash(f"{not_id} is not found", "danger")
            return redirect("notifications.html")
    else:
        flash("UnAuthorized User","danger")
        return redirect("/")

@notification_bp.route("/notifications/delete/<int:not_id>")
def delete_notifications(not_id):
    if is_user_auth():
        notification  = Notification.query.filter(Notification.user_id==g.user.id,
                                                   Notification.id==not_id).first()
        
        if notification:
            db.session.delete(notification)
            db.session.commit()
            
            flash(f"Selected Notification is deleted", "info")
            return redirect("/notifications")
       
        else:
            flash(f"{not_id} is not found", "danger")
            return redirect("notifications.html")
    else:
        flash("UnAuthorized User","danger")
        return redirect("/")