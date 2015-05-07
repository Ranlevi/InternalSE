import xml.etree.cElementTree as ET
from whoosh.fields import Schema, TEXT, KEYWORD
from whoosh.index import create_in
import shelve, os

#import pdb

def parse_xmls(path_to_xmls):
    #get all the questions from the file. create a dict of posts.

    posts_root = ET.iterparse(path_to_xmls + 'Posts.xml')
    
    questions = {}
    for (event, post) in posts_root:
        if post.tag == 'row' and (post.attrib['PostTypeId']=='1'):
            questions[post.attrib['Id']] = post.attrib
            questions[post.attrib['Id']].update({'Comments': [], 'PostLinks': [], 'Answers': []})
    
    #get all the answers from the file. create a dict: keys are post_id, value is post
    
    
    answers_root = ET.iterparse(path_to_xmls + 'Posts.xml')
    
    answers = {}
    for (event, post) in answers_root:
        if post.tag=='row' and (post.attrib['PostTypeId']=='2'):
    
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
    
    #Now go over all the answers, and find the related question.
    
    for id in answers.keys():
        parent_id = answers[id]['ParentId'] 
        
        questions[parent_id]['Answers'].append(answers[id])

    return questions

def create_schema(path_to_index_folder, db_name):

    db_docs_schema = Schema(doc_texts   = TEXT(),
                            doc_tags    = KEYWORD(commas = True, scorable = True),
                            question_id = TEXT(stored = True))

    db_docs_ix_pointer = create_in(path_to_index_folder, 
                                   schema    = db_docs_schema, 
                                   indexname = db_name + '_index')
    return db_docs_ix_pointer

def index_data(db_docs_ix_pointer, db_name, data):

    doc_writer = db_docs_ix_pointer.writer(limitmb = 512, procs = 4)

    num_of_docs = len(data.keys())
    i = 0

    for qid in data.keys():

        i+=1
        if (i%100 == 0):
            print ("Indexed doc {0} out of {1}".format(i,num_of_docs))

        tmp_text = ''
        tmp_text += data[qid]['Title'] + ''
        tmp_text += data[qid]['Body'] + ''

        tmp_text += ' '.join([comment['Text'] for comment in data[qid]['Comments']]) + ' '
        tmp_text += ' '.join([answer['Body'] for answer in data[qid]['Answers']]) + ' '

        for answer in data[qid]['Answers']:
            tmp_text += ' '.join([ans_comment['Text'] for ans_comment in answer['Comments']]) + ' '

        tmp_tags = data[qid]['Tags']
        l = tmp_tags.split("><")
        fixed_tags = [tag.replace("<", "").replace(">","") for tag in l]
        fixed_tags = unicode(",".join(fixed_tags))

        doc_writer.add_document(doc_texts = unicode(tmp_text),
                                    doc_tags  = fixed_tags,
                                    question_id = unicode(qid))
    
    doc_writer.commit()
    return 

         

#we now have a dict of questions with their answers and all.
if __name__ == "__main__":

    path_to_datadumps = '../Datadumps/'
    datadumps = os.listdir(path_to_datadumps)
 
    #create a shelv
    metadata_shelve = shelve.open('../Metadata/metadata.db', protocol = -1)
    
    for datadump in datadumps:

        data = parse_xmls(path_to_datadumps + datadump + '/')
        db_docs_ix_pointer = create_schema('../Index', datadump)
        index_data(db_docs_ix_pointer, datadump, data)

        metadata_shelve[datadump] = len(data.keys())

    metadata_shelve.close()
    

    #import pprint 
    #pprint.pprint(questions['22'])
    #
    #questions = parse_xmls('../Datadumps/CodeReview/')
    #pprint.pprint(questions['22'])

    #data = parse_xmls('../Datadumps/CodeReview/')
    #db_docs_ix_pointer = create_schema('../Index', 'CodeReview')
    #index_data(db_docs_ix_pointer, 'CodeReview', data)
