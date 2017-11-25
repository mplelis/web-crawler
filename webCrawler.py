from html.parser import HTMLParser
from urllib.request import urlopen
from urllib import parse
import time
import threading
from queue import Queue
import sys


class LinkParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    # We are attaching the relative URL to the base URL.
                    newUrl = parse.urljoin(self.baseUrl, value)
                    # Skip URLs that don't start with our baseURL.
                    if newUrl.startswith(self.baseUrl):
                        self.links = self.links + [newUrl]

    def getLinks(self, url):
        self.links = []
        self.baseUrl = url
        response = urlopen(url)
        # Make sure that we are looking at HTML only
        if (response.getheader('Content-Type').startswith("text/html")):
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            return htmlString, self.links
        else:
            return "", []


class myThread(threading.Thread):

    url = "https://www.intersport.gr/"
    pagesToVisit = [url]

    def __init__(self, threadId, name, text, q):
        threading.Thread.__init__(self)
        self.threadID = threadId
        self.name = name
        self.text = text
        self.q = q

    def run(self):
        print("Starting " + self.name)
        spider(self.getName(), self.text, self.q)
        print("Exiting " + self.name)


# Method which does the spider work.
def spider(threadName, textToFind, q):
    global exitFlag
    textFound = False
    global urlSet
    global pagesVisited
    parser = LinkParser()

    # Main loop which gets all the links of the page.
    # Also searches the page for the word or string
    # In the getLinks function the web page is returned
    # (this is useful for searching for the word)
    # and a set of links from that web page also.
    # (this is useful for where to go next)
    # We are also adding the URLs in a set, to avoid
    # visiting any URL more than once.
    while not exitFlag and pagesVisited < pagesLimit:
        if not q.empty():
            currentUrl = q.get()
            try:
                print("Thread", threadName + ": Visiting:", currentUrl)
                data, links = parser.getLinks(currentUrl)
                queueLock.acquire()
                pagesVisited += 1
                queueLock.release()
                for link in links:
                    if link in urlSet:
                        continue
                    else:
                        q.put(link)
                        urlSet.add(link)
                if data.find(textToFind) > -1:
                    textFound = True
                    queueLock.acquire()
                    exitFlag = 1
                    queueLock.release()

            except Exception as e:
                print("Error during crawling:", str(e))

            if textFound:
                print("Thread", threadName + ": The text '" + textToFind + "' was found at", currentUrl)
            else:
                print("Thread", threadName + ": The text '" + textToFind + "' was not found at", currentUrl)
        time.sleep(1)


url = ''
text = ''
pagesLimit = 0
threadList = []
for index, value in enumerate(sys.argv):
    if value == '-url':
        try:
            if not sys.argv[index+1].startswith('http'):
                print('Unrecognised URL.')
                sys.exit()
            else:
                print('The URL to crawl is\n' + sys.argv[index+1])
                url = sys.argv[index+1]
        except IndexError as e:
            print("No URL was found. Exiting...")
            sys.exit()

    if value == '-text':
        try:
            print('Text to look for is\n' + sys.argv[index+1])
            text = sys.argv[index+1]
        except IndexError as e:
            print("No text was found. Exiting...")
            sys.exit()

    if value == '-pl':
        try:
            print('The pages limit to look for is', sys.argv[index+1])
            pagesLimit = int(sys.argv[index+1])
        except (IndexError, TypeError) as e:
            print("Pages limit is set to 1 be default.")

    if value == '-thr':
        try:
            for i in range(1, int(sys.argv[index+1])+1):
                threadList.append("t" + str(i))
        except (IndexError, TypeError) as e:
            print('Starting crawling with 1 thread by default.')
            threadList.append("t1")

if not url or not text:
    print("No URL or text was found. Exiting...")
    sys.exit()
if not threadList:
    print('Starting crawling with 1 thread by default.')
    threadList.append("t1")
if pagesLimit == 0:
    print("Setting pages limit to 10 pages by default")
    pagesLimit = 10

exitFlag = 0
pagesToVisit = [url]
urlSet = set()
urlSet.add(url)
pagesVisited = 0

queueLock = threading.RLock()
workQueue = Queue(0)
threads = []
threadID = 1
workQueue.put(url)

# Create new threads
for tName in threadList:
    thread = myThread(threadID, tName, text, workQueue)
    thread.start()
    threads.append(thread)
    threadID += 1

# Wait for all threads to complete
for t in threads:
    t.join()
print("Exiting Main Thread")
