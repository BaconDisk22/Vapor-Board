"""Private shop membership gate. No self-approval or ID document storage."""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class Role(str, Enum):
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"


@dataclass(frozen=True)
class Member:
    member_id: str
    role: Role = Role.CUSTOMER
    verified_21_plus: bool = False
    verified_by: str = ""
    verified_at: str = ""
    active: bool = False


def approve_customer(member: Member, *, approver: Member, verified_in_person: bool) -> Member:
    """Only an active admin may record an in-person 21+ verification."""
    if not approver.active or approver.role is not Role.ADMIN:
        raise PermissionError("Active shop admin approval required")
    if not verified_in_person:
        raise PermissionError("Shop must verify 21+ before approval")
    if member.role is not Role.CUSTOMER or not member.member_id:
        raise ValueError("Only identified customer accounts can be approved")
    return Member(member.member_id, member.role, True, approver.member_id,
                  datetime.now(timezone.utc).isoformat(), True)


def can_access_private_channel(member: Member) -> bool:
    return bool(member.active and member.verified_21_plus and member.verified_by and member.verified_at)


def revoke(member: Member) -> Member:
    return Member(member.member_id, member.role, member.verified_21_plus,
                  member.verified_by, member.verified_at, False)
