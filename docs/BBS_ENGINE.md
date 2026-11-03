# Local BBS engine (Phase 2)

This initial implementation provides persistent SQLite boards, posts and private mail plus read-only commands. It has **no radio connection, network listener, transport, authentication, or access-control integration**. It must not be exposed to untrusted clients before the authorization layer is complete. Do not treat sender/recipient strings as verified identities.

Run: `python3 -m unittest discover -s tests -v`

Example:

```python
from vapor_board.bbs import BulletinBoard
bbs = BulletinBoard("local.sqlite")
board_id = bbs.create_board("Notices")
bbs.post(board_id, "operator", "Welcome")
print(bbs.command("operator", "/boards"))
```

Next integration steps: enforce staff/customer permissions and approved customer identities, introduce moderation, review upstream licenses and attribution before copying any Sitdown BBS modules, then attach optional Meshtastic TCP with outbound transmissions disabled by default. No Sitdown BBS source files or credentials are copied in this PR.
