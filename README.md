# Project-E.M.M.A.

(Extended Multi Management Assistant)

This is my very first Python project. It is designed to help me keep track of all my expenses and finances (and a couple of gimmicks) in conjuction with a Google Spreadsheet and a PostgreSQL database all hosted on an AWS Linux instance. 

EMMA is constantly evolving as it is something I have been using every day for the past year. At first it used to enter a specific Goolge Keep note to gather my expense info and then add it to the Spreadsheet. Unfortunately as Google Keep has no public API after the bot got more and more complex it turned out to be quite unreliable. Nowadays it is using Evernote which improved the consistency and lowered the run time to 0.7s.

In the future I'm planning on adding asynchronous support as it is possible to run more than one command at the time. Also it will be rewritten from a scratch given it has a lot of syntax from when I was just starting to mess around with Python.

Some other features it has is to return the balance of a certain month, the USD currency value and a gimmicky one (currently discontinued do to lack of Google Keep support) is to return a certain number of randomly generated meals using some ingredients located on `Chef.py`. Then it'd output on two separate notes the recipes and a grocery list.
