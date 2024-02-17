def transform(assessment):
    markdown = f"Quiz title: {assessment['title']}\n"
    desc_str = assessment["description"].replace("\n", "<br>")
    if desc_str:
        markdown += f"Quiz description: {desc_str}\n"
    markdown += "\n"

    for i, item in enumerate(assessment["items"], start=1):
        answer = item["correct_answer"]
        correct = item["correct_explanation"]
        incorrect = item["incorrect_explanation"]
        markdown += f"Title: Question {i}\nPoints: 1\n"
        markdown += f"{i}.  {item['question']}"
        for image in item["images"]:
            markdown += f"<br>![alt_text]({image})"
        markdown += "\n"
        if correct == incorrect:
            markdown += f"... {correct}\n"
        else:
            if correct:
                markdown += f"+   {correct}\n"
            if incorrect:
                markdown += f"-   {incorrect}\n"
        char = 97
        for j, choice in enumerate(item["choices"]):
            markdown += f"{'*' if j == answer else ''}{chr(char + j)}) {choice}\n"
        markdown += "\n"
    return markdown
