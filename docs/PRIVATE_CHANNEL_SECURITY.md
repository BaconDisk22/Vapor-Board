# Private shop channels: security requirements

Vapor Board is a **single-shop-at-a-time** system. Private customer membership is **shop-approved, 21+ only**, and never self-approved.

## Membership
- Shop verifies age and identity using an appropriate lawful process before approving access.
- Store only minimum verification metadata (approved by/when/status); do not store identity-document scans by default.
- Only active, authorized administrators may approve customers. Staff moderation does not imply approval rights.
- Revocation blocks application access immediately and is audited.

## Transport boundaries
- **Meshtastic:** app membership checks alone cannot revoke a radio that already has a channel key. Implement a documented key-rotation and redistribution process when membership changes. Never claim absolute privacy or end-to-end confidentiality without validating channel/key settings.
- **MQTT:** require broker-side authentication and per-shop ACLs. No shared public subscription topics for private customer content.
- No automatic bridge from MQTT to radio, across shops, or across networks.
- Demo mode cannot transmit, publish, or contact a real broker.
- No automatic broadcasts. Consent and operator approval are mandatory.

## Launch gates
- Threat-model stolen devices, lost keys, removed members, shared accounts, and credential leaks.
- Test access denial, membership expiry/revocation, transport ACLs, and key rotation with real hardware.
- General store/customer service communication first. Age-restricted product advertising remains gated on applicable legal/compliance review; age verification alone does not create an exemption.
- Document privacy, retention, and notification consent before customer rollout.

## Limitations of current code
The membership and channel-policy modules are local, in-memory building blocks. They do not yet provide persistent accounts, cryptographic identity, secure authentication, encrypted storage, or actual radio/MQTT channel enforcement.
