# Web Crawler
# Author : Mihalis Plelis

This web crawler scans URLs to find a specific text.

### Running the web crawler

The web crawler script receives up to 4 arguments which are the following:

1. -url "url"
	* Specify the URL to crawl.
2. -text "text"
	* Specify the text to look for.
3. -thr <number_of_threads>
	* Specify the number of threads to be started.
4. -pl <number_of_pages_limit>
	* Specify the number of pages to scan.

The **-url** and **-text** arguments are mandatory in order for the script to work.  
The **-thr** and the **-pl** arguments are optional.

Example: python webCrawler.py -url https://www.bbc.com -text have -thr 5 -pl 10
