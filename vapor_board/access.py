"""Local, explicit authorization gateway. Caller must supply authenticated identities."""
from dataclasses import dataclass
from enum import Enum
from .bbs import BulletinBoard


class Role(str, Enum):
    STAFF = "staff"
    CUSTOMER = "customer"


@dataclass(frozen=True)
class Principal:
    identity: str
    role: Role
    age_verified: bool = False
    approved: bool = False

    def __post_init__(self):
        if not isinstance(self.identity, str) or not self.identity.strip() or len(self.identity) > 80:
            raise ValueError("invalid identity")
        if not isinstance(self.role, Role):
            raise ValueError("invalid role")
        if type(self.age_verified) is not bool or type(self.approved) is not bool:
            raise ValueError("invalid verification flags")


class AccessDenied(PermissionError):
    pass


class AuthorizedBBS:
    """Only call with server-authenticated Principal objects, never user-supplied claims."""
    def __init__(self, board: BulletinBoard):
        self._board = board

    @staticmethod
    def _require(principal, staff=False):
        if not isinstance(principal, Principal):
            raise AccessDenied("authenticated identity required")
        if principal.role == Role.STAFF:
            return
        if staff or not principal.approved or not principal.age_verified:
            raise AccessDenied("staff or approved, age-verified customer required")

    def create_board(self, principal, name):
        self._require(principal, staff=True)
        return self._board.create_board(name)

    def list_boards(self, principal):
        self._require(principal)
        return self._board.list_boards()

    def post(self, principal, board_id, body):
        self._require(principal)
        return self._board.post(board_id, principal.identity, body)

    def list_posts(self, principal, board_id, limit=50):
        self._require(principal)
        return self._board.list_posts(board_id, limit)

    def send_mail(self, principal, recipient, body):
        self._require(principal)
        return self._board.send_mail(principal.identity, recipient, body)

    def inbox(self, principal, limit=50):
        self._require(principal)
        return self._board.inbox(principal.identity, limit)

    def command(self, principal, command):
        self._require(principal)
        return self._board.command(principal.identity, command)
