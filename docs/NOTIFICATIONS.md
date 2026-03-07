# ValuAdis Notifications (VA-95)

## Overview

Automated email notifications for key events. SMS is a placeholder for future integration.

## Email (SMTP)

### Configuration

Set in `.env` or environment:

```env
NOTIFICATIONS_ENABLED=true
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=noreply@valuadis.et
SMTP_USE_TLS=true
```

If `NOTIFICATIONS_ENABLED` is false or SMTP is not configured, notifications are skipped (no errors).

### Supported Events

| Event | Recipient | Trigger |
|-------|-----------|---------|
| Registration pending | New user | User registers |
| Account approved | User | Admin approves user |
| Valuation completed | Valuer | (Future) Valuation status → approved |

### Usage

```python
from app.services.notification_service import NotificationService

svc = NotificationService()
svc.notify_user_registration_pending("user@example.com", "User Name")
svc.notify_user_approved("user@example.com", "User Name")
svc.send_email("to@example.com", "Subject", "Body text")
```

## SMS (Placeholder)

Set `SMS_PROVIDER` when integrating an Ethiopian SMS provider (e.g. Ethio Telecom API, Twilio). The `send_sms` method is ready for implementation.
