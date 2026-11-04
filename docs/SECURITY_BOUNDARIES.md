# Security boundary audit checklist

These tests assert existing guardrails: customer access requires both approval and age verification, customers cannot create boards, receive-only TCP cannot send, and default radio state is unverified and TX disabled.

**Not yet secure for public customer access:** Principal is a plain data class; callers can construct fake staff or approved identities. No trusted login/session layer or independent age-verification provider is implemented. Never expose AuthorizedBBS directly to untrusted network clients. Treat all current desktop BBS browsing as trusted local operator functionality only.
