"""Module for storing the jump types for GOTO command."""


class JumpType:
    _target: str

    def __init__(self, target: str):
        """
        Initialize JumpType instance.

        Args:
            value (str): raw argument value to store
        """
        self._target = target

    @property
    def target(self):
        """
        Raw jump's target.

        Returns:
            target for GOTO command
        """
        return self._target

    def __repr__(self):
        """
        Get a string representation of JumpType instance.

        Returns:
            string representation
        """
        return f"<JumpType: {self._target!r}>"

    def __eq__(self, other):
        """
        Check if two JumpType instances have the same content.

        Args:
            other (Any): target to compare current instance with

        Returns:
            boolean for content equality
        """
        if not isinstance(other, JumpType):
            return False
        # GOTO ignores case-sensitivity
        return self.target.lower() == other.target.lower()


class JumpTypeEof(JumpType):
    _target: str = ":eof"

    def __init__(self):
        """
        Initialize JumpTypeEof instance.
        """
        super().__init__(target=self._target)
