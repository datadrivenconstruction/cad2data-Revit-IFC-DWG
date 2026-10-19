"""Optional desktop adapter. Conversion and CLI paths never open a browser here."""
import webbrowser
import time

from . import community
from .presentation import local_community_page


class CommunityUI:
    """Full-featured Community accounting; not a paid-license enforcement boundary."""

    def __init__(self, product_id, *, db_path=None, coordinator=None):
        if product_id not in community.PRODUCT_IDS:
            raise ValueError("Unknown product")
        self.product_id = product_id
        self.db_path = db_path
        if coordinator is not None and (
            getattr(coordinator, "product_id", None) != product_id
            or not callable(getattr(coordinator, "get_access", None))
        ):
            raise ValueError("A coordinator for the exact product is required")
        self._coordinator = coordinator

    def _paid(self):
        """Use a fresh local verification, never a cached presentation flag.

        This dependency is supplied by trusted host code, not a command-line
        switch or configuration boolean. It must implement LicenseCoordinator's
        verification contract. Unavailable verification means full Community.
        """
        if self._coordinator is None:
            return False
        try:
            access = self._coordinator.get_access(self.product_id)
            return (access.paid is True
                    and access.entitlement.product == self.product_id)
        except Exception:
            return False

    def accepted(self, operation_id):
        """Caller must have validated conversion acceptance before calling this."""
        paid = self._paid()
        result = community.record_completed(self.product_id, operation_id,
                                            ad_free=paid, db_path=self.db_path)
        result["edition"] = "paid" if paid else "community"
        result["ad_pending"] = (not paid and community.has_pending(
            product_id=self.product_id, db_path=self.db_path))
        return result

    def launch_one_pending(self, *, opener=None):
        """Explicit desktop action; use a background UI worker, never parser threads.

        An opener's success means launch was accepted, not that a user viewed the
        page. Crashes between external launch and ack can cause a repeated launch.
        No failures may be mapped to failed conversion or removal of its output.
        """
        if self._paid():
            return {"status": "nothing_pending", "edition": "paid"}
        event = community.claim_pending(product_id=self.product_id, db_path=self.db_path)
        if event is None:
            pending = community.list_pending(product_id=self.product_id, db_path=self.db_path)
            if not pending:
                return {"status": "nothing_pending"}
            # An existing process may hold an unexpired lease. Tell a desktop
            # adapter when to retry instead of making it poll or abandon the
            # durable event until another conversion happens.
            unclaimed = [row for row in pending if row["status"] == "pending"]
            if unclaimed:
                delay = 0.1
            else:
                expiries = [row["lease_until"] for row in pending if row["lease_until"] is not None]
                delay = max(0.1, min(60.0, min(expiries) - time.time())) if expiries else 1.0
            return {"status": "busy_lease", "retry_after_seconds": delay}
        opener = opener or (lambda url: webbrowser.open(url, new=2))
        try:
            target = local_community_page()
            # Activation can finish while SQLite waits for a claim. Check again
            # at dispatch; preserve the event for any later Community session.
            # A page already handed to the browser cannot be recalled.
            if self._paid():
                community.release_claim(event["event_id"], event["lease_token"], db_path=self.db_path)
                return {"status": "nothing_pending", "edition": "paid"}
            if not opener(target):
                community.release_claim(event["event_id"], event["lease_token"], db_path=self.db_path)
                return {"status": "launch_failed", "event_id": event["event_id"]}
            ack = community.acknowledge_launch_attempt(event["event_id"], event["lease_token"], db_path=self.db_path)
            return {"status": "launch_requested" if ack else "ack_lost", "event_id": event["event_id"]}
        except Exception:
            community.release_claim(event["event_id"], event["lease_token"], db_path=self.db_path)
            return {"status": "launch_failed", "event_id": event["event_id"]}
