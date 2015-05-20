import xml.etree.cElementTree as ET
from whoosh.fields import Schema, TEXT, KEYWORD
from whoosh.index import create_in
import shelve, os
import cPickle

"""
    Internal Stack Exchange - Indexer
    ---------------------------------
    This module scans the available datadumps in the /Datadumps directory,
    and parses the .xml files it finds their.
    It then builds a database that holds 'docs'. A 'doc' is a full
    question + answers dataset, and is referenced by it's question Id.

    It also creates a search engine index (using the Woosh library), that
    allows the user to index and search for docs using tags, keywords, etc.

"""
#####################################################################
#####################################################################
#@profile
def parse_xmls(path_to_xmls, site_name):
    """ Create a file <site_name>.db under the folder /db/.
        The file is a shelve, containing full docs of the named site. Key is the question id. 

        Note: this function usage of Shelve is optimzed for memory use, since the S.E datadumps
              can be huge. 
              All the .xml files are parsed into Shelves, so that their content will
              not need to stay in memory. The shelve is opened and read only when needed.
    """

    ################################################################################### 
    #Create a shelve to hold users' info: {user id : user info}
    shlv = shelve.open('../temp_db/tmp_users.db', 'n', protocol = -1, writeback = False)
    
    #Memory efficient method, allows for clearing the root.
    context     = ET.iterparse(path_to_xmls + 'Users.xml', events = ('start', 'end'))
    context     = iter(context)
    event, root = context.next() #get root

    print ("******* Starting Users.xml parsing ******")
    i = 0
    for (event, user) in context:
        if event == 'end' and user.tag=='row':
            shlv[user.attrib['Id']] = user.attrib
            
            #Log out progress to the caller.
            i += 1
            if i%5000==0: 
                shlv.sync() #Syncing the shelve clears the cache, and frees the memory.
                print ("Processed {} users so far.".format(i))
        root.clear()

    shlv.close()

    ################################################################################### 
    #Create a shelve to hold RelatedPosts info: {post id (id of relevant post) : list of related post id} 
    shlv = shelve.open('../temp_db/tmp_related_posts.db', 'n', protocol = -1, writeback = False)
    
    #Memory efficient method
    context     = ET.iterparse(path_to_xmls + 'PostLinks.xml', events = ('start', 'end'))
    context     = iter(context)
    event, root = context.next() #get root

    print ("******* Starting PostLinks.xml parsing ******")
    i = 0
    for (event, postlink) in context:
        if event == 'end' and postlink.tag=='row':

            #Check if the shelve already has the post_id key, and if not - create a new one.
            post_id               = postlink.attrib['PostId']
            list_of_related_links = shlv.get(post_id, [])
            list_of_related_links.append(postlink.attrib)
            shlv.update({post_id: list_of_related_links})

            #Log out progress to the user.
            i += 1
            if i%5000==0:
                shlv.sync()
                print ("Processed {} PostLinks so far.".format(i))
        root.clear()

    shlv.close()

    ################################################################################### 
    #Create a shelve to hold comments info: {post id : list of comments}
    shlv = shelve.open('../temp_db/tmp_comments.db', 'n', protocol = -1, writeback = True)

    #This shlv holds the user data.
    tmp_users_shlv = shelve.open('../temp_db/tmp_users.db', 'r', protocol = -1)

    #Memory efficient method
    context     = ET.iterparse(path_to_xmls + 'Comments.xml', events = ('start', 'end'))
    context     = iter(context)
    event, root = context.next()

    print ("******* Starting Comments.xml parsing ******")
    i = 0
    for (event, comment) in context:
        if event == 'end' and comment.tag=='row':

            if 'UserId' in comment.attrib.keys():
                #If the comment has a userId, we try to find the user's details
                #in the tmp_users_shlv. If there is none, we keep the field empty.
                user_id   = comment.attrib.get('UserId', '') 
                user_data = tmp_users_shlv.get(user_id, '') 
                comment.attrib.update({'User': user_data})

            post_id = comment.attrib['PostId']

            list_of_comments = shlv.get(post_id, [])
            list_of_comments.append(comment.attrib) 
            shlv.update({post_id:list_of_comments})

            #Log out progress to the user.
            i += 1
            if i%10000==0: 
                shlv.sync() 
                print ("Processed {} Comments so far.".format(i))
        root.clear()

    tmp_users_shlv.close()
    shlv.close()
 
    ################################################################################### 
    #Create a shelve to hold questions info only: {post id: post info}
    #Same for answers, but structure is: {parent id: list of posts}
    tmp_questions_shlv = shelve.open('../temp_db/tmp_questions.db', 'n', protocol = -1, writeback = True)
    tmp_answers_shlv   = shelve.open('../temp_db/tmp_answers.db', 'n', protocol = -1, writeback = True)

    tmp_comments_shlv  = shelve.open('../temp_db/tmp_comments.db', 'r', protocol = -1)
    tmp_users_shlv     = shelve.open('../temp_db/tmp_users.db', 'r', protocol = -1)
    tmp_postlinks_shlv = shelve.open('../temp_db/tmp_related_posts.db', 'r', protocol = -1)

    context     = ET.iterparse(path_to_xmls + 'Posts.xml', events = ('start', 'end'))
    context     = iter(context)
    event, root = context.next()

    print ("******* Starting Posts.xml parsing ******")
    i = 0
    for (event, post) in context:
        if event == 'end' and post.tag == 'row':
    
            if   (post.attrib['PostTypeId']=='1'):#A question
                tmp_questions_shlv[post.attrib['Id']] = post.attrib

            elif (post.attrib['PostTypeId']=='2'):#An Answer

                if 'OwnerUserId' in post.attrib.keys():
                    #If we have the user details, add them to the answer.
                    user_id   = post.attrib['OwnerUserId'] 
                    user_data = tmp_users_shlv.get(user_id, '')
                    post.attrib.update({'User': user_data})
 
                post_id = post.attrib['Id']

                list_of_postlinks = tmp_postlinks_shlv.get(post_id, [])
                post.attrib.update({'PostLinks': list_of_postlinks})

                list_of_comments = tmp_comments_shlv.get(post_id, [])
                post.attrib.update({'Comments': list_of_comments})

                parent_id = post.attrib['ParentId'] 

                list_of_answers = tmp_answers_shlv.get(parent_id, [])
                list_of_answers.append(post.attrib) 
                tmp_answers_shlv.update({parent_id:list_of_answers})

            i += 1
            if i%5000==0: 
                tmp_questions_shlv.sync()
                tmp_answers_shlv.sync() 
                print ("Processed {} Posts so far.".format(i)) 
 
        root.clear()

    tmp_postlinks_shlv.close()
    tmp_users_shlv.close()
    tmp_comments_shlv.close()
    tmp_questions_shlv.close()
    tmp_answers_shlv.close()


   #################################################################################### 
    # Create the shelve that will hold the full documents. {question id : doc} 
    full_docs_shlv     = shelve.open('../db/' + site_name +'.db', 'n', protocol = -1, writeback = True)

    tmp_posts_shlv     = shelve.open('../temp_db/tmp_questions.db', 'r', protocol = -1)
    tmp_users_shlv     = shelve.open('../temp_db/tmp_users.db', 'r', protocol = -1)
    tmp_answers_shlv   = shelve.open('../temp_db/tmp_answers.db', 'r', protocol = -1)
    tmp_comments_shlv  = shelve.open('../temp_db/tmp_comments.db', 'r', protocol = -1)
    tmp_postlinks_shlv = shelve.open('../temp_db/tmp_related_posts.db', 'r', protocol = -1)

    print ("******* Now creating full docs ******")
    i = 0
    num_of_docs = len(tmp_posts_shlv.keys())
    
    for id in tmp_posts_shlv.keys():

        doc_template = {'Comments'          : [], 
                        'PostLinks'         : [], 
                        'Answers'           : [],
                        'User'              : '',
                        'AcceptedAnswerId'  : '',
                        'Body'              : '',
                        'OwnerUserId'       : '',
                        'Title'             : '',
                        'Tags'              : '',
                        'Score'             : ''
                        }

        doc_template['Title'] = tmp_posts_shlv[id]['Title']
        doc_template['Tags']  = tmp_posts_shlv[id]['Tags']
        doc_template['Body']  = tmp_posts_shlv[id]['Body']
        doc_template['Score'] = tmp_posts_shlv[id]['Score']

        #return default value '' if none
        doc_template['AcceptedAnswerId'] = tmp_posts_shlv[id].get('AcceptedAnswerId', '')
        doc_template['OwnerUserId']      = tmp_posts_shlv[id].get('OwnerUserId', '')
        doc_template['User']             = tmp_users_shlv.get(doc_template['OwnerUserId'], '')

        #get all the comments, answers and postlinks. Return empty list if none.
        doc_template['Comments'] = tmp_comments_shlv.get(id, [])
        doc_template['Answers']  = tmp_answers_shlv.get(id, [])
        doc_template['PostLinks']  = tmp_postlinks_shlv.get(id, [])
        
        full_docs_shlv[id] = doc_template
 
        i += 1
        if i%1000==0:
            full_docs_shlv.sync()
            print ("Processed {} Full Docs out of {}.".format(i, num_of_docs)) 
 

    tmp_posts_shlv.close()
    tmp_users_shlv.close()
    full_docs_shlv.close()
    tmp_answers_shlv.close()
    tmp_comments_shlv.close()
    tmp_postlinks_shlv.close()


