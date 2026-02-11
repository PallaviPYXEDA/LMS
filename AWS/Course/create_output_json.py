import os
import json
from pinecone import Pinecone

from Utils import response_utils as rutils
from Utils import request_utils as req_utils

# Configuring pinecone
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_ENV = os.environ["PINECONE_HOST"]
INDEX_NAME = "aiclub-serverless"
NAMESPACE = "curriculum-db-dev"
EMBEDDING_SIZE = 1536

# Initialize pinecone
pinecone = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pinecone.Index(INDEX_NAME)

#Verifying pinecone connection
print("[INIT] Pinecone client initialized")
print(f"[INFO] Connected to index: {INDEX_NAME} in namespace: {NAMESPACE}")


def fetch_chapter_details(file_id, index):
    """
    Fetches multimedia and discussion question details for a given file_id.
    """
    print(f"Fetching chapter details for file_id: {file_id}")

    metadata_filter = {"fileId": {"$eq": file_id}}
    dummy_vector = [0.0] * EMBEDDING_SIZE

    response = index.query(
        vector=dummy_vector,
        top_k=10,
        filter=metadata_filter,
        namespace=NAMESPACE,
        include_metadata=True
    )

    multimedia_list = []
    discussion_questions = []
    json_order = 0
    chapter_title = "NA"

    for match in response.get("matches", []):
        metadata = match.get("metadata", {})
        resource_data = metadata.get("resource_data")

        if not resource_data:
            continue

        try:
            resource_data_json = json.loads(resource_data)
        except Exception as parse_err:
            print(f"[WARN] Failed to parse resource_data for file {file_id}: {parse_err}")
            continue

        resources = resource_data_json.get("resources", {})
        discussion_questions = resources.get("discussionQuestions", [])

        for multimedia_item in resources.get("multimedia", []):
            json_order += 1
            multimedia_list.append({
                "title": multimedia_item.get("title", "NA"),
                "video": multimedia_item.get("youtube_link") or multimedia_item.get("video", "NA"),
                "slide": multimedia_item.get("slides", "NA"),
                "teachers_guide": multimedia_item.get("teachers_guide", "NA"),
                "json_order": json_order
            })

        chapter_title = metadata.get("moduleTitle", "NA")

    return {
        "chapter_title": chapter_title,
        "chapter_resources": {
            "multimedia": multimedia_list,
            "discussion_questions": discussion_questions
        }
    }


def fetch_section_details(section, index):
    """
    Fetches all chapter details for a given section.
    """
    section_id = section.get("section_id", "")
    section_title = section.get("section_title", "")
    file_ids = section.get("file_ids", [])

    print(f"\nProcessing section: {section_title} ({section_id}) with {len(file_ids)} file_ids")

    chapters = []

    for file_id in file_ids:
        chapter_data = fetch_chapter_details(file_id, index)
        chapters.append(chapter_data)

    return {
        "section_id": section_id,
        "section_title": section_title,
        "chapters": chapters
    }


def process_get_request(event):
    """
    Processes GET requests to build structured course data.
    """
    params = event.get("queryStringParameters", {})
    course_dict = req_utils.get_params(params, "inputJson")
    if isinstance(course_dict, str):
        course_dict = json.loads(course_dict)
    course_id = course_dict.get("course_id", "")
    course_title = course_dict.get("course_title", "")
    sections = course_dict.get("sections", [])

    processed_sections = []

    for section in sections:
        section_data = fetch_section_details(section, index)
        processed_sections.append(section_data)

    final_response = {
        "course_id": course_id,
        "course_title": course_title,
        "sections": processed_sections
    }

    return final_response


def lambda_handler(event: dict, context: dict) -> dict:
    """
    Handles API Gateway Lambda requests.
    """
    try:
        print("EVENT : ",json.dumps(event, indent=2))
        method = event.get('httpMethod', 'UNKNOWN')
        print(f"[INFO] HTTP Method: {method}")
        
        if method == "GET":
            print("Invoking process_get_request()")
            response = process_get_request(event)
        else:
            print(f"[WARN] Unsupported HTTP Method: {method}")
            return rutils.unsupported_method(event, context, Exception("Unsupported method"))

    except Exception as e:
        print(f"[ERROR] Exception occurred in lambda_handler: {e}")
        return rutils.unsupported_method(event, context, e)

    return rutils.success_method(response)