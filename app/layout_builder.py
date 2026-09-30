def build_comic_layout(image_paths, story_panels, outline):
    """
    Combines generated images, structured story panels,
    and the original outline into the final comic layout.
    """

    if len(image_paths) != len(outline):
        raise ValueError(
            f"Image/outline mismatch: "
            f"{len(image_paths)} images, "
            f"{len(outline)} outline panels."
        )

    if len(story_panels) != len(outline):
        raise ValueError(
            f"Story/outline mismatch: "
            f"{len(story_panels)} story panels, "
            f"{len(outline)} outline panels."
        )

    layout = []

    for idx, panel_info in enumerate(outline, start=1):
        story = story_panels[idx - 1]

        layout.append({
            "panel": idx,
            "title": panel_info.get(
                "title",
                f"Panel {idx}"
            ),
            "image_path": image_paths[idx - 1],
            "text": story.get("story", ""),
            "scene_description": panel_info.get(
                "scene_description",
                ""
            )
        })

    return layout