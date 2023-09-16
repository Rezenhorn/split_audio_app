from flask import request

from apps.api import blueprint
from apps.api.utils import add_apprequest_to_db
from apps.errors.errors import APIError
from modules.main_logic import get_mono_audio_links


@blueprint.route("/split_audio", methods=["POST"])
def audio_split():
    link = request.json.get("link")
    if not link:
        raise APIError("В запросе отсутствует link.")
    try:
        mono_files_links = get_mono_audio_links(link)
    except Exception as e:
        add_apprequest_to_db(link, False)
        raise APIError(str(e)) from e
    add_apprequest_to_db(link, True)
    return {
        "status": "success",
        "result": {
            "left_mono": mono_files_links.left_channel_link,
            "right_mono": mono_files_links.right_channel_link
        }
    }
