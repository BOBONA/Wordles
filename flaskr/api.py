import datetime

from flask import Blueprint, jsonify, request, current_app

from flaskr.db import db_session
from flaskr.models import Wordle, IpAddress

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/wordles', methods=['GET'])
def get_wordles():
    wordles = []
    for wordle in Wordle.query.all():
        wordles.append({'id': wordle.id, 'url': wordle.url, 'data': wordle.data, 'likes': wordle.likes, 'date': wordle.date})
    return jsonify(wordles)


@bp.route('/likes', methods=['GET'])
def get_likes():
    ip = get_ip()
    address = IpAddress.query.filter(IpAddress.address == ip).first()
    if address is not None:
        return jsonify(address.likes)
    else:
        return jsonify([])


@bp.route('/like/<wordle>/add', methods=['PUT'])
def like_wordle(wordle):
    ip = get_ip()
    address = IpAddress.query.filter(IpAddress.address == ip).first()
    if address is None:
        limit = current_app.config['ADDRESS_LIMIT']
        count = IpAddress.query.count()
        if count >= limit:
            oldest_address = IpAddress.query.order(IpAddress.date.asc()).limit(1).first()
            db_session.delete(oldest_address)
        address = IpAddress(ip)
        db_session.add(address)
    wordle = Wordle.query.filter(Wordle.id == wordle).first()
    if wordle is None:
        raise Exception('Wordle ID is invalid')
    else:
        if wordle.id in address.likes:
            raise Exception('Address already liked this Wordle ID')
        else:
            likes = list(address.likes)
            likes.append(wordle.id)
            address.likes = likes
            address.date = datetime.datetime.now()
            wordle.likes += 1
            db_session.commit()
            return jsonify(success=True)


@bp.route('/like/<wordle>/remove', methods=['DELETE'])
def unlike_wordle(wordle):
    ip = get_ip()
    address = IpAddress.query.filter(IpAddress.address == ip).first()
    if address is None:
        raise Exception('Address is no longer stored')
    wordle = Wordle.query.filter(Wordle.id == wordle).first()
    if wordle is None:
        raise Exception('Wordle ID is invalid')
    else:
        if wordle.id not in address.likes:
            raise Exception('Address had not liked this Wordle ID')
        else:
            likes = list(address.likes)
            likes.remove(wordle.id)
            address.likes = likes
            address.date = datetime.datetime.now()
            wordle.likes -= 1
            db_session.commit()
            return jsonify(success=True)


def get_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']
