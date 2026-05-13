"""Tests for GoF Observer pattern — booking notifications."""
import pytest
from src.services.booking_observer import (
    IBookingObserver,
    LoggingObserver,
    EmailNotificationObserver,
    BookingNotifier,
)


# ── LoggingObserver ───────────────────────────────────────────────────────

class TestLoggingObserver:
    def setup_method(self):
        self.obs = LoggingObserver()

    def test_starts_empty(self):
        assert self.obs.events == []

    def test_on_booking_created_records_event(self):
        self.obs.on_booking_created(1, 2, 3, 300.0)
        assert len(self.obs.events) == 1

    def test_on_booking_created_event_type(self):
        self.obs.on_booking_created(1, 2, 3, 300.0)
        assert self.obs.events[0]["event"] == "created"

    def test_on_booking_created_stores_ids(self):
        self.obs.on_booking_created(7, 8, 9, 150.0)
        ev = self.obs.events[0]
        assert ev["booking_id"] == 7
        assert ev["user_id"] == 8
        assert ev["slot_id"] == 9
        assert ev["total_price"] == pytest.approx(150.0)

    def test_on_booking_cancelled_records_event(self):
        self.obs.on_booking_cancelled(5, 6)
        assert len(self.obs.events) == 1
        assert self.obs.events[0]["event"] == "cancelled"

    def test_on_booking_cancelled_stores_ids(self):
        self.obs.on_booking_cancelled(5, 6)
        ev = self.obs.events[0]
        assert ev["booking_id"] == 5
        assert ev["user_id"] == 6

    def test_on_booking_confirmed_records_event(self):
        self.obs.on_booking_confirmed(10, 20)
        assert self.obs.events[0]["event"] == "confirmed"

    def test_on_booking_confirmed_stores_ids(self):
        self.obs.on_booking_confirmed(10, 20)
        assert self.obs.events[0]["booking_id"] == 10
        assert self.obs.events[0]["user_id"] == 20

    def test_multiple_events_accumulate(self):
        self.obs.on_booking_created(1, 1, 1, 100.0)
        self.obs.on_booking_cancelled(1, 1)
        self.obs.on_booking_confirmed(1, 1)
        assert len(self.obs.events) == 3

    def test_implements_interface(self):
        assert isinstance(self.obs, IBookingObserver)


# ── EmailNotificationObserver ─────────────────────────────────────────────

class TestEmailNotificationObserver:
    def setup_method(self):
        self.obs = EmailNotificationObserver()

    def test_starts_empty(self):
        assert self.obs.sent_notifications == []

    def test_on_booking_created_stores_confirmation(self):
        self.obs.on_booking_created(1, 2, 3, 300.0)
        notif = self.obs.sent_notifications[0]
        assert notif["type"] == "booking_confirmation"
        assert notif["booking_id"] == 1
        assert notif["user_id"] == 2
        assert notif["total_price"] == pytest.approx(300.0)

    def test_on_booking_cancelled_stores_cancellation(self):
        self.obs.on_booking_cancelled(3, 4)
        notif = self.obs.sent_notifications[0]
        assert notif["type"] == "booking_cancellation"
        assert notif["booking_id"] == 3

    def test_on_booking_confirmed_stores_payment(self):
        self.obs.on_booking_confirmed(5, 6)
        notif = self.obs.sent_notifications[0]
        assert notif["type"] == "payment_confirmed"

    def test_implements_interface(self):
        assert isinstance(self.obs, IBookingObserver)

    def test_multiple_notifications_accumulate(self):
        self.obs.on_booking_created(1, 1, 1, 100.0)
        self.obs.on_booking_confirmed(1, 1)
        assert len(self.obs.sent_notifications) == 2


# ── BookingNotifier ───────────────────────────────────────────────────────

class TestBookingNotifier:
    def setup_method(self):
        self.notifier = BookingNotifier()
        self.obs1 = LoggingObserver()
        self.obs2 = LoggingObserver()

    def test_starts_with_no_observers(self):
        assert self.notifier.get_observers() == []

    def test_subscribe_adds_observer(self):
        self.notifier.subscribe(self.obs1)
        assert len(self.notifier.get_observers()) == 1

    def test_subscribe_same_observer_once(self):
        self.notifier.subscribe(self.obs1)
        self.notifier.subscribe(self.obs1)
        assert len(self.notifier.get_observers()) == 1

    def test_subscribe_multiple_observers(self):
        self.notifier.subscribe(self.obs1)
        self.notifier.subscribe(self.obs2)
        assert len(self.notifier.get_observers()) == 2

    def test_unsubscribe_removes_observer(self):
        self.notifier.subscribe(self.obs1)
        self.notifier.unsubscribe(self.obs1)
        assert len(self.notifier.get_observers()) == 0

    def test_unsubscribe_nonexistent_does_not_raise(self):
        self.notifier.unsubscribe(self.obs1)  # not subscribed

    def test_notify_created_reaches_all_observers(self):
        self.notifier.subscribe(self.obs1)
        self.notifier.subscribe(self.obs2)
        self.notifier.notify_booking_created(1, 2, 3, 300.0)
        assert len(self.obs1.events) == 1
        assert len(self.obs2.events) == 1

    def test_notify_cancelled_reaches_all_observers(self):
        self.notifier.subscribe(self.obs1)
        self.notifier.subscribe(self.obs2)
        self.notifier.notify_booking_cancelled(1, 2)
        assert self.obs1.events[0]["event"] == "cancelled"
        assert self.obs2.events[0]["event"] == "cancelled"

    def test_notify_confirmed_reaches_all_observers(self):
        self.notifier.subscribe(self.obs1)
        self.notifier.subscribe(self.obs2)
        self.notifier.notify_booking_confirmed(1, 2)
        assert self.obs1.events[0]["event"] == "confirmed"
        assert self.obs2.events[0]["event"] == "confirmed"

    def test_notify_with_no_observers_no_error(self):
        self.notifier.notify_booking_created(1, 2, 3, 100.0)
        self.notifier.notify_booking_cancelled(1, 2)
        self.notifier.notify_booking_confirmed(1, 2)

    def test_after_unsubscribe_no_notification(self):
        self.notifier.subscribe(self.obs1)
        self.notifier.unsubscribe(self.obs1)
        self.notifier.notify_booking_created(1, 2, 3, 100.0)
        assert len(self.obs1.events) == 0

    def test_mixed_observer_types(self):
        email_obs = EmailNotificationObserver()
        self.notifier.subscribe(self.obs1)
        self.notifier.subscribe(email_obs)
        self.notifier.notify_booking_created(1, 2, 3, 200.0)
        assert len(self.obs1.events) == 1
        assert len(email_obs.sent_notifications) == 1
