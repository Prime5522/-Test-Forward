from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN
from database import set_channel, get_user_settings, set_active, get_all_active, is_admin

app = Client("forward_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("👋 Welcome! Use /set_source and /set_dest to begin.")

@app.on_message(filters.command("set_source"))
async def set_source(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /set_source <channel_id>")
    channel_id = message.command[1]
    if not await is_admin(client, channel_id):
        return await message.reply("❌ Bot is not an admin in the source channel.")
    set_channel(message.from_user.id, "source", channel_id)
    await message.reply("✅ Source channel saved.")

@app.on_message(filters.command("set_dest"))
async def set_dest(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /set_dest <channel_id>")
    channel_id = message.command[1]
    if not await is_admin(client, channel_id):
        return await message.reply("❌ Bot is not an admin in the destination channel.")
    set_channel(message.from_user.id, "dest", channel_id)
    await message.reply("✅ Destination channel saved.")

@app.on_message(filters.command("start_forwarding"))
async def start_forwarding(client, message):
    user_id = message.from_user.id
    settings = get_user_settings(user_id)
    if not settings or "source" not in settings or "dest" not in settings:
        return await message.reply("❌ Please set both source and destination first.")
    
    set_active(user_id, True)
    await message.reply(
        "🚀 Forwarding started.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⛔ Cancel Forwarding", callback_data=f"cancel_{user_id}")]
        ])
    )

@app.on_callback_query(filters.regex(r"cancel_(\d+)"))
async def cancel_forwarding(client, query):
    user_id = int(query.matches[0].group(1))
    set_active(user_id, False)
    await query.message.edit("✅ Forwarding cancelled.")

@app.on_message(filters.channel)
async def forward_messages(client, message):
    active_users = get_all_active()
    for user in active_users:
        if str(message.chat.id) == str(user.get("source")):
            try:
                await message.copy(chat_id=user.get("dest"))
            except Exception as e:
                print(f"Error: {e}")

app.run()