#####################################################################
#####################################################################
def create_schema(path_to_index_folder, db_name):
    """ Create a schema for the whoosh index. Return a pointer to the created index.
    """
    #The schema will hold the texts of a full document, 
    #the tags (As a comma seperated list) and the id of the question.
    db_docs_schema = Schema(doc_texts   = TEXT(),
                            doc_tags    = KEYWORD(commas = True, scorable = True),
                            question_id = TEXT(stored = True))

    db_docs_ix_pointer = create_in(path_to_index_folder, 
                                   schema    = db_docs_schema, 
                                   indexname = db_name + '_index')
    return db_docs_ix_pointer

#####################################################################
#####################################################################
def index_data(db_docs_ix_pointer, site_name):
    """ Do the search engine indexing of a data.
    """
    doc_writer = db_docs_ix_pointer.writer(limitmb = 512, procs = 4)

    full_docs_shlv = shelve.open('../db/' + site_name +'.db', 'r', protocol = -1)

    num_of_docs = len(full_docs_shlv.keys())
    i = 0

    print ("Now Indexing {}".format(site_name))
    for qid in full_docs_shlv.keys():

        #Display a progress report to the user.
        i+=1
        if (i%100 == 0):
            print ("Indexed doc {0} out of {1}".format(i,num_of_docs))

        #Extract all the texts from a document.
        tmp_text = ''
        tmp_text += full_docs_shlv[qid]['Title'] + ''
        tmp_text += full_docs_shlv[qid]['Body'] + ''

        tmp_text += ' '.join([comment['Text'] for comment in full_docs_shlv[qid]['Comments']]) + ' '
        tmp_text += ' '.join([answer['Body'] for answer in full_docs_shlv[qid]['Answers']]) + ' '

        for answer in full_docs_shlv[qid]['Answers']:
            tmp_text += ' '.join([ans_comment['Text'] for ans_comment in answer['Comments']]) + ' '

        #Convert the tags from the form <aa><bb> to ['aa','bb']
        tmp_tags = full_docs_shlv[qid]['Tags']
        l = tmp_tags.split("><")
        fixed_tags = [tag.replace("<", "").replace(">","") for tag in l]
        fixed_tags = unicode(",".join(fixed_tags))

        doc_writer.add_document(doc_texts       = unicode(tmp_text),
                                    doc_tags    = fixed_tags,
                                    question_id = unicode(qid))
    full_docs_shlv.close()
    doc_writer.commit()
    return 

