from typing import Any, List

def create_image_data_dict(
    thumbnail_heights: List[int], 
    img_obj: Any, # cannot set an type because of partially initialized module
    is_expiring_link_generation_provided: bool,
    is_link_to_original_provided: bool
) -> dict:
    data = {}
    data["thumbnails"] = []
    for height in thumbnail_heights:
        data["thumbnails"].append(
            img_obj.create_image_dict(
                height,
                is_expiring_link_generation_provided
            )
        )
    if is_link_to_original_provided:
        data["original"] = img_obj.create_image_dict(None, is_expiring_link_generation_provided)
    return data