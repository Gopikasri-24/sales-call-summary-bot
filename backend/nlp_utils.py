def generate_summary(transcript):
    if not transcript.strip():
        return "No transcript provided."

    lines = transcript.splitlines()
    clean_lines = []

    for line in lines:
        if line.strip():
            clean_lines.append(line.strip())

    first_lines = clean_lines[:3]
    summary = " ".join(first_lines)

    return "Sales call summary: " + summary


def extract_action_items(transcript):
    text = transcript.lower()
    action_items = []

    if "pricing" in text or "price" in text:
        action_items.append("Send pricing details to the customer.")

    if "demo" in text:
        action_items.append("Schedule a product demo.")

    if "follow" in text:
        action_items.append("Follow up with the customer.")

    if "email" in text:
        action_items.append("Send an email to the customer.")

    if "meeting" in text:
        action_items.append("Schedule the next meeting.")

    if len(action_items) == 0:
        action_items.append("Review the call and identify next steps.")

    return action_items


def analyze_sentiment(transcript):
    text = transcript.lower()

    positive_words = ["interested", "thank", "good", "great", "sure", "definitely", "yes"]
    negative_words = ["not interested", "bad", "issue", "problem", "no", "cancel"]

    positive_count = 0
    negative_count = 0

    for word in positive_words:
        if word in text:
            positive_count += 1

    for word in negative_words:
        if word in text:
            negative_count += 1

    if positive_count > negative_count:
        return "POSITIVE"
    elif negative_count > positive_count:
        return "NEGATIVE"
    else:
        return "NEUTRAL"