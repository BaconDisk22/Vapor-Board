# Message threads

The Messages page opens on **Threads**: one row per person the operator mailbox has written to or heard from, newest conversation first. **Inbox** and **Sent** still list single messages as before.

## Threads list
- Row: `●  name (unread) — preview`. The dot, bold text and count appear only while that person has unread messages; `You:` marks a conversation where the operator wrote last.
- Opening a thread shows every message between the two, oldest at the top, newest at the bottom (scrolled into view), each headed `name · time` (`You` for the operator).
- Opening a thread marks all of that person's messages to the operator as read. Other mailboxes are never touched.
- **Reply** fills in the person's name. After sending, the view stays in the conversation and shows the new message.

## Engine (`vapor_board/bbs.py`)
- `conversations(user, limit=50)`: other, last_body, last_at, last_from_user, unread, total.
- `conversation(user, other, limit=100)`: the latest messages between the two, oldest first.
- `mark_conversation_read(user, other)`: returns how many were newly marked.
- No schema change; existing databases and backups work as they are.

## Tests
- `tests/test_conversations.py` (engine), `tests/test_desktop_messages_ui.py` (threads view, reply-in-thread, Inbox/Sent unchanged).

## Not yet verified
- Very long conversations: the thread shows the latest 100 messages.
- Names are matched exactly, so "Sam" and "sam" are separate conversations.
