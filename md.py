def transform(assessment):
    markdown = f"Quiz title: {assessment['title']}\n\n"
    for i, item in enumerate(assessment["items"]):
        answer = item["correct_answer"]
        correct = item["correct_explanation"]
        incorrect = item["incorrect_explanation"]
        markdown += f"Title: Question {i}\nPoints: 1\n"
        markdown += f"{i}.  {item['question']}\n"
        if correct == incorrect:
            markdown += f"... {correct}\n"
        else:
            markdown += f"+   {correct}\n"
            markdown += f"-   {incorrect}\n"
        char = 97
        for j, choice in enumerate(item["choices"]):
            markdown += f"{'*' if j == answer else ''}{chr(char + j)}) {choice}\n"
        markdown += "\n"
    return markdown
