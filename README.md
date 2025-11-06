# MaimaiPy
Cookie-based data fetcher using Python. Initially forked from [swyrin/paranormal-maimai](https://github.com/swyrin/paranormal-maimai). Detached as most of the codebase and features have been completely rewritten.

## Features
`app/session.py` - utilises a modular class as an interface to access pages using the `clal` cookie.
`app/parser.py` - feeds routes onto the session and parses HTML responses.
`app/record.py` - class structures of data to be returned by parser.
`app/datasource.py` - retrieves song metadata from [zvuc/otoge-db](https://github.com/zvuc/otoge-db), can be attached to instances such as `RecordEntry` for seamless access using `@property` attributes.



*Random notes*
Hopefully I dont get sidetracked again.


