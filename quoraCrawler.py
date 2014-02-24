from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os

DEBUG = 1

def crawlTopicHierarchy():
    if (DEBUG): print "In crawlTopicHierarchy()..."
    
    # Create files for topic names and topic URLs
    file_topic_names = open("topic_names.txt", mode = 'w')
    file_topic_urls = open("topic_urls.txt", mode = 'w')

    # Starting node link
    url = 'http://www.quora.com/Preventive-Medicine?share=1'

    depth = 0
    topic_names_hierarchy = ""

    # Create stack to keep track of links to visit and visited
    urls_to_visit = []
    urls_visited = []
    # Add root to stack
    urls_to_visit.append([url, depth])

    #if (DEBUG): print urls_to_visit

    while (len(urls_to_visit)):
        # Pop stack of stack to get URL and current depth
        url, current_depth = urls_to_visit.pop()
        if (DEBUG): print 'Current url:{0} current depth:{1} depth:{2}'.format(url, str(current_depth), str(depth))

        page_name = url[21:].split('?')[0]
        if (DEBUG): print page_name
        
        urls_visited.append([url, page_name])

        if (current_depth < depth):
            for i in range(depth - current_depth):
                j = topic_names_hierarchy.rfind(" ")
                if (j != -1):
                    topic_names_hierarchy = topic_names_hierarchy[:j]
            depth = current_depth

        # Record topic Name
        if (depth == 0):
            file_topic_names.write((page_name + '\n').encode('utf-8'))
        else:
            file_topic_names.write((topic_names_hierarchy + " " + page_name + '\n').encode('utf-8'))

        depth += 1
        # Record topic URL
        file_topic_urls.write((url + '\n').encode('utf-8'))

        url_about = url.split('?')[0] + "/about?share=1"

        chromedriver = "chromedriver"   # Needed?
        os.environ["webdriver.chrome.driver"] = chromedriver    # Needed?
        browser = webdriver.Chrome()
        browser.get(url_about)

        # Fetch /about page
        src_updated = browser.page_source
        src = ""
        while src != src_updated:
            time.sleep(.5)
            src = src_updated
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            src_updated = browser.page_source

        html_source = browser.page_source

        soup = BeautifulSoup(html_source)
        raw_topics = soup.find_all(attrs={"class":"topic_name"})
        #print raw_topics

        # Split to get just child topics
        split_html = html_source.split('<strong>Child Topics</strong>')
        if (len(split_html) == 1):
            browser.quit()
        else:
            split_html = split_html[1]
            # Split to separate child topics
            split_child = split_html.split('<div class="topic_list_item"')
            child_count = 0

            for i in range(1, len(split_child)):
                part = split_child[i].split('class="light"')[0]
                part_soup = BeautifulSoup(part)
                for link in part_soup.find_all('a', href=True):
                    link_url = "http://www.quora.com" + link['href'] + "?share=1"
                    urls_to_visit.append([link_url, depth])
                    child_count += 1

            browser.quit()
            if (topic_names_hierarchy):
                topic_names_hierarchy += " " + page_name
            else:
                topic_names_hierarchy += page_name
            if (DEBUG): print "Links read: " + str(child_count)

    # File cleanup
    file_topic_names.close()
    file_topic_urls.close()

    return urls_visited

