# Desktop status integration

The preview footer now reads from the shared fail-closed StatusSnapshot model. This removes a duplicated hard-coded status string but is **not live telemetry**: it always displays the default disconnected/TX-disabled/MQTT-disabled state. Future work must connect real radio lifecycle events to the UI without misrepresenting a TCP socket as protocol verification.
