"""Engagement state machine with hysteresis."""

from enum import Enum


class EngagementState(str, Enum):
    ENGAGED = "engaged"
    PASSIVE = "passive"
    DISTRACTED = "distracted"
    DROWSY = "drowsy"
    CONFUSED = "confused"


class EngagementStateMachine:
    """Finite state machine for engagement states with temporal hysteresis."""

    def __init__(self):
        self.current_state = EngagementState.ENGAGED
        self._state_start = None
        self._pending_state = None
        self._pending_start = None

    def update(
        self, score: float, is_drowsy: bool, is_confused: bool, timestamp: float
    ) -> EngagementState:
        """Update state machine with new engagement score.

        Returns:
            Current engagement state after applying hysteresis.
        """
        # TODO: Implement state transitions with duration thresholds
        raise NotImplementedError
