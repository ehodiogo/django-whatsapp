from django.dispatch import Signal

# Sent when a new contact is created
# Arguments: contact (WhatsAppContact), created (bool)
contact_created = Signal()

# Sent when a contact is updated
# Arguments: contact (WhatsAppContact)
contact_updated = Signal()

# Sent when an inbound message is received
# Arguments: message (WhatsAppMessage), contact (WhatsAppContact), raw_event (MessageReceived)
message_received = Signal()

# Sent when an outbound message is sent
# Arguments: message (WhatsAppMessage), contact (WhatsAppContact)
message_sent = Signal()

# Sent when a message status changes (e.g. sent, delivered, read, failed)
# Arguments: message (WhatsAppMessage), status (str), previous_status (str), raw_event (MessageStatusUpdated)
message_status_updated = Signal()
