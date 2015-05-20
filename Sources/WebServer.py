from bottle import route, run, template, static_file, request
import shelve
import SearchEngine, Indexer
import cPickle
import os, sys

"""
    Internal Stack Exchange
    -----------------------
    A tool to enable using the StackExchange datadumps (https://archive.org/details/stackexchange)
    in offline enviroments (e.g. internal network of a company, not connected to the 
    internet).

    Prequisites:
    -Python 2.7 
    -A linux server with admin priviliges

    Dependencies:
    -Bootle
    -Whoosh

    Usage:
        -Unzip internal_s_e.zip to some directory.
        -Go to the /Sources directory
        -type: python Indexer.py
            The app will index all the datadumps in the /Datadumps folder.
        -type: python Webserver.py <optional: server's ip address> <optional: port number>
            The webserver will start.

        If no IP or Port number were given, the server will launch in 'development mode':
        localhost, 8080.

        Open the web browswer, and go to the server's ip address. e.g.:
        "http://192.1.2.3:80/"

    TODO:
        decide on a standard naming scheme.
        add related links
        add selected answer
        add loging and better print out
        add self test for deployment
        remove temp dbs
        document in sphinx
        add py3 support
        make the indexer a standalone app, for someone to build a front end. 
"""
## Webpages ###
###############

@route('/')
@route('/index')
def index():
    """ Display a list of 'sites'. a 'site' is a single datadump, e.g. 'Beer', 'Math'.
        Sites are sorted alpahbeticaly (default) or by size.
    """
    sort_type             = request.query.sort_type or 'name' 
    sorted_s_e_sites_list = sort_by_name_of_size(s_e_sites, sort_type)
   
    return template('index', s_e_sites = sorted_s_e_sites_list)

#####################################
@route('/help')
def help():
    return template('help')

#####################################
@route('/news')
def news():
    return template('news')

#####################################
@route('/about')
def about():
    return template('about')

#####################################
@route('/contact')
def contanct():
    return template('contact')

#####################################
@route('/site')
def site():
    """ Display a Search box, and a list of tags avaliable for that site.
        Tags can be sorted by name (default) or size.
    """
    site_name = request.query.site_name
    sort_type = request.query.sort_type or 'name'
    site_tags = tags_dict[site_name] 

    sorted_site_tags = sort_by_name_of_size(site_tags, sort_type)
    return template('site', site_name = site_name, site_tags = sorted_site_tags)

#####################################
@route('/search')
def search():
    """ Display the search results, 10 items at a time.
        The user can browse to the previous page or the next page.
    """

    search_term   = request.query.search_term
    site_name     = request.query.site_name
    page_number   = int(request.query.page_number or '1', 10)
    is_tag        = request.query.is_tag #Is the search_term a tag, or is it a free search?

    # If this is the first page, there's no previous page.
    if page_number == 1:
        prev_page = None
    else:
        prev_page = page_number-1

    #Load the pointer to the site's search engine index.
    index_pointer = index_pointers[site_name]

    search_results , is_last_page = SearchEngine.get_search_results(index_pointer, 
                                                                    search_term, 
                                                                    page_number, 
                                                                    site_name, 
                                                                    is_tag)
   
    # If this is the last page of results, there's no next page. 
    if is_last_page:
        next_page = None
    else:
        next_page = page_number+1
    
    return template('search_results', current_page_num  = page_number, 
                                      prev_page         = prev_page, 
                                      next_page         = next_page, 
                                      site_name         = site_name, 
                                      is_tag            = is_tag, 
                                      search_term       = search_term, 
                                      search_results    = search_results)

#####################################
@route('/display_full_doc')
def display_full_doc():
    """ Display a full 'doc': a 'doc' is a question with all of it's answers, comments, etc.
    """
    doc_id        = request.query.doc_id
    site_name     = request.query.site_name
    is_tag        = request.query.is_tag
    search_term   = request.query.search_term
    page_number   = int(request.query.page_number, 10)

    # Open the database for the selected site, and retrive the doc by it's Id.
    full_docs_shlv = shelve.open('../db/' + site_name +'.db', 'r', protocol = -1)
    doc_data       = full_docs_shlv[str(doc_id)]
    full_docs_shlv.close() 

    return template('full_doc', search_term = search_term, 
                                site_name   = site_name, 
                                page_number = page_number, 
                                is_tag      = is_tag, 
                                doc_data    = doc_data)

###################################################
@route('/static/<filename:path>')
def server_static(filename):
    """ Get all the static files: css, images, fonts, etc.
    """
    return static_file(filename, root = 'static')

###################################################
def sort_by_name_of_size(list_to_be_sorted, sort_type):
    """ Get a list of tuples such as: [(site name, size), (site name, size)]
        and return it sorted by name or size.
    """
    sorted_list = []
    if sort_type == 'name':
        sorted_list = sorted(list_to_be_sorted, key = lambda x: x[0], reverse = False)
    else: # 'size'
        sorted_list = sorted(list_to_be_sorted, key = lambda x: x[1], reverse = True)

    return sorted_list

if __name__ == '__main__':

    # Chech if the user provided an IP and Port number. If not,
    # use default values.
    try:
        ip = sys.argv[1]
        port = sys.argv[2]
        print "Starting in production Mode: {}, {}.".format(ip, port)
    except IndexError:
        print "Starting in development Mode: localhost, 8000."
        ip = 'localhost'
        port = 8000

    # The metadata_shelve holds information about available sites and their sizes,
    # and the tags for each site, and their sizes.
    # {site_name: (sites metadata, tags metadata)}
    metadata_shelve = shelve.open('../Metadata/metadata.db', protocol = -1)

    s_e_sites = []
    tags_dict = {}
    site_names = metadata_shelve.keys()

    for site_name in site_names:
        s_e_sites.append((site_name, metadata_shelve[site_name][0]))
        tags_dict.update({site_name: metadata_shelve[site_name][1]})

    metadata_shelve.close()

    #Scan the /Index directory for all the available search engine indexes.
    index_pointers = SearchEngine.get_all_index_pointers('../Index', site_names)
    
    #Run the webserver
    run(host = ip, port = port, debug = True)
