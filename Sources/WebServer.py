from bottle import route, run, template, static_file, request
import shelve


"""

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

    if sort_type == 'name':
        sorted_s_e_sites_list = sorted(s_e_sites, key = lambda x: x[0], reverse = False)
    else: # 'size'
        sorted_s_e_sites_list = sorted(s_e_sites, key = lambda x: x[1], reverse = True)
   
    return template('index', s_e_sites = sorted_s_e_sites_list)

#get all the static files (css, images, fonts..)
@route('/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root = 'static')


if __name__ == '__main__':

    metadata_shelve = shelve.open('../Metadata/metadata.db', protocol = -1)

    s_e_sites = []
    for site_name in metadata_shelve.keys():
        s_e_sites.append((site_name, metadata_shelve[site_name]))

    metadata_shelve.close()
   
    #get the sites and size
    run(host = 'localhost', port = 8000, debug = True)
