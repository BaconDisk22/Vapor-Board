"""Local operator actions for bulletin boards; no network transport."""
from .bbs import BulletinBoard


def create_local_board(database, name):
    return BulletinBoard(database).create_board(name)


def publish_local_post(database, board_id, author, body):
    return BulletinBoard(database).post(board_id, author, body)
