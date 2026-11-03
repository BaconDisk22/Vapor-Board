# Access gateway — initial foundation

The `AuthorizedBBS` wrapper requires a server-authenticated `Principal` for all local BBS operations. Staff can create boards; customers must be both approved and age-verified. Sender identities are derived from the principal, not a user-provided sender field. Customer approval and age verification are separate flags.

**Security limitation:** This PR does not implement login, proof-of-age verification, account storage, moderation, sessions, or a secure role assignment process. Do not construct Principal objects from untrusted radio messages or UI inputs. The underlying `BulletinBoard` remains directly callable; integration must restrict its use to this gateway. These flags alone are not legal age verification. No product advertising is implemented.

Run: `python3 -m unittest discover -s tests -v`.

Next: authenticated identity provider, persistent staff-managed approval decisions, audit trail, fail-closed enforcement at every TCP/desktop/API entry point, and moderation. No radio transmissions are added.
