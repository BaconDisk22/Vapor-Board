# Board order and pinned posts

## Board order
- The **↑** and **↓** buttons in the Boards card header move the selected board one place; Option-↑ / Option-↓ do the same in the list. The board stays selected.
- New boards go to the end. Boards keep creation order until moved.
- Stored as `boards.position`; `BulletinBoard.move_board(board_id, ±1)` renumbers 1..n and returns False at either end.

## Pinned posts
- **Pin** / **Unpin** (beside Edit) toggles the selected post. Pinned posts sit at the top of their board, most recently pinned first, then everything else newest first.
- Pinned posts show `◆` in the post list and `· Pinned` in the reader; the subtitle reads "pinned first, then newest".
- Stored as `posts.pinned_at`; `BulletinBoard.pin_post(post_id, pinned=True)`. Pinning twice keeps the first pin time.
- The Overview's Recent posts list stays in plain date order.

## Older databases and backups
- Opening a database for writing adds `position` (filled with the old creation order) and `pinned_at` in place, like `read_at` before.
- The read-only reader (`local_operator.inspect_database`) checks which columns exist, so an un-upgraded database still opens.
- Restored older backups are upgraded the same way the first time they are written to.

## Tests
- `tests/test_board_order_pins.py` (engine and upgrade), `tests/test_desktop_board_order_ui.py` (buttons, pin toggle, wording).