# Crawl each topic url and save each question url
def crawlTopicQuestions(topic_urls):
    if (DEBUG): print "In crawlTopicQuestions()...", topic_urls
    
    # Create a topic page and download all question text and URL
    file_question_urls =  open("question_urls.txt", mode = 'w')
    file_topic_urls = open("topic_urls.txt", mode = 'r')

    total = 0

    for topic in range(len(topic_urls)):
        current_url = topic_urls[topic][0]
        current_topic = topic_urls[topic][1]
        
        if (not current_url): # Needed?
            break

        # Open browser
        chromedriver = "chromedriver"   # Needed?
        os.environ["webdriver.chrome.driver"] = chromedriver    # Needed?
        browser = webdriver.Chrome()
        browser.get(current_url)

        # Fetch current page
        #fw = open("page", mode = 'w')
        src_updated = browser.page_source
        src = ""
        while src != src_updated:
            time.sleep(.5)
            src = src_updated
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            src_updated = browser.page_source

        html_source = browser.page_source
        #fw.write(html_source.encode('utf8'))
        #fw.close()
        browser.quit()

        split_html = html_source.split("<h3>")

        for i in range(1,len(split_html)):
            part = split_html[i].split('</h3>')[0]
            part_soup = BeautifulSoup(part)
            if ("<div") in part:
                #print part_soup.get_text()
                for link in part_soup.find_all('a' , href=True):
                    link_url = "http://www.quora.com" + link['href'] + "?share=1"
                    file_question_urls.write((link_url + " " + current_topic + '\n').encode('utf-8'))
                    total += 1

    print "Total questions:{0}".format(str(total))
    return 0

# Crawl a question URL and save data into a csv file
def crawlQuestionData(file):
    if (DEBUG): print ("In crawlQuestionData...")
    
    # Open question url file
    file_question_urls = open(file, mode = 'r')
    file_data = open("answers.csv", mode = 'w')
    file_users = open("users.txt", mode = 'w')
    
    current_line = file_question_urls.readline()
    while (current_line):
        if (DEBUG): print "***", current_line
        question_id = current_line.split(" ")[0]
        current_topic = current_line.split(" ")[1].rstrip('\n')
        if (DEBUG): print question_id, "-", current_topic
    
        # Open browser to current_question_url
        chromedriver = "chromedriver"   # Needed?
        os.environ["webdriver.chrome.driver"] = chromedriver    # Needed?
        browser = webdriver.Chrome()
        browser.get(question_id)
    
        # Fetch page
        src_updated = browser.page_source
        src = ""
        while src != src_updated:
            time.sleep(.5)
            src = src_updated
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            src_updated = browser.page_source
        
        # Load "more" of the users who upvoted
        more_link = browser.find_elements_by_partial_link_text("ore")
        #if (DEBUG): print more_link
        if (DEBUG): print "Number of clicks:", len(more_link)
        for each in more_link:
            if (DEBUG): print "Click on:", each
            each.click()
            time.sleep(.5)
        
        html_source = browser.page_source
        browser.quit()
        
        # Find topics tagged on question
        topic_string = ""
        topic_list_soup = BeautifulSoup(html_source)
        topic_raw = topic_list_soup.find_all(attrs={"class":"topic_list_item"})
        for x in range(len(topic_raw)):
            #if (DEBUG): print topic_raw[x]
            topic_raw_soup = BeautifulSoup(str(topic_raw[x]))
            for topic in topic_raw_soup.find_all('a', href=True):
                if (topic_string):
                    topic_string += ", " + topic['href'].split("/")[1]
                else:
                    topic_string += topic['href'].split("/")[1]
        topic_string = "{{{" + topic_string + "}}}"
        if (DEBUG): print "Topic List:{0}".format(topic_string)
        
        # Find question text
        question_text = html_source.split("<h1>")[1]
        question_text = question_text.split("</h1>")[0]
        question_text = question_text.split(">")
        question_text = "{{{" + question_text[len(question_text)-1] + "}}}"
        if (DEBUG): print "Question text:{0}".format(question_text)
        
        # Split html to parts
        split_html = html_source.split('<div class="e_col w5 answer_border answer_text_wrapper">')
        if (DEBUG): print "Length of split_html:{0}".format(len(split_html))
        for i in range(1, len(split_html)):
            part = split_html[i]
            if (DEBUG): print part
            part_soup = BeautifulSoup(part)
            
            # Find number of upvotes
            upvote = part_soup.find(attrs={"class":"numbers"})
            upvote = (str(upvote).split("</span")[0]).split(">")[1]
            if (DEBUG): print "Upvote:{0}".format(upvote)

            # Find user id
            user_id_raw = part_soup.find(attrs={"class":"answer_user_wrapper"})
            user_id_soup = BeautifulSoup(str(user_id_raw))
            user_id = user_id_soup.find('a', href=True)
            if (not user_id):
                continue
            user_id = "http://www.quora.com" + user_id['href'] + "?share=1"
            file_users.write((user_id + '\n').encode('utf8'))
            if (DEBUG): print user_id
        
            # Set answer id as question url + user id
            answer_id = question_id + "-" + user_id
        
            # Find users (user id) who voted
            users_voted = ""
            users_voted_raw = part_soup.find_all(attrs={"class":"user"})
            #if (DEBUG): print users_voted_raw
            for x in range(1, len(users_voted_raw)):
                users_voted_soup = BeautifulSoup(str(users_voted_raw[x]))
                for user in users_voted_soup.find_all('a', href=True):
                    if (users_voted):
                        users_voted += ", " + "http://www.quora.com" + user['href'] + "?share=1"
                    else:
                        users_voted += "http://www.quora.com" + user['href'] + "?share=1"
                    file_users.write(("http://www.quora.com" + user['href'] + "?share=1" + '\n').encode('utf-8'))
            users_voted = "{{{" + users_voted + "}}}"
            
            # Find answer text
            answer_text = ""
            answer_text = part_soup.find(attrs={"class":"answer_content"}).text
            answer_text = answer_text.split("Embed Quote")[0]
            if (DEBUG): print answer_text
            answer_text = "{{{" + answer_text + "}}}"

            # Find date
            date = ""
            date = part_soup.find(attrs={"class":"answer_permalink"}).text
            if (DEBUG): print "Date:", date
            
            # Write to csv file
            s = answer_id + ", " + question_id + ", " + user_id + ", " + str(date) + ", " + str(upvote) + ", " + users_voted + ", " + topic_string + ", " + current_topic + ", " + question_text + ", " + answer_text
            file_data.write((s + '\n').encode('utf8'))
        current_line = file_question_urls.readline()

    file_question_urls.close()
    file_data.close()
    file_users.close()
    return 0

