import os
import re
import json
from telethon import TelegramClient, events

# === YOUR SETTINGS ===
API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
SOURCE = os.environ['SOURCE_CHANNEL']        # @cryptoinsidebets
TARGET = os.environ['TARGET_CHANNEL']        # @cryptoinsderpump
BRAND = os.environ.get('BRAND_USERNAME', '@Cryptoinsiderbets')

# Optional custom keywords (add in Railway Variables later)
default_keywords = {
    'fuck': '****',
    'shit': '****',
    'scam': 'opportunity',
    'join now': 'check bio',
    'buy now': 'limited spots'
}
KEYWORDS = json.loads(os.environ.get('KEYWORDS', '{}')) or default_keywords

client = TelegramClient('session', API_ID, API_HASH)

def clean_text(text):
    if not text:
        return text
    # Remove t.me links
    text = re.sub(r'https?://(?:t\.me|telegram\.me|telegram\.dog)[^\s]+', '', text, flags=re.IGNORECASE)
    # Replace keywords
    for bad, good in KEYWORDS.items():
        text = text.replace(bad, good)
        text = text.replace(bad.title(), good)
        text = text.replace(bad.upper(), good)
    # Replace all @usernames
    text = re.sub(r'@\w+', BRAND, text)
    return text.strip()

@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    msg = event.message

    # If it's a forward → keep original forward tag
    if msg.fwd_from:
        await client.forward_messages(TARGET, msg)
        print(f"Forwarded (kept tag): {msg.id}")
        return

    # Otherwise → clean copy (no forward tag)
    cleaned = clean_text(msg.message or '')
    await client.send_message(
        TARGET,
        cleaned or ' ',
        file=msg.media,
        formatting_entities=msg.entities,
        silent=True
    )
    print(f"Clean copied: {msg.id}")

print("Forwarder started — waiting for messages...")
with client:
    client.run_until_disconnected()
