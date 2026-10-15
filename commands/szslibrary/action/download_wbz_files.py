import json

from common_utils.szslibrary_helpers import validate_start_end_wbz_ids
from tockdomio.szslibrary_read import get_wbz_file_from_id, get_by_wbz_id


def download_wbz(start_id, end_id, folder_path):
    if not validate_start_end_wbz_ids(start_id, end_id):
        return False

    for i in range(int(start_id), int(end_id) + 1):
        print(f"{i} processing entry")
        szslib_info = get_by_wbz_id(i)
        if szslib_info is None:
            print(f"{i} information does not exist, skipping")
        else:
            with open(folder_path + f"/{i}.json", "wb") as f:
                f.write(json.dumps(szslib_info, ensure_ascii=False).encode('utf8'))

        content = get_wbz_file_from_id(i)
        if content is None:
            print(f"{i} wbz file does not exist, skipping")
            continue

        with open(folder_path + f"/{i}.wbz", "wb") as f:
            f.write(content)

    return True