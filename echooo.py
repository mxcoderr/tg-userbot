from lxml import etree as ET
from telethon import TelegramClient, events
import logging
logging.basicConfig(level=logging.INFO)

def load_config():
    tree = ET.parse("config.xml")
    root = tree.getroot()

    return {
        "api_id": int(root.xpath("/Client/API_ID/text()")[0]),
        "api_hash": root.xpath("/Client/API_HASH/text()")[0],
        "phone_number": root.xpath("/Client/PHONE_NUMBER/text()")[0],
    }


def parse_pycode(text):
    code = text[8:].strip()
    if "import" in code or "open" in code or "__import__" in code or "exec" in code or "eval" in code:
        return "недопустимо"
    else:
        env = {}
        env["env"] = env
        exec(code, env)
        return "true"


def parse(text):
    if text.startswith(".pycode/"):
        return parse_pycode(text)

    if text.startswith(".about"):
        return "роботизированный телеграм аккаунт с своими командами(echo, pycode)"
    
    if text.startswith(".echo/"):
        return text[6:].strip()

    return None


config = load_config()

client = TelegramClient(
    "session",
    config["api_id"],
    config["api_hash"]
)
sent_users = set()

@client.on(events.NewMessage(incoming=True, outgoing=True))
async def handler(event):
    response = parse(event.raw_text)

    if response:
        await event.reply(response)

    if event.is_private:
        sender = await event.get_sender()

        if sender.id not in sent_users:
            await event.reply(
                f"приветствую '{sender.first_name}' !\n"
                "владелец аккаунта отсутствует до 26 апреля.\n"
                "я бот который создал mxplay(владелец аккаунта)."
            )
            sent_users.add(sender.id)

if __name__ == "__main__":
   client.start(phone=config["phone_number"])
   client.run_until_disconnected()
   
