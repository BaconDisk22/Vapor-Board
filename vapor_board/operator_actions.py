"""Local operator actions for bulletin boards; no network transport."""
from .bbs import BulletinBoard


def create_local_board(database, name):
    return BulletinBoard(database).create_board(name)


def publish_local_post(database, board_id, author, body):
    return BulletinBoard(database).post(board_id, author, body)


def edit_local_post(database, post_id, body):
    return BulletinBoard(database).edit_post(post_id, body)


def delete_local_post(database, post_id):
    return BulletinBoard(database).delete_post(post_id)
