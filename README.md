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
  "One Pen": "",
  "Two Pens": "",
  "Three Pens": "",
  "Four Pens": "",
  "Five Pens": "",
  "Six Pens": "",
  "Seven Pens": "",
  "Eight Pens": "",
  "Nine Pens": "",
  "Ten Pens": ""
}
```

If there is a pattern, this JSON can be simplified using placeholder characters (default: *) to create a template file (template.json). Values defined in this file will be correctly assigned to elements matching specified keys:
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