# Gather user data and save into csv file
def crawlUser():
    if (DEBUG): print "In crawlUser..."
    
    unique_users = set(open("users.txt").readlines())
    bar = open('temp.txt', 'w').writelines(set(unique_users))
    
    file_users = open("temp.txt", mode='r')
    file_users_csv = open("users.csv", mode='w')
    total = 0
    
    current_line = file_users.readline()
    while(current_line):
        
        # Open browser to current_question_url
        chromedriver = "chromedriver"   # Needed?
        os.environ["webdriver.chrome.driver"] = chromedriver    # Needed?
        browser = webdriver.Chrome()
        browser.get(current_line)
        
        # Fetch page
        src_updated = browser.page_source
        src = ""
        while src != src_updated:
            time.sleep(.5)
            src = src_updated
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
        # Find user id
        user_id = browser.current_url
        html_source = browser.page_source
        browser.quit()
        
        source_soup = BeautifulSoup(html_source)
        part = source_soup.find_all(attrs={"class":"link_label"})
        part_soup = BeautifulSoup(str(part))
        raw_info = part_soup.text.split(",")
        if (DEBUG): print raw_info
        
        for x in range(1, len(raw_info)):
            #if (DEBUG): print raw_info[x]
            key = raw_info[x].split(" ")[1]
            value = raw_info[x].split(" ")[2]
            if key == "Topics":
                num_topics = value
                if (DEBUG): print "num_topics:", num_topics
            elif key == "Blogs":
                num_blogs = value
                if (DEBUG): print "num_blogs:", num_blogs
            elif key == "Questions":
                num_questions = value
                if (DEBUG): print "num_questions:", num_questions
            elif key == "Answers":
                num_answers = value
                if (DEBUG): print "num_answers:", num_answers
            elif key == "Edits":
                value = value.split("]")[0]
                num_edits = value
                if (DEBUG): print "num_edit:", num_edits
        
        # Find followers
        followers_url = user_id.split('?')[0] + "/followers?share=1"
        browser = webdriver.Chrome()
        browser.get(followers_url)

        src_updated = browser.page_source
        src = ""
        while src != src_updated:
            time.sleep(.5)
            src = src_updated
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            src_updated = browser.page_source
        followers_html_source = browser.page_source
        browser.quit()

        followers_soup = BeautifulSoup(followers_html_source)
        followers_raw = followers_soup.find_all(attrs={"class":"user"})
        if (DEBUG): print "num of followers:", len(followers_raw)

        followers = ""
        count = 0
        for x in range(1, len(followers_raw)):
            followers_soup = BeautifulSoup(str(followers_raw[x]))
            for follower in followers_soup.find_all('a', href=True):
                count += 1
                if (followers):
                    followers += ", " + "http://www.quora.com" + follower['href'] + "?share=1"
                else:
                    followers += "http://www.quora.com" + follower['href'] + "?share=1"

        if (DEBUG): print "Followers count:", count
        followers = "{{{" + followers + "}}}"

        # Find following
        following_url = user_id.split('?')[0] + "/following?share=1"
        browser = webdriver.Chrome()
        browser.get(following_url)
        
        src_updated = browser.page_source
        src = ""
        while src != src_updated:
            time.sleep(.5)
            src = src_updated
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            src_updated = browser.page_source
        following_html_source = browser.page_source
        browser.quit()
        
        following_soup = BeautifulSoup(following_html_source)
        following_raw = following_soup.find_all(attrs={"class":"user"})
        if (DEBUG): print "num of following:", len(following_raw)
        
        following = ""
        count = 0
        for x in range(1, len(following_raw)):
            following_soup = BeautifulSoup(str(following_raw[x]))
            for each_following in following_soup.find_all('a', href=True):
                count += 1
                if (following):
                    following += ", " + "http://www.quora.com" + each_following['href'] + "?share=1"
                else:
                    following += "http://www.quora.com" + each_following['href'] + "?share=1"

        if (DEBUG): print "Following count:", count
        following = "{{{" + following + "}}}"

        s = user_id + ", " + str(num_topics) + ", " + str(num_blogs) + ", " + str(num_questions) + ", " + str(num_answers) + ", " + str(num_edits) + ", " + followers + ", " + following
        if (DEBUG): print s
        file_users_csv.write((s + '\n').encode('utf8'))
        current_line = file_users.readline()
        total += 1
    
    file_users.close()
    file_users_csv.close()
    print "Total users:{0}".format(str(total))
    return 0

