Yak Barber
=========

Yak Barber is a vainglorious effort at maximizing minimal know-how to create an unexceptional blogging thingy.

[Yak Shaving](http://programmers.stackexchange.com/questions/34775/correct-definition-of-the-term-yak-shaving)

This is currently in a very early stage. It can very quickly process markdown files and generate pages. It will process any directory according to the settings.py file in the directory.

## TO-DO:

1. Mustache RSS template.
2. Implement SimpleHTTPServer for local testing.
3. Find a way to import the settings that doesn't display the package import warning.
4. Add xmlrpc to allow publishing from applications that support xmlrpc.
5. Refactor the page write step to happen when the dictionary is fully assembled.
6. Refactor the dictionary to be a Python Class object.
7. Clean-up the generated page names. Current replace is a hack, should be RegEx.