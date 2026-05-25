from plugins_func.register import register_function, ToolType, ActionResponse, Action
from plugins_func.functions.hass_init import initialize_hass_handler
from config.logger import setup_logging
import asyncio
import requests
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.connection import ConnectionHandler

TAG = __name__
logger = setup_logging()

hass_play_music_function_desc = {
    "type": "function",
    "function": {
        "name": "hass_play_music",
        "description": "Use this when the user wants to listen to music or an audiobook. Play the corresponding audio on the room media player.",
        "parameters": {
            "type": "object",
            "properties": {
                "media_content_id": {
                    "type": "string",
                    "description": "Album name, song title, or artist for music or audiobooks. Use random if not specified.",
                },
                "entity_id": {
                    "type": "string",
                    "description": "Speaker device ID to operate on, the entity_id in Home Assistant. It should start with media_player.",
                },
            },
            "required": ["media_content_id", "entity_id"],
        },
    },
}


@register_function(
    "hass_play_music", hass_play_music_function_desc, ToolType.SYSTEM_CTL
)
def hass_play_music(conn: "ConnectionHandler", entity_id="", media_content_id="random"):
    try:
        # 执行音乐播放命令
        future = asyncio.run_coroutine_threadsafe(
            handle_hass_play_music(conn, entity_id, media_content_id), conn.loop
        )
        ha_response = future.result()
        return ActionResponse(
            action=Action.RESPONSE, result="退出意图已处理", response=ha_response
        )
    except Exception as e:
        logger.bind(tag=TAG).error(f"处理音乐意图错误: {e}")


async def handle_hass_play_music(
    conn: "ConnectionHandler", entity_id, media_content_id
):
    ha_config = initialize_hass_handler(conn)
    api_key = ha_config.get("api_key")
    base_url = ha_config.get("base_url")
    url = f"{base_url}/api/services/music_assistant/play_media"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"entity_id": entity_id, "media_id": media_content_id}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return f"正在播放{media_content_id}的音乐"
    else:
        return f"音乐播放失败，错误码: {response.status_code}"
