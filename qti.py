import json
import os
import zipfile
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString


def create_qti_xml(data):
    response_label = 0
    root = Element(
        "questestinterop",
        {
            "xmlns": "http://www.imsglobal.org/xsd/ims_qtiasiv1p2",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd",
        },
    )

    assessment = SubElement(
        root,
        "assessment",
        {
            "title": data["title"]
        },
    )

    # Number of attempts
    qtimetadata = SubElement(
        assessment,
        "qtimetadata"
    )
    qtimetadatafield = SubElement(
        qtimetadata,
        "qtimetadatafield"
    )
    attempts_field = SubElement(
        qtimetadatafield,
        "fieldlabel"
    )
    attempts_field.text = "cc_maxattempts"
    attempts_entry = SubElement(
        qtimetadatafield,
        "fieldentry",
    )
    attempts_entry.text = "3"

    # Questions
    questions = SubElement(
        assessment,
        "section",
        {
            "ident": "root_section",
        },
    )
    for item in data["items"]:
        question = SubElement(
            questions,
            "item",
            {
                "title": "Question",
            },
        )
        itemmetadata = SubElement(
            question,
            "itemmetadata"
        )
        for field, entry in [
                ("question_type", "multiple_choice_question"),
                ("points_possible", "1.0"),
                ("original_answer_ids", ",".join([str(x) for x in range(response_label, response_label + len(item["choices"]))]))
        ]:
            qtimetadata = SubElement(
                itemmetadata,
                "qtimetadata"
            )
            qtimetadatafield = SubElement(
                qtimetadata,
                "qtimetadatafield"
            )
            _field = SubElement(
                qtimetadatafield,
                "fieldlabel"
            )
            _field.text = field
            _entry = SubElement(
                qtimetadatafield,
                "fieldentry",
            )
            _entry.text = entry

        # Presentation
        presentation = SubElement(
            question,
            "presentation"
        )
        material = SubElement(
            presentation,
            "material"
        )
        mattext = SubElement(
            material,
            "mattext",
            {
                "texttype": "text/plain"
            }
        )
        mattext.text = item["question"]

        response_lid = SubElement(
            presentation,
            "response_lid",
            {
                "rcardinality": "Single"
            }
        )
        render_choice = SubElement(
            response_lid,
            "render_choice"
        )
        for i, choice in enumerate(item["choices"]):
            response_lab = SubElement(
                render_choice,
                "response_label",
                {
                    "ident": str(response_label + i)
                }
            )
            material = SubElement(
                response_lab,
                "material"
            )
            mattext = SubElement(
                material,
                "mattext",
                {
                    "texttype": "text/plain"
                }
            )
            mattext.text = choice

        # Results
        resprocessing = SubElement(
            question,
            "resprocessing"
        )
        # TODO: outcomes
        respcondition = SubElement(
            question,
            "respcondition",
            {
                "continue": "No"
            }
        )
        # TODO
        answer_id = item["correct_answer"] + response_label
        response_label += len(item["choices"])

    # Format the XML
    xml_str = tostring(root, "utf-8")

    return parseString(xml_str).toprettyxml(indent="  ")


def create_manifest_file(num_items):
    manifest = Element(
        "manifest",
        {
            "xmlns": "http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1",
            "xmlns:lom": "http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource",
            "xmlns:imsmd": "http://www.imsglobal.org/xsd/imsmd_v1p2",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2p2.xsd",
            "identifier": "manifest1",
        },
    )
    resources = SubElement(manifest, "resources")
    for i in range(1, num_items + 1):
        resource = SubElement(
            resources,
            "resource",
            {
                "identifier": f"resource{i}",
                "type": "imsqti_xmlv2p1",
                "href": f"assessment{i}.xml",
            },
        )
        SubElement(resource, "file", {"href": f"assessment{i}.xml"})

    xml_str = tostring(manifest, "utf-8")
    pretty_xml = parseString(xml_str).toprettyxml(indent="  ")

    return pretty_xml


def json_to_qti_zip(assessments, output_zip):
    # Create QTI XML files
    for i, assessment in enumerate(assessments, start=1):
        qti_xml = create_qti_xml(assessment)
        with open(f"assessment{i}.xml", "w") as xml_file:
            xml_file.write(qti_xml)

    # Create manifest file
    manifest_xml = create_manifest_file(len(assessments))
    with open("imsmanifest.xml", "w") as manifest_file:
        manifest_file.write(manifest_xml)

    # Create ZIP package
    with zipfile.ZipFile(output_zip, "w") as zipf:
        zipf.write("imsmanifest.xml")
        for i in range(1, len(assessments) + 1):
            zipf.write(f"assessment{i}.xml")

    # Clean up XML files
    os.remove("imsmanifest.xml")
    for i in range(1, len(assessments) + 1):
        os.remove(f"assessment{i}.xml")
