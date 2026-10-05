"""
Background Job Scheduler for Autonomous Operations.
Executes periodic mailbox polling and schedules the end-of-day operational digest.
"""

import logging
import time
from datetime import UTC, datetime

import schedule

from src.api.deps import engine

logger = logging.getLogger(__name__)


def poll_mailbox_job() -> None:
    """Periodic job to pull unread communications and execute autonomous steps."""
    logger.info("Executing periodic mailbox sync...")
    unread_messages = engine.email_service.fetch_unread_messages(limit=20)
    for msg in unread_messages:
        try:
            logger.info("Processing incoming message from %s: %s", msg.sender, msg.subject)
            engine.process_incoming_email(msg)
        except Exception as err:
            logger.error("Failed to process message %s: %s", msg.id, err)


def daily_digest_job() -> None:
    """Scheduled end-of-day job to synthesize metrics and publish Notion digest."""
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    logger.info("Generating scheduled daily digest for %s...", today)
    digest = engine.generate_daily_digest(date_str=today)
    logger.info("Daily digest published successfully: ID %s", digest.id)


def start_scheduler_loop(interval_minutes: int = 5) -> None:
    """Start blocking scheduler loop."""
    logger.info("Starting AI Employee background scheduler...")
    # Schedule inbox polling
    schedule.every(interval_minutes).minutes.do(poll_mailbox_job)

    # Schedule daily digest at 18:00 every day
    schedule.every().day.at("18:00").do(daily_digest_job)

    # Initial poll upon startup
    poll_mailbox_job()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_scheduler_loop()
