def build_comic_layout(image_paths, full_story, outline):
    story_panels = full_story.split("**Panel")
    story_panels = [
        f"**Panel{panel}"
        for panel in story_panels
        if panel.strip()
    ]

    if len(image_paths) != len(outline):
        raise ValueError(
            f"Image/outline mismatch: {len(image_paths)} images, "
            f"{len(outline)} outline panels."
        )

    if len(story_panels) != len(outline):
        raise ValueError(
            f"Story/outline mismatch: {len(story_panels)} story panels, "
            f"{len(outline)} outline panels."
        )

    layout = []

    for idx, panel_info in enumerate(outline, start=1):
        image = image_paths[idx - 1]
        text = story_panels[idx - 1]

        layout.append({
            "panel": idx,
            "title": panel_info.get("title", f"Panel {idx}"),
            "image_path": image,
            "text": "\n".join(
                text.strip().splitlines()[1:]
            ).strip(),
            "scene_description": panel_info.get(
                "scene_description", ""
            ),
        })

    return layout