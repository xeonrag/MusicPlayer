import os
from config import config
from core.song import Song
from pyrogram import Client
from yt_dlp import YoutubeDL
from pytgcalls import PyTgCalls
from core.funcs import generate_cover
from core.groups import get_group, set_title
from pytgcalls.types.stream import MediaStream
from pytgcalls.types import AudioQuality, VideoQuality

safone = {}
ydl_opts = {
    "quiet": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
}

app = Client(
    "MusicPlayerUB",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.SESSION,
    in_memory=True,
)

ytdl = YoutubeDL(ydl_opts)
pytgcalls = PyTgCalls(app)


async def start_stream(song: Song, lang):
    chat = song.request_msg.chat

    # delete previous message
    if safone.get(chat.id) is not None:
        try:
            await safone[chat.id].delete()
        except BaseException:
            pass

    infomsg = await song.request_msg.reply_text(lang["downloading"])

    # Directly try to play — no exception handling
    await pytgcalls.play(
        chat.id,
        get_quality(song),
    )

    await set_title(chat.id, song.title, client=app)

    thumb = await generate_cover(
        song.title,
        chat.title,
        chat.id,
        song.thumb,
    )

    safone[chat.id] = await song.request_msg.reply_photo(
        photo=thumb,
        caption=lang["playing"]
        % (
            song.title,
            song.source,
            song.duration,
            song.request_msg.chat.id,
            (
                song.requested_by.mention
                if song.requested_by
                else song.request_msg.sender_chat.title
            ),
        ),
        quote=False,
    )

    await infomsg.delete()
    if os.path.exists(thumb):
        os.remove(thumb)


def get_quality(song: Song) -> MediaStream:
    group = get_group(song.request_msg.chat.id)

    if group["stream_mode"] == "video":
        if config.QUALITY.lower() == "high":
            return MediaStream(
                song.remote,
                AudioQuality.HIGH,
                VideoQuality.FHD_1080p,
                headers=song.headers,
            )
        elif config.QUALITY.lower() == "medium":
            return MediaStream(
                song.remote,
                AudioQuality.MEDIUM,
                VideoQuality.HD_720p,
                headers=song.headers,
            )
        elif config.QUALITY.lower() == "low":
            return MediaStream(
                song.remote,
                AudioQuality.LOW,
                VideoQuality.SD_480p,
                headers=song.headers,
            )
        else:
            print("WARNING: Invalid Quality Specified. Defaulting to High!")
            return MediaStream(
                song.remote,
                AudioQuality.HIGH,
                VideoQuality.FHD_1080p,
                headers=song.headers,
            )
    else:
        if config.QUALITY.lower() == "high":
            return MediaStream(
                song.remote,
                AudioQuality.HIGH,
                video_flags=MediaStream.Flags.IGNORE,
                headers=song.headers,
            )
        elif config.QUALITY.lower() == "medium":
            return MediaStream(
                song.remote,
                AudioQuality.MEDIUM,
                video_flags=MediaStream.Flags.IGNORE,
                headers=song.headers,
            )
        elif config.QUALITY.lower() == "low":
            return MediaStream(
                song.remote,
                AudioQuality.LOW,
                video_flags=MediaStream.Flags.IGNORE,
                headers=song.headers,
            )
        else:
            print("WARNING: Invalid Quality Specified. Defaulting to High!")
            return MediaStream(
                song.remote,
                AudioQuality.HIGH,
                video_flags=MediaStream.Flags.IGNORE,
                headers=song.headers,
            )
