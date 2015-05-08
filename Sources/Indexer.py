import xml.etree.cElementTree as ET
from whoosh.fields import Schema, TEXT, KEYWORD
from whoosh.index import create_in
import shelve, os
import cPickle

#####################################################################
#####################################################################
def parse_xmls(path_to_xmls):
    """ Gets the path to the folder where the datadump xml files are kept.
        This folder should contain: Posts.xml, Users.xml, Comments.xml, and PostLinks.xml.

        Process the data found in the xmls, and return a list of dictionaries. Each dict
        holds a full 'Document', which is a Question, all it's answers and their comments, etc.

        Each dict in the returned list is of the following structure:
        'Id': all the data in the post (dict of Title, Count, etc.), plus
              {'Comments': list of comments,
               'PostLinks': list of related posts links
               'Answers': list of answers}
    """

    #get all the questions from the file. create a dict of posts.
    posts_root = ET.iterparse(path_to_xmls + 'Posts.xml')
    
    questions = {}
    for (event, post) in posts_root:
        if post.tag == 'row' and (post.attrib['PostTypeId']=='1'):#A question
            questions[post.attrib['Id']] = post.attrib
            questions[post.attrib['Id']].update({'Comments': [], 'PostLinks': [], 'Answers': []})
    
    #get all the answers from the file. create a new dict: keys are post_id, value is post
    answers_root = ET.iterparse(path_to_xmls + 'Posts.xml')
    
    answers = {}
    for (event, post) in answers_root:
        if post.tag=='row' and (post.attrib['PostTypeId']=='2'):#An answer
    
            answers[post.attrib['Id']] = post.attrib
            answers[post.attrib['Id']].update({'Comments': [], 'PostLinks': []})
    
    #get all the comments from the file. 
    #for each comment, find the PostId it belongs to.
    #try to find the post in the questions. if found - add it to a 'comments' key, as a list.
    #if not, do the same for the answers.
    comments_root = ET.iterparse(path_to_xmls + 'Comments.xml')
    
    for (event, comment) in comments_root:
        if comment.tag=='row':
    
            post_id = comment.attrib['PostId']
    
            if post_id in questions:
                questions[post_id]['Comments'].append(comment.attrib)
            elif post_id in answers:
                answers[post_id]['Comments'].append(comment.attrib)
                
    #Create a users dict, where the id is the key.
    users_root = ET.iterparse(path_to_xmls + 'Users.xml')
    
    users = {}
    for (event, user) in users_root:
        if user.tag=='row':
            users[user.attrib['Id']] = user.attrib
            
    #get all the post_links
    #for each one, try to find the post in the questions and in the answers
    post_links_root = ET.iterparse(path_to_xmls + 'PostLinks.xml')
    
    for (event, post_link) in post_links_root:
        if post_link.tag=='row':
    
            post_id = post_link.attrib['PostId']
            if post_id in questions:
                questions[post_id]['PostLinks'].append(post_link.attrib)
            elif post_id in answers:
                answers[post_id]['PostLinks'].append(post_link.attrib)
    
    #Now go over all the answers, and find the related question: add the answers to the questions.
    for id in answers.keys():
        parent_id = answers[id]['ParentId'] 
        
        questions[parent_id]['Answers'].append(answers[id])

    return questions

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
def index_data(db_docs_ix_pointer, db_name, data):
    """ Do the actual indexing of a data.
    """
    doc_writer = db_docs_ix_pointer.writer(limitmb = 512, procs = 4)

    #To be used in reporting the indexing current status
    num_of_docs = len(data.keys())
    i = 0

    for qid in data.keys():

        #Display a progress report to the user.
        i+=1
        if (i%100 == 0):
            print ("Indexed doc {0} out of {1}".format(i,num_of_docs))

        #Extract all the texts from a document.
        tmp_text = ''
        tmp_text += data[qid]['Title'] + ''
        tmp_text += data[qid]['Body'] + ''

        tmp_text += ' '.join([comment['Text'] for comment in data[qid]['Comments']]) + ' '
        tmp_text += ' '.join([answer['Body'] for answer in data[qid]['Answers']]) + ' '

        for answer in data[qid]['Answers']:
            tmp_text += ' '.join([ans_comment['Text'] for ans_comment in answer['Comments']]) + ' '

        #Convert the tags from the form <aa><bb> to ['aa','bb']
        tmp_tags = data[qid]['Tags']
        l = tmp_tags.split("><")
        fixed_tags = [tag.replace("<", "").replace(">","") for tag in l]
        fixed_tags = unicode(",".join(fixed_tags))

        doc_writer.add_document(doc_texts       = unicode(tmp_text),
                                    doc_tags    = fixed_tags,
                                    question_id = unicode(qid))
    
    doc_writer.commit()
    return 

#####################################################################
#####################################################################
def get_tags_information(path_to_datadumps, datadump):
    """ Get the tags of a single site, and their count.
        Return a list of the form: [(tag name, tag count)..]
    """
    tags_info = []
    tags_root = ET.parse(path_to_datadumps + datadump + '/Tags.xml').getroot()
    for tag in tags_root:
        tag_name = tag.attrib['TagName']
        count    = tag.attrib['Count']
        tags_info.append((tag_name, count))
    
    return tags_info

#####################################################################
#####################################################################
#####################################################################
if __name__ == "__main__":
    """ When this module is called stand-alone, it will iterate over all the avaiable 
        datadumps, index them all and create a metadata file.
    """

    path_to_datadumps = '../Datadumps/'
    datadumps = os.listdir(path_to_datadumps)
 
    #create a shelv to hold the metadata
    metadata_shelve = shelve.open('../Metadata/metadata.db', protocol = -1)
    
    for datadump in datadumps:

        #Allow the user to skip indexing of a datadump
        user_input = raw_input('Skip {}?'.format(datadump))
        if user_input=='y':
            continue

        #Index the documents
        data = parse_xmls(path_to_datadumps + datadump + '/')
        db_docs_ix_pointer = create_schema('../Index', datadump)
        index_data(db_docs_ix_pointer, datadump, data)

        #get the tags information
        tags_info = get_tags_information(path_to_datadumps, datadump) #[(tag name, size), ..]

        #Store metadata as shelve dict: {db_name, (number of docs, list of tags)}
        metadata_shelve[datadump] = (len(data.keys()), tags_info)

        #Store the datadump data as a pickle object.
        f = open('../Data/'+datadump+'_db', 'w')
        cPickle.dump(data, f)
        f.close()    

    metadata_shelve.close()
    
