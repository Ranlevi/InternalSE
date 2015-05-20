from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import os
import shelve

"""
    Internal Stack Exchange - Search Engine
    ---------------------------------------
    Holds various function the search the database.
"""

########################################################
def get_all_index_pointers(path_to_index_folder, db_names):
    """ Scan the /Index folder, return the pointers to every index found there.
    """
    index_pointers = {}
    for name in db_names:
        pointer              = open_dir(path_to_index_folder, name+'_index')
        index_pointers[name] = pointer

    return index_pointers

########################################################
def get_search_results(index_pointer, search_term, page_number, site_name, is_tag):
    """ Query the index for the desired search term. The select field
        in the schema ("doc_tags" or "doc_texts") is selected by the is_tag parameter.
    """

    #This shlv holds all the docs of the selected site.
    full_docs_shlv = shelve.open('../db/' + site_name +'.db', 'r', protocol = -1)

    matched_docs_ids = []
    with index_pointer.searcher() as searcher:

        # If we are searching for a tag - query the "doc_tags" field,
        # else, query the "doc_texts".
        if is_tag == "1":
            myquery = QueryParser("doc_tags", index_pointer.schema).parse(search_term)
        else: #"0"
            myquery = QueryParser("doc_texts", index_pointer.schema).parse(search_term)
        
        results = searcher.search_page(myquery, page_number)

        #Find the questions Id of the results.
        for hit in results:
            matched_docs_ids.append(hit['question_id'])

    search_results = []
    #Store the title and body of the question, to display to the user.
    for doc_id in matched_docs_ids:
        tmp_title = full_docs_shlv[str(doc_id)]['Title']
        tmp_text  = full_docs_shlv[str(doc_id)]['Body']
        
        search_results.append({'Title':tmp_title, 'Body':tmp_text, 'Id':doc_id})

    full_docs_shlv.close()
    return search_results, results.is_last_page()

