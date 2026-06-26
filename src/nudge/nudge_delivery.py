"""Multi-channel nudge delivery: notification, overlay, audio."""

# TODO: Implement full nudge delivery channels


class NudgeDelivery:
    """Delivers nudges through configured channels (notification, overlay, audio)."""

    def deliver(self, message: str, channel: str = "notification") -> bool:
        """Deliver a nudge message through the specified channel.

        Args:
            message: The nudge message text.
            channel: Delivery channel - "notification", "overlay", or "audio".

        Returns:
            True if delivery succeeded.
        """
        # TODO: Implement delivery channels
        raise NotImplementedError