#####################################################################
#####################################################################
def get_tags_information(path_to_datadumps, site_name):
    """ Get the tags of a single site, and their count.
        Return a list of the form: [(tag name, tag count)..]
    """
    tags_info = []
    tags_root = ET.parse(path_to_datadumps + site_name + '/Tags.xml').getroot()
    for tag in tags_root:
        tag_name = tag.attrib['TagName']
        count    = tag.attrib['Count']
        tags_info.append((tag_name, count))
    
    return tags_info

#####################################################################
#####################################################################
#####################################################################

def main(is_debug_mode):
    """ Iterate over all the avaiable datadumps, index them all and create a metadata file.
        in debug_mode, allow the user to select which sites to index.
    """

    path_to_datadumps = '../Datadumps/'
    site_names        = os.listdir(path_to_datadumps)
 
    #create a shelv to hold the metadata
    metadata_shelve = shelve.open('../Metadata/metadata.db', 'n', protocol = -1, writeback = False)
    
    for site_name in site_names:

        if is_debug_mode:
            #Allow the user to skip indexing of a datadump
            user_input = raw_input('Skip {}?'.format(site_name))
            if user_input=='y':
                continue

        #Parse the xmls, and index the documents
        parse_xmls(path_to_datadumps + site_name + '/', site_name)
        db_docs_ix_pointer = create_schema('../Index', site_name)
        index_data(db_docs_ix_pointer, site_name)

        #get the tags information
        tags_info = get_tags_information(path_to_datadumps, site_name) #[(tag name, size), ..]

        #Store metadata as shelve dict: {db_name, (number of docs, list of tags)}
        full_docs_shlv = shelve.open('../db/' + site_name +'.db', 'r', protocol = -1)
        metadata_shelve[site_name] = (len(full_docs_shlv.keys()), tags_info)
        full_docs_shlv.close()

    metadata_shelve.close()

    
if __name__ == "__main__":
    main(True)
