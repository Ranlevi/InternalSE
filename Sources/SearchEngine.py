from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import os

########################################################
def get_all_index_pointers(path_to_index_folder, db_names):
    index_pointers = {}
    for name in db_names:
        pointer = open_dir(path_to_index_folder, name+'_index')
        index_pointers[name] = pointer

    return index_pointers

########################################################
def get_search_results(index_pointer, tag, page_number, data):

    matched_docs_ids = []
    with index_pointer.searcher() as searcher:
        myquery = QueryParser("doc_tags", index_pointer.schema).parse(tag)
        results = searcher.search_page(myquery, page_number)
        for hit in results:
            matched_docs_ids.append(hit['question_id'])

    search_results = []
    for doc_id in matched_docs_ids:
        tmp_title = data[doc_id]['Title']
        tmp_text  = data[doc_id]['Body']
        
        search_results.append({'Title':tmp_title, 'Body':tmp_text, 'Id':doc_id})

    return search_results 
    
#path_to_datadumps = '../Datadumps/'
#datadumps = os.listdir(path_to_datadumps)
# 
#indexes_pointer = get_all_index_pointers('../Index', datadumps)


