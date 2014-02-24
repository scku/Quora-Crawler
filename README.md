Quora-Crawler
=============

This Python script makes use of the Selenium and chromedriver to crawl Quora.com. It starts at a specified root 
topic and traverses the child topics to build a hierarchy tree. It will first crawl and scrape all the questions within
all the topics. Meanwhile, it maintains a list of users who have either asked a question, answered, or upvoted. After
crawling the questions, it will crawl and scrape all the users.


####Requirements
Following needs to be installed for the script to run.

-selenium https://code.google.com/p/selenium/

-chromedriver https://code.google.com/p/selenium/wiki/ChromeDriver

-beautifulsoup http://www.crummy.com/software/BeautifulSoup/


####Outputs

For a given root topic, the script will extract the hierarchy of all the sub-topics and save it to topic_names.txt in the following format.

```
Level 1 Topic 1
Level 1 Topic 1 Level 2 Topic 1-1
Level 1 Topic 1 Level 2 Topic 1-1 Level 3 Topic 1-1-1
Level 1 Topic 1 Level 2 Topic 1-1 Level 3 Topic 1-1-2
Level 1 Topic 1 Level 2 Topic 1-1 Level 3 Topic 1-1-3
Level 1 Topic 1 Level 2 Topic 1-1 Level 3 Topic 1-2-1
Level 1 Topic 1 Level 2 Topic 1-1 Level 3 Topic 1-2-2
Level 1 Topic 2
Level 1 Topic 2 Level 2 Topic 2-1
Level 1 Topic 2 Level 2 Topic 2-2
Level 1 Topic 2 Level 2 Topic 2-2 Level 3 Topic 2-2-1
.
.
```
For each topic, the script will crawl and record all the questions under it. Then, the script will crawl each question and extract the following data and save it to answers.csv in the following format.

```
answer_id, question_id, user_id, date, number_of_upvotes, {{{users who upvoted}}}, {{{topics}}}, current_topic, {{{question_text}}} , {{{answer_text}}}

where...
answer_id = a unique global identifier for answers and is question_url-user_id 
question_id = a unique identifier of each question and is the question URL
user_id = the URL of the responder's page
{{{Users who voted}}} = user_id of ones who upvoted the answer, i.e. {{{user1_id, user2_id, etc.}}}
{{{topics}}} = the list of topics tagged on a question, separated with a comma
current_topic = the topic under which question is found
{{{question_text}}} = the question in plain text.
{{{answer_text}}} = the body of the answer in plain text.
```

After crawling all the questions-answers, the script will crawl all the users encountered previously. The user data will be saved in users.csv in the following format.

```
user_id, number_of_topics, number_of_blogs, number_of_questions, number_of_answers, number_of_edits, {{{followers}}}, {{{following}}}

where...
{{followers}}} = comma-separated lists of user_ids of those who follow this user
{{{following}}} = comma-separated lists of user_ids of those who this user follows
```
