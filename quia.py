import json

import bs4

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

        descs = form.find_all("textarea")
        desc = ""
        for _desc in descs:
            if _desc.attrs.get("name") == "desc":
                desc = _desc.text
                break

        standard_format = True
        placeholders = form.find_all("table", id="insertDataBlockTblId")
        # Extra table at the end to sum up points.
        questions = [p.find_next("table") for p in placeholders[:-1]]

        if not questions:
            # Quiz editing HTML is on the alternate format, or has errors.
            standard_format = False
            questions = [
                x
                for x in form.find_all("textarea")
                if "tagQECPrefixQuestionText_" in x.attrs["name"]
            ]

        results = {
            "title": title,
            "description": desc,
            "items": [extract(q, standard_format) for q in questions],
        }
        break

    if verbose:
        print(results["title"])
        for i, item in enumerate(results["items"]):
            print(f"Question {i+1}: {item['question']}")
            if choices:
                for opt in item["choices"]:
                    print(f" * {opt}")
                print(f"Answer: {chr(65 + item['correct_answer'])}\n")
            else:
                print(f"Answer(s): {item['correct_answer']}\n")
            print(f"Feedback (correct) {item['correct_explanation']}\n")
            print(f"Feedback (incorrect) {item['incorrect_explanation']}\n\n{SEP}\n")

    return results


def extract(question, standard):
    if standard:
        ch1 = [x for x in question.children if x.text.strip()]
        ch2 = [x for x in ch1[0].children if x.text.strip()]
        ch3 = [x for x in ch2[0].children if x.text.strip()]
        # ch3[0] is the Switch to edit mode/Remove button
        ch4 = [x for x in ch3[1].children if x.text.strip()]
        text, images, options = get_q_and_a(ch4[0])
        ans, corr, incorr = get_explanations(ch4[1], options)
    else:
        text = question.text
        index = question.attrs["name"].split("_")[1]
        tag = "tagQECPrefixIsCorrectAnswer_" + index
        ans = -1
        images = []  # TODO: Is it possible for images to be here?
        options = []
        it = question.find_next("input")
        while it.attrs["name"] == tag:
            opt_idx = it.attrs["value"]
            if "checked" in it.attrs:
                ans = int(opt_idx)
            it = it.find_next("input")
            assert it.attrs["name"] == f"tagQECPrefixAnswerText_{index}_{opt_idx}"
            option = it.attrs["value"]
            if option:
                options.append(option)
                it = it.find_next("input")
            else:
                break
        while it.attrs["name"] != f"tagQECPrefixCorrectFeedback_{index}":
            it = it.find_next("input")
        corr = it.attrs["value"].strip()
        while it.attrs["name"] != f"tagQECPrefixIncorrectFeedback_{index}":
            it = it.find_next("input")
        incorr = it.attrs["value"].strip()
    return dict(
        question=text,
        images=images,
        choices=options,
        correct_answer=ans,
        correct_explanation=corr,
        incorrect_explanation=incorr,
    )


def get_q_and_a(question):
    # Unwrapping the table
    q = [question]
    for _ in range(3):
        q = [x for x in q[0].children if x.text.strip()]
    # Assumes there are only images in the question.
    images = [x.attrs["src"] for x in q[0].find_all("img")]
    q = [x for x in q[0].children if x.text.strip()]
    boxes = [x for x in q if x.text.strip()]
    text = ""
    i = 0
    while i < len(boxes):
        if not "find_all" in dir(boxes[i]):
            if i != 0:
                text += " "
            text += boxes[i].text.strip()
        else:
            break
        i += 1
    if i < len(boxes):
        options = [x.text.strip() for x in boxes[i].find_all("td")][1::2]
    else:
        options = []  # short answer
    return text, images, options


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
        if "Correct answers:" in ans_child.text:
            continue
        ans_text = ans_child.text.strip()
        break
    if options:
        # single choice
        ans = -1
        for i, o in enumerate(options):
            if o == ans_text:
                ans = i
                break
        # multiple choice
        if ans == -1:
            ans = []
            accept = ans_text.split("• ")[1:]
            for i, o in enumerate(options):
                for acc in accept:
                    if o == acc:
                        ans.append(i)
    else:
        # short answer
        if "• " in ans_text:
            ans = ans_text.split("• ")[1:]
        else:
            ans = [ans_text]
    corr = ""
    incorr = ""
    if len(e) > 1:
        _corr = [x.text for x in e[1] if x.text.strip()]
        if len(_corr) > 1:
            corr = _corr[1]
    if len(e) > 2:
        _incorr = [x.text for x in e[2] if x.text.strip()]
        if len(_incorr) > 1:
            incorr = _incorr[1]
    return ans, corr, incorr
