# Local operator inspection

Run `python3 -m vapor_board.local_operator /path/to/existing/bbs.sqlite` to list boards, or add `--board 1` to list recent posts. This is a local diagnostic tool for an operator with filesystem access; it is not a customer API, authenticated session, or a secure access boundary. Do not expose private databases to untrusted users. No radio networking or outbound transmissions occur.
