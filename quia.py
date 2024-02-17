import bs4
import json

SEP = "---"

def html_to_json(filename, verbose=False):
    with open(filename) as f:
        html = f.read()
    soup = bs4.BeautifulSoup(html, "html.parser")
    forms = soup.find_all("form")
    for form in forms:
        if form.attrs.get("name") != "quiaForm":
            continue
        inputs = form.find_all("input")
        title = ""
        for _input in inputs:
            if _input.attrs.get("name") == "title":
                title = _input.attrs.get("value")
                break
        placeholders = form.find_all("table", id="insertDataBlockTblId")
        # Extra table at the end to sum up points.
        questions = [p.find_next("table") for p in placeholders[:-1]]
        results = {"title": title, "items": [extract(q) for q in questions]}

    if verbose:
        print(results["title"])
        for i, item in enumerate(results["items"]):
            print(f"Question {i+1}: {item['question']}")
            for opt in item["choices"]:
                print(f" * {opt}")
            print(f"Answer: {chr(65 + item['correct_answer'])}\n")
            print(f"Feedback (correct) {item['correct_explanation']}\n")
            print(f"Feedback (incorrect) {item['incorrect_explanation']}\n\n{SEP}\n")

    return results


def extract(question):
    ch1 = [x for x in question.children if x.text.strip()]
    ch2 = [x for x in ch1[0].children if x.text.strip()]
    ch3 = [x for x in ch2[0].children if x.text.strip()]
    # ch3[0] is the Switch to edit mode/Remove button
    ch4 = [x for x in ch3[1].children if x.text.strip()]
    text, options = get_q_and_a(ch4[0])
    ans, corr, incorr = get_explanations(ch4[1], options)
    return dict(
        question=text,
        choices=options,
        correct_answer=ans,
        correct_explanation=corr,
        incorrect_explanation=incorr
    )


def get_q_and_a(question):
    # Unwrapping the table
    q = [question]
    for _ in range(4):
        q = [x for x in q[0].children if x.text.strip()]
    boxes = [x for x in q if x.text.strip()]
    text = boxes[0].text.strip()
    options =  [x.text.strip() for x in boxes[1].find_all("td")][1::2]
    return text, options


def get_explanations(expl, options):
    e = [expl]
    for _ in range(6):
        e = [x for x in e[0].children if x.text.strip()]
    ans_children = [x for x in e[0].children]
    for ans_child in ans_children:
        if not ans_child.text.strip():
            continue
        if "Correct answer:" in ans_child.text:
            continue
        ans_text = ans_child.text.strip()
        break
    ans = -1
    for i, o in enumerate(options):
        if o == ans_text:
            ans = i
            break
    corr = [x.text for x in e[1] if x.text.strip()][1]
    incorr = [x.text for x in e[2] if x.text.strip()][1]
    return ans, corr, incorr
