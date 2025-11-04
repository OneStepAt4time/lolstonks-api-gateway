"""
API Key Rotation for load distribution across multiple Riot API keys.

Provides round-robin rotation to distribute requests evenly across
available API keys, helping avoid rate limit exhaustion on a single key.
"""

import threading
from loguru import logger


class KeyRotator:
    """
    Thread-safe round-robin key rotator for Riot API keys.

    Distributes API requests across multiple keys to better manage
    rate limits and provide redundancy.

    Example:
        >>> rotator = KeyRotator(["key1", "key2", "key3"])
        >>> key = rotator.get_next_key()
        >>> # Returns "key1", next call returns "key2", etc.
    """

    def __init__(self, api_keys: list[str]):
        """
        Initialize the key rotator.

        Args:
            api_keys: List of Riot API keys to rotate through

        Raises:
            ValueError: If api_keys list is empty
        """
        if not api_keys:
            raise ValueError("KeyRotator requires at least one API key")

        self.api_keys = api_keys
        self._current_index = 0
        self._lock = threading.Lock()

        key_count = len(api_keys)
        logger.info(
            f"Key rotator initialized with {key_count} API key{'s' if key_count > 1 else ''}"
        )

    def get_next_key(self) -> str:
        """
        Get the next API key in round-robin rotation.

        Thread-safe method that returns keys in a circular fashion.

        Returns:
            str: The next API key to use

        Example:
            >>> rotator = KeyRotator(["key1", "key2"])
            >>> rotator.get_next_key()  # Returns "key1"
            >>> rotator.get_next_key()  # Returns "key2"
            >>> rotator.get_next_key()  # Returns "key1" (wraps around)
        """
        with self._lock:
            key = self.api_keys[self._current_index]
            self._current_index = (self._current_index + 1) % len(self.api_keys)

            # Mask key for logging (show first 10 chars only)
            masked_key = f"{key[:15]}..." if len(key) > 15 else key
            logger.debug(f"Selected API key: {masked_key}")

            return key

    def get_key_count(self) -> int:
        """
        Get the total number of keys available for rotation.

        Returns:
            int: Number of API keys
        """
        return len(self.api_keys)

    def reset(self) -> None:
        """
        Reset rotation to start from the first key.

        Useful for testing or when you want to restart rotation.
        """
        with self._lock:
            self._current_index = 0
            logger.debug("Key rotation reset to first key")
