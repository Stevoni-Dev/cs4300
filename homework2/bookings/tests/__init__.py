"""Shared test helpers for the bookings app."""


def tag(name):
    """Attach a lightweight classification to Django tests.

    The project uses the `@tag("unit")` / `@tag("integration")` convention from
    the task specification rather than a pytest dependency.
    """

    def decorator(obj):
        tags = list(getattr(obj, "tags", []))
        if name not in tags:
            tags.append(name)
        obj.tags = tags
        return obj

    return decorator


__all__ = ["tag"]
