import discord
import io
import analysImage
from PIL import Image
import os

# ボットのトークン
TOKEN = os.environ['TOKEN']

# Discord Intentsの設定
intents = discord.Intents.default()
intents.message_content = True

# Discordクライアントを作成
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}")


@client.event
async def on_message(message):
    # メッセージがボット自身のものであれば無視
    if message.author == client.user:
        return
    # 特定のチャンネルID
    target_channel_id = int(os.environ['CHANNEL_ID'])

    # 投稿されたメッセージが特定のチャンネルからのものかチェック
    if message.channel.id == target_channel_id:
        if client.user in message.mentions:
            # 画像が添付されているかチェック
            if len(message.attachments) > 0:
                total_images = len(message.attachments)
                for index, attachment in enumerate(message.attachments,
                                                   start=1):
                    if attachment.content_type.startswith("image"):
                        # 画像のダウンロード
                        image_data = await attachment.read()
                        image_binary = io.BytesIO(image_data)
                        image = Image.open(image_binary)

                        # 画像解析
                        try:
                            result1, result2, result3, score = analysImage.main(
                            image)
                            scores = {
                                "vo": result1,
                                "da": result2,
                                "vi": result3,
                                "total": score
                            }

                        except:
                            scores = {}

                        # 画像解析から取得したスコアを返信
                        await reply(message, scores)


async def reply(message, scores):
    if scores != {}:
        print(scores)
        vo = scores["vo"]
        da = scores["da"]
        vi = scores["vi"]
        upload_message = f"Vo: {vo}, Da: {da}, Vi: {vi}"
        await message.reply(upload_message)
    else:
        await message.reply("解析に失敗しました")


if __name__ == "__main__":
    client.run(TOKEN)

