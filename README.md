batchlate is a Python program that uses a custom template to fill or translate a JSON file. This is particularly useful on a JSON that contains many elements with repeated patterns.

# Installation

Download the latest release or clone this repository.

### Requirements:

- Python 3.2 or newer

# Usage
Run `python batchlate.py -h` for a comprehensive documentation.

### Basic Usage
We will need 3 files:
- JSON file we want to update
- JSON file that will hold custom templates
- JSON file that will hold translations

The original JSON file (source.json):
```JSON
{
  "One Pen": "There is one pen.",
  "Two Pens": "There are two pens.",
  "Three Pens": "There are three pens.",
  "Four Pens": "There are four pens.",
  "Five Pens": "There are five pens.",
  "Six Pens": "There are six pens.",
  "Seven Pens": "There are seven pens.",
  "Eight Pens": "There are eight pens.",
  "Nine Pens": "There are nine pens.",
  "Ten Pens": "There are ten pens."
}
```

If there is a pattern, this JSON can be simplified with placeholder characters (default: *) to create a template file (template.json):
```JSON
{
  "One Pen": "There is one pen.",
  "* Pens": "There are * pens",
}
```

Then create a JSON file with an empty object for translations (translation.json): `{}`

Run `python batchlate.py source.json template.json translation.json` for basic usage. It will detect any matches and list translations needed. Once translation.json is filled (manually or automatically), run the program again to apply changes.\
Note: This execution will overwrite source.json. If you don't want that, provide a path with --target option.

# Contributing
Thank you for your contributions!

Open an issue for requests and bug reports.\
Create a pull request if you've made changes that will help improve this project such as the entries in [TODO](#todo) section.

# TODO
- Optimize code
- Test large data
- Proper project structure
- Migrate execution to shell commands
- Support more file types
- Enable entering regex directly as a key in templates
