# LING 360 Final Project Write-up

## What did I set out to accomplish and why?
The idea for this project probably started on my mission. I was serving in Germany at the time, but was serving in an area that was well known for how many Chinese college students would come to study engineering. My mission president, compelled to try and take advantage of this, asked me to start to learn Chinese, in addition to my eight-month-old German. After thinking about it, I obliged. (Although I will admit now that my Chinese level never really got to the same level as my German). In any case, after this arrangement the mission office ordered me some materials, in which was included a [*Book of Mormon: Mandarin Language Study Edition*](https://media.ldscdn.org/pdf/lds-scriptures/book-of-mormon/book-of-mormon-language-study-edition-34406-cmn_eng.pdf), a resource given to missionaries which had the text of the Book of Mormon formatted into three columns: traditional Chinese characters, Mandarin pinyin (a Romanization of sorts), and English. I thought that this edition of the Book of Mormon was just the coolest, however ended up begin not very useful, as I was studying the simplified character system, and that frustrated me that, despite this awesome resource I still had to have multiple copies of the Book of Mormon open simultaneously in order to study. Later in my mission we were allowed to use thebible.org's [Parallel Reader](https://thebible.org/gt/index), from which I also took a great deal of design inspiration, however I would only focus on two texts at a time.

At the beginning of the project, the goals I had set for myself were:
* Add six languages:
  * English
  * Spanish
  * French
  * Russian
  * Chinese (simplified)
  * Arabic
* Have the project be hosted on a website
* Create a database for the texts

The six languages are the six 'official' languages of the United Nations, which I thought would be a good starting point. I decided to put this project on a website because I wanted it to be open and accessible to anyone with a web browser. I decided to put the textual information into a database because I think it provided a few advantages over dynamically scraping the texts, namely: (1) it provides the opportunity to manually clean up data, (2) load times would be quicker out of a database, (3) I'm not sure how I would be able to run a Python program from inside a JavaScript program, and just hooking into the database from these two languages separately was a task with which I was already familiar, as a result of my concurrent web development course.

## What were the various steps I took to accomplish my goal?
1. Using `BeautifulSoup4` scrape the data from [www.churchofjesuschrist.org](https://www.churchofjesuschrist.org/study/scriptures/bofm?lang=eng)
  1. Using the element inspector, explore the general layout of the webpage
  2. Obtain a list of how many chapters each book of the Book of Mormon has
  3. Scrape the text using the url formatting: `https://www.churchofjesuschrist.org/study/scriptures/bofm/(book_to_scrape)/(chapter_num)?lang=(language_to_scrape)`
  4. Save the results to a Python dictionary, and then to a JSON file
2. Add these results to a database
  1. Using `pymongo` iterate through each JSON file from step 1.4
  2. Remove extraneous data (see Challenges)
  3. Add a `meta` tag to the JSON data containing language, book, and chapter number information.
  4. Add the document to `MongoDB`
  * As a footnote, I'm aware that steps 1 and 2 could have been combined as a single step, however scraping and then adding to a database all in one go (although I will admit is more streamlined), made step 2 considerably slower, because once the text files had been downloaded, `databaser.py` could just rip through the files. Also that process wouldn't need to leave a JSON backup, which I ended up needing in order to transfer my database to my web server.
3. Using Vue, Node, and Express, create a website
  1. I won't write anything about this, to spare you of the details and because that information would be outside of the scope of this class anyway.

## What challenges did I run into and how did I overcome them?
As with all projects of this size, I of course ran into an innumerable number of programs, each of these problems varying in size and scope. I will insert three:

After deciding to add Arabic to my my list of supported languages, I went about trying to obtain a digital copy of the Arabic Book of Mormon. Getting the text in `.pdf` form was simple enough, as it was easily accessible on the Church's site. However, this PDF had no actual textual data in it, but was rather just a list of scans of the text, which made it impossible to use something like `PyPDF2`. After being disappointed in the support for Arabic optical character recognition services, I just decided to make the difficult decision to not support Arabic.

Another issue I ran into was having my project be blocked from the accessing the Church's website for making too many requests (around 2,100 page requests because at this point it was quite easy to add new languages, so I added support for German, Malagasy, Finnish, and Swedish, in addition to the other five languages). The workaround for this was that I had my program skip over scraping the texts, for which I already had a JSON file.

Another difficulty I ran into was the many different heading types in LDS edition of the Book of Mormon. Chapters like [1 Nephi 1](https://www.churchofjesuschrist.org/study/scriptures/bofm/1-ne/1?lang=eng), [Alma 36](https://www.churchofjesuschrist.org/study/scriptures/bofm/alma/36?lang=eng) for example, contain more information than simply a chapter title and summary. The way that I worked around this was that I created a `header` sub-class in my Python dictionary design, and then allowed `BeautifulSoup` to save the dictionary key as that same name as the HTML id (while eliminating trailing numerals which occurred). After getting a list of all possible `header` keys, I was able to search through my JSON data and look at their corresponding chapters to find a pattern that the header tags were presented in a concrete order (provided each tag existed). Knowing this order, I was able to recreate this order in my site.

## What have you learned in this class that (a) helped you with your final project and (b) will/might help you in your future?
a. This class taught my how to program in Python, about which I had not yet learned. It also taught my about the Python dictionary data structure, and about `BeautifulSoup` and webscraping. Also iterating through text files was a general skill, to which I was introduced in this class.

b. I think that the project in and of itself may be to the interest of some employers. Webscraping is also a skill which I'm sure is quite helpful in the work force. Creating a database is also a helpful skill.

### Word count: 1149
