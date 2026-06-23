"""
ops-bot, a small Matrix automation bot for the self-hosted stack.

Listens in a Matrix room; when a user types `!ticket <subject> | <body>`,
it opens a request in Zammad via the REST API and replies with the number.
One example of the custom automation glue that ties the stack together.
"""
import asyncio
import os

import httpx
from nio import AsyncClient, MatrixRoom, RoomMessageText

MATRIX_HOMESERVER = os.environ["MATRIX_HOMESERVER"]
MATRIX_USER = os.environ["MATRIX_USER"]
MATRIX_PASSWORD = os.environ["MATRIX_PASSWORD"]
ZAMMAD_URL = os.environ["ZAMMAD_URL"].rstrip("/")
ZAMMAD_TOKEN = os.environ["ZAMMAD_TOKEN"]
DEFAULT_GROUP = os.environ.get("ZAMMAD_GROUP", "Users")


async def create_ticket(subject: str, body: str, sender: str) -> int:
    payload = {
        "title": subject,
        "group": DEFAULT_GROUP,
        "customer": sender,
        "article": {"subject": subject, "body": body, "type": "note", "internal": False},
    }
    headers = {"Authorization": f"Token token={ZAMMAD_TOKEN}"}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(f"{ZAMMAD_URL}/api/v1/tickets", json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()["number"]


def make_handler(client: AsyncClient):
    async def on_message(room: MatrixRoom, event: RoomMessageText) -> None:
        if not event.body.startswith("!ticket"):
            return
        try:
            _, rest = event.body.split(" ", 1)
            subject, _, body = rest.partition("|")
            number = await create_ticket(subject.strip(), body.strip() or subject.strip(), event.sender)
            reply = f"Opened request #{number} for {event.sender}."
        except Exception as exc:  # noqa: BLE001
            reply = f"Could not open request: {exc}"
        await client.room_send(
            room.room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": reply},
        )

    return on_message


async def main() -> None:
    client = AsyncClient(MATRIX_HOMESERVER, MATRIX_USER)
    await client.login(MATRIX_PASSWORD)
    client.add_event_callback(make_handler(client), RoomMessageText)
    print(f"ops-bot online as {MATRIX_USER}")
    await client.sync_forever(timeout=30000, full_state=True)


if __name__ == "__main__":
    asyncio.run(main())
