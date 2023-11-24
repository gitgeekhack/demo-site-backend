from app.database.common_queries import get_document_name_from_hash, get_parent_doc_id, get_document_name_from_id


def get_s3_bucket_url(doc_hash):
    """
    The method returns S3 bucket url formed by parent document name and page range of split document.

    :param doc_hash: split document hash name
    :return: Url of the S3 bucket
    """
    parent_doc_id = get_parent_doc_id(doc_hash)
    doc_name = get_document_name_from_hash(doc_hash)
    page_range = doc_name.split('.')[0]
    original_doc_name = get_document_name_from_id(parent_doc_id)

    return original_doc_name + '/' + page_range
