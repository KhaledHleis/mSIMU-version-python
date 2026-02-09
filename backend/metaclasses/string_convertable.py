class StringConvertible:
    """
    Mixin that provides a default string representation
    for any inheriting class.
    """

    def __str__(self) -> str:
        attrs = ", ".join(
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
        )
        return f"{self.__class__.__name__}({attrs})"

    def __repr__(self) -> str:
        return self.__str__()