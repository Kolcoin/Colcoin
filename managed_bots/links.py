"""Helpers for generating Telegram Managed Bot creation links."""

from urllib.parse import quote


def generate_bot_creation_link(
    management_bot_username: str,
    desired_bot_username: str,
    desired_bot_name: str,
) -> str:
    """Build a t.me/newbot link for a managed bot.

    Raises:
        ValueError: If any parameter is empty.
    """
    for name, value in (
        ("management_bot_username", management_bot_username),
        ("desired_bot_username", desired_bot_username),
        ("desired_bot_name", desired_bot_name),
    ):
        if not value or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    clean_mgmt_username = management_bot_username.strip().lstrip("@")
    clean_desired_username = desired_bot_username.strip().lstrip("@")

    return (
        f"https://t.me/newbot/{clean_mgmt_username}/{clean_desired_username}"
        f"?name={quote(desired_bot_name.strip())}"
    )


def create_customer_bot_link(
    customer_name: str,
    customer_id: int,
    management_bot_username: str,
) -> str:
    """Generate a deterministic managed bot link for a customer."""
    username = f"pleada_ai_customer_{customer_id}".lower()
    display_name = f"PLEADA AI - {customer_name.strip()}"
    return generate_bot_creation_link(
        management_bot_username=management_bot_username,
        desired_bot_username=username,
        desired_bot_name=display_name,
    )
