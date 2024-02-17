def transform(assessment):
    markdown = f"Quiz title: {assessment['title']}\n"
    desc_str = assessment["description"].replace("\n", "<br>")
    if desc_str:
        markdown += f"Quiz description: {desc_str}\n"
    markdown += "\n"

    i = 0
    seen_questions = set()
    for item in assessment["items"]:
        question = item["question"]
        if question in seen_questions:
            continue
        i += 1
        seen_questions.add(question)
        answer = item["correct_answer"]
        choices = item["choices"]
        correct = item["correct_explanation"]
        incorrect = item["incorrect_explanation"]
        markdown += f"Title: Question {i}\nPoints: 1\n"
        markdown += f"{i}.  {item['question']}"
        for image in item["images"]:
            markdown += f"<br>![alt_text]({image})"
        markdown += "\n"
        if correct and correct == incorrect:
            markdown += f"... {correct}\n"
        else:
            if correct:
                markdown += f"+   {correct}\n"
            if incorrect:
                markdown += f"-   {incorrect}\n"
        if choices:
            for j, choice in enumerate(choices):
                markdown += f"{'*' if j == answer else ''}{chr(97 + j)}) {choice}\n"
        else:
            for ans in answer:
                markdown += f"*   {ans}\n"
        markdown += "\n"
    return markdown
