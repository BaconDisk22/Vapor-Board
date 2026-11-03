"""App-level authorization only; not a substitute for radio key rotation or MQTT ACLs."""
from vapor_board.membership import Role, can_access_private_channel


def can_read(member, channel):
    if not channel or not channel.startswith("private:"):
        return False
    return can_access_private_channel(member)


def can_post(member, channel, *, announcements_only=False):
    if not can_read(member, channel):
        return False
    if announcements_only:
        return member.role in (Role.STAFF, Role.ADMIN)
    return True


def can_moderate(member, channel):
    return can_read(member, channel) and member.role in (Role.STAFF, Role.ADMIN)