# Reads a line of users.csv format and return the fields in separate variabes
def parseUsersFile(line):
    parts = line.split(',', 6)
    user_id = parts[0]
    number_of_upvotes = parts[1]
    number_of_blogs = parts[2]
    number_of_questions = parts[3]
    number_of_answers = parts[4]
    number_of_edits = parts[5]
    rest = parts[6]
    followers = rest.split('}}}', 2)[0].split('{{{')[1]
    following = rest.split('}}}', 2)[1].split('{{{')[1]
    return user_id, number_of_upvotes, number_of_blogs, number_of_questions, number_of_answers, number_of_edits, followers, following

# Reads a line of answers.csv format and return the fields in separate variabes
def parseAnswersFile(line):
    parts = line.split(',', 5)
    answer_id = parts[0]
    question_id = parts[1]
    user_id = parts[2]
    date = parts[3]
    number_of_upvotes = parts[4]
    rest = parts[5]
    users_who_upvoted = (rest.split('}}}')[0]).split('{{{')[1]
    topics = (rest.split('}}}',3)[1]).split('{{{')[1]
    if (DEBUG): print topics
    current_topics = (rest.split('}}}',3)[2]).split(',',2)[1].split(',',2)[0]
    if (DEBUG): print current_topics
    question_text = (rest.split('}}}',4)[2]).split('{{{')[1]
    if (DEBUG): print question_text
    answer_text = (rest.split('}}}',5)[3]).split('{{{')[1]
    if (DEBUG): print answer_text
    return answer_id, question_id, user_id, number_of_upvotes, users_who_upvoted, topics, current_topics, question_text, answer_text

def main():
    topics = crawlTopicHierarchy()
    crawlTopicQuestions(topics)
    crawlQuestionData("question_urls.txt")
    crawlUser();
    return 0

if __name__ == "__main__": main()
