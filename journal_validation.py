def validate_journal_entry(title, content):
    
    title = title.strip()
    content = content.strip()

    if not title:
        return "Title cannot be empty."
    
    if not content:
        return "Content cannot be empty."
    
    if len(title) > 100:
        return "Title cannot exceed 100 characters."
    
    if len(content) > 3000:
        return "Content cannot exceed 1000 characters."
    
    return None