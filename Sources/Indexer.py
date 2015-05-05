import xml.etree.cElementTree as ET

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


#we now have a dict of questions with their answers and all.

#import pdb
#pdb.set_trace()
#
#import pprint 
#pprint.pprint(questions['22'])
#pprint.pprint(answers['13'])
#pprint.pprint(users['13'])

if __name__ == "__main__":

    questions = parse_xmls('../Datadumps/Beer/')
    import pprint 
    pprint.pprint(questions['22'])
    #
