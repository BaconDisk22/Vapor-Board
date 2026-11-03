# Vapor Board

A single-shop-at-a-time, shop-branded communications and bulletin-board project.

## Project direction

Vapor Board is a separate project inspired by the engineering work on [THE SITDOWN BBS](https://github.com/BaconDisk22/The-Sitdown-BBS). The original remains independent and unchanged.

Initial scope:
- Shop-controlled bulletin board for general store information, operating hours, closures, and notices.
- Staff/operator and customer roles, moderation, opt-in notifications, and basic customer discussions.
- Desktop application with demo mode and optional Meshtastic TCP connectivity.
- Optional MQTT monitoring, disabled by default, with no automatic bridging or outbound transmissions.
- A future configurable shop name, colors, and branding for one shop per installation.

## Safety and compliance

Age-restricted product promotions are not part of the initial release. Any advertising features must undergo applicable legal review, including age-access controls, required health warnings, and local rules. No automatic broadcast of product promotions. Customer messaging must be opt-in, privacy-conscious, and moderated.

## Migration approach

Reuse selected open-source BBS modules, tests, and packaging only after reviewing source licenses, attribution, and dependencies. Maintain upstream credits. No existing radio/MQTT credentials, private customer data, or device-specific configuration should be copied.

## Status

**Planning / repository initialization.** This README is not a completed port or runnable application. See the upcoming migration PRs for implementation.
