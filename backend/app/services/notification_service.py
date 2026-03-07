"""
VA-95: Notification Service

Sends email and SMS notifications. Email via SMTP; SMS is a placeholder for future integration.
"""

from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class NotificationService:
    """Send email and SMS notifications."""

    def __init__(self):
        self._email_enabled = bool(
            settings.NOTIFICATIONS_ENABLED
            and settings.SMTP_HOST
            and settings.SMTP_USER
            and settings.SMTP_PASSWORD
        )

    def send_email(
        self,
        to: str | List[str],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
    ) -> bool:
        """Send email via SMTP. Returns True if sent, False if skipped or failed."""
        if not self._email_enabled:
            logger.debug("Email disabled or SMTP not configured, skipping", to=to, subject=subject)
            return False
        recipients = [to] if isinstance(to, str) else to
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM
            msg["To"] = ", ".join(recipients)
            msg.attach(MIMEText(body_text, "plain"))
            if body_html:
                msg.attach(MIMEText(body_html, "html"))
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM, recipients, msg.as_string())
            logger.info("Email sent", to=recipients, subject=subject)
            return True
        except Exception as e:
            logger.error("Email send failed", to=recipients, subject=subject, error=str(e))
            return False

    def send_sms(self, to_phone: str, message: str) -> bool:
        """Placeholder for SMS. Returns False until provider is configured."""
        if not settings.SMS_PROVIDER:
            logger.debug("SMS provider not configured, skipping", to=to_phone)
            return False
        logger.warning("SMS not implemented", to=to_phone, provider=settings.SMS_PROVIDER)
        return False

    # --- Convenience methods for common events ---

    def notify_user_registration_pending(self, email: str, full_name: str) -> bool:
        """Notify user their registration is pending admin approval."""
        subject = "ValuAdis: Registration Pending Approval"
        body = f"""Hello {full_name},

Your ValuAdis account registration has been received and is pending administrator approval.

You will receive an email when your account has been approved. Until then, you will not be able to log in.

If you have questions, please contact your administrator.

— ValuAdis Team
"""
        return self.send_email(email, subject, body)

    def notify_user_approved(self, email: str, full_name: str) -> bool:
        """Notify user their account has been approved."""
        subject = "ValuAdis: Account Approved"
        body = f"""Hello {full_name},

Your ValuAdis account has been approved. You can now log in and start using the platform.

— ValuAdis Team
"""
        return self.send_email(email, subject, body)

    def notify_valuation_completed(
        self, email: str, full_name: str, property_address: str, valuation_id: int
    ) -> bool:
        """Notify user a valuation has been completed."""
        subject = f"ValuAdis: Valuation #{valuation_id} Completed"
        body = f"""Hello {full_name},

Your valuation for the property at {property_address} has been completed.

Log in to ValuAdis to view the details.

— ValuAdis Team
"""
        return self.send_email(email, subject, body)
