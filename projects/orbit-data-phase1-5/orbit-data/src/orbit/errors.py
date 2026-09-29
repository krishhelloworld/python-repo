class OrbitError(Exception):
    pass


class ReproducibilityError(OrbitError):
    """Same identity (seed + versions) produced different content."""
