def summarize_event(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    title = lines[0][:150] if lines else "Untitled Event"

    description = " ".join(lines[1:6])[:500]

    return {
        "title": title,
        "description": description
    }
