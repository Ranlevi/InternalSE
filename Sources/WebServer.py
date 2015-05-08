from bottle import route, run, template, static_file, request
import shelve
import SearchEngine
import cPickle

"""
    fix the users not in data
    decide on a standard naming scheme.
    TODO: add loging and better print out
          add self test for deployment
          profile memory
          document in sphinx
          add py3 support
          make the indexer a standalone app, for someone to build a front end. 
"""
@route('/')
def index():
    sort_type = request.query.sort_type or 'name'
    sorted_s_e_sites_list = sort_by_name_of_size(s_e_sites, sort_type)
   
    return template('index', s_e_sites = sorted_s_e_sites_list)

@route('/site')
def site():
    site_name = request.query.site_name
    sort_type = request.query.sort_type or 'name'
    site_tags = tags_dict[site_name] 

    sorted_site_tags = sort_by_name_of_size(site_tags, sort_type)
    return template('site', site_name = site_name, site_tags = sorted_site_tags)

@route('/search')
def search():

    tag = request.query.tag
    site_name = request.query.site_name
    page_number = request.query.page_number or '1'
    index_pointer = index_pointers[site_name]

    current_data = current_site.get_site_data(site_name)
    search_results = SearchEngine.get_search_results(index_pointer, tag, int(page_number,10), current_data)
    
    return template('search_results', tag_name = tag, search_results = search_results)

#get all the static files (css, images, fonts..)
@route('/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root = 'static')

def sort_by_name_of_size(list_to_be_sorted, sort_type):
    sorted_list = []
    if sort_type == 'name':
        sorted_list = sorted(list_to_be_sorted, key = lambda x: x[0], reverse = False)
    else: # 'size'
        sorted_list = sorted(list_to_be_sorted, key = lambda x: x[1], reverse = True)

    return sorted_list
        
class CurrentSite(object):
    
    def __init__(self, site_name):
        self.site_name = site_name

    def load_site_data(self):
        f = open('../Data/'+self.site_name+'_db', 'r')
        self.data = cPickle.load(f)
        f.close()    

    def get_site_data(self, site_name):
        if self.site_name == site_name:
            return self.data
        else:
            self.site_name = site_name
            self.load_site_data() 
            return self.data


if __name__ == '__main__':

    current_data = None

    metadata_shelve = shelve.open('../Metadata/metadata.db', protocol = -1)

    s_e_sites = []
    tags_dict = {}
    site_names = metadata_shelve.keys()

    for site_name in site_names:
        s_e_sites.append((site_name, metadata_shelve[site_name][0]))
        tags_dict.update({site_name: metadata_shelve[site_name][1]})
    metadata_shelve.close()

    index_pointers = SearchEngine.get_all_index_pointers('../Index', site_names)
    
    current_site = CurrentSite(site_names[0])   
    current_site.load_site_data()

    #get the sites and size
    run(host = 'localhost', port = 8000, debug = True)
