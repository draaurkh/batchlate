_batchlate_ is a Python program that uses a custom template to automatically fill or "translate" a JSON file. 

# Installation

Download the latest release or clone this repository.

### Requirements:

- Python 3.10 or newer

# Usage

_Note: In this document, all occurrences of_ __"python3"__ _will refer to the path to a_ python3 _executable._

Run `python3 batchlate.py -h` to view usage information.

### Basic Usage

- `python3 batchlate.py source.json template.json`: Searches "source.json" to update its entries matching keys in "template.json". A path to the translation file will be asked and automatically created.
- `python3 batchlate.py source.json template.json translation.json`: Same as the first example except the translation file path is provided. "translation.json" will be created if it's not found.
- `python3 batchlate.py --output out.json source.json template.json translation.json`: Same as the previous example except it writes to "out.json" without changing "source.json".

These commands produce the same results with the only difference being where to read and write the files. To learn how to construct these files, read [How To Create Template and Translation Files](#how-to-create-template-and-translation-files).

> [!IMPORTANT]
> Read these carefully before working with _batchlate_.
> - The program first reads all provided files to memory and then continues to work on the memory. Therefore any outside changes to those files while the program is running will be ignored and discarded. 
> - The program accepts __JSON files only with an OBJECT as top-level value__. 
> - Any JSON object entry with a non-string value is skipped because the program only works on strings. If you also want to overwrite them with produced string values, run with `--allow-nonstring-overwrite` flag.
> <a name="no-duplicates-warning"></a>
> - The program expects __unique__ JSON object keys by default. If there are duplicates, only the last key-value pair with the same keys will be accepted. There is no way around this for now, but it may be added if requested. For now, make sure to provide a separate path for the output with `--output` option when there are duplicate entries. This will help avoid losing duplicate entries in your original file since __the program always outputs unique entries__.
> - You can't use this program to add or remove entries. This feature may be added later but for now, you can only update existing ones. However, duplicate entries are removable as mentioned earlier. If that is your goal, see [the workaround](#duplicate-removal-workaround).

## How To Create Template and Translation Files

This section will get you started with _batchlate_. The concepts and rules used here are vaguely explained, see [Template Structure](#template-structure) section to read in detail.

First thing you need to do is to analyze your data. Look for similarities in the entries and notice what differs between them. Let's say your source file is like this:
```json
// source.json
{
    "house.red": "Red House", 
    "house.blue": "", 
    "house.green": "", 
    ...
    "ball.red": "Red Ball", 
    "ball.blue": "", 
    "ball.green": "", 
    ...
}
```
This is a simple yet very systematic and logical way of assigning names to things such as objects in video games. If you have a logic behind your naming of these strings, you'll find many patterns in your file. These patterns are what we'll make use of.

If there are a couple of entries, it's easy to fill manually but there may be hundreds or even thousands. _batchlate_ can easily update them provided with a good template. Once a template is created, it can be used any time it's needed. 

Apply these steps to get started:
1. _source.json_ contains objects with their colors. There is no wrong in matching the objects in this case but we will use the placeholders to only match the colors. (More on this later)
2. Delete the ellipses in _source.json_ and add as many keys as you want (keep it simple for now) with the same arrangement for objects and colors.
3. Create a JSON file named _template.json_ and copy-paste this JSON: `{"house.*": "* House", "ball.*": "* Ball"}` template will match the color parts of each entry, which are common in all keys.
4. Run `python batchlate.py -o path/to/output.json path/to/source.json path/to/template.json path/to/translation.json` with the paths to your files. You don't need to create _output.json_ and _translation.json_ as they will be automatically created if needed.
    > _Note:_ `-o` option writes the results to a separate file and doesn't alter _source.json_. If you don't mind overwriting your original file, you can omit `-o` option. 
5. The program will then ask to list the untranslated keys or auto-fill translation.json with them. Select auto-filling. Check _translation.json_ and confirm that it's created with lowercase colors inserted as keys.
6. Update the values in translation.json with the capitalized version of their keys.
7. Run the command in step 4 again. It shouldn't warn you about untranslated elements but if it does, repeat the steps 4-7. If no translation is needed, it will ask "\<n\> key(s) will be updated. Do you want to proceed?" to write the results. Answer "yes" and confirm the "Done." message.
8. _batchlate_ will look up the translations in _translation.json_ according to _template.json_ and update _output.json_. Check _output.json_ to view the results.
9. Try experimenting with more colors, or try changing the translation in template (such as: "* Colored House").

There are no limits to how you create a template. There are just efficient templates and inefficient templates. We created `{"house.*": "* House", "ball.*": "* Ball"}` instead of `{"*.red": "Red *", "*.blue": "Blue *", "*.green": "Green *"}` and there is a reason for it: _The color is an attribute of the object, not the other way around_.\
An object has many attributes but a color has only the available objects to qualify. When an object is added (to a video game for instance), all of its attributes are also added and there is high chance that they are differently phrased. When we add a color, only the naming of the color changes. 

<a name="template-efficiency"></a>
__The practical approach is to include more complex phrases in the template, and use placeholders for simple phrases__. This way, you won't need to update the template every time you add a new color. You would run the program with the same template and automatically add newly added colors to _translation.json_. This situation is kind of obvious with the arrangement of our example but it may be harder to evaluate for different arrangements. There is no wrong way to templates if it gets you what you want, it's just a matter of efficiency.

You may be wondering why we didn't just use `{"$.*": "* $"}` template and be done with it. Although it's okay with the current state of our problem, it is generally a bad idea to use templates like this. Read more [here](#ambiguous-templates). 

## Template Structure

A template is a JSON file that's used for matching entries in another JSON file to automatically update it with _batchlate_. Its entries contain placeholders that will act as wildcard characters which represent the changing parts in repeating patterns. To create a template, one needs to determine these repeating patterns in the source file. An example of a basic template JSON: `{"Type of *": "*"}` will represent this list of keys `[Type of bread, Type of cheese, Type of table, ...]` and assign the corresponding values for `[bread, cheese, table, ...]`.

_Note: Both the file and JSON entries of that file may be called as __template__ in this document._

### Placeholders And Delimeters

Placeholders match with the changing parts of similar keys. The default placeholder is `*` (asterisk) character. __A single placeholder will match only one part of a string__ and it would suffice for most use cases. But for instance, the list of keys `[Two Blue Balls, Three Blue Balls, Three Red Balls, ...]` includes infinite number of combinations. In this case, one placeholder wouldn't be enough because there are two different changing parts: The amount and the color. This list may easily be simplified by using two placeholders with the following template:
```json
{"$ * Balls": "There are $ of * colored balls."}
```

Although this template is enough for us to understand, the program will fail to detect the correct matches. Since the program doesn't know which characters to use as placeholders, it will try to use the default. Thus, __placeholder usage must be specified when it's different than the default__. Enter all of the placeholder characters (without spaces) with the key `<bt>placeholders</bt>` in the template file.
> [!NOTE]
> "`<bt></bt>`" is a _batchlate-specific_ tag. Keys containing this tag with predefined keywords do not follow standard template structure and will not be matched with your source file. The tag only accepts these keywords: placeholders, delimeters, excluded.

The program will properly execute with the updated template:
```json
{
    "<bt>placeholders</bt>": "*$",
    "$ * Balls": "There are $ of * colored balls.",
    "One * Ball": "There is one of * colored balls."  // added for the complete coverage of possible combinations
}
```
This template is constructed in a way that the program only looks for a space character between `$` and `*` placeholders. This means that possible other space characters detected with the placeholders could be confused with the one its looking for. Then it won't necessarily work correctly if there are space characters where placeholders are. In fact, while `Forty Two Blue Balls` won't cause any problems, `Two Light Blue Balls` is going to produce undesired results. To see why this happens, read [how the program creates regular expressions](#regular-expression-matching).\
This type of failure can easily be avoided by adding delimeters to the template. Since matches with more than one word cause the error, we may want to avoid matching space characters entirely. A space character as a delimeter will divide the sequence of characters word-by-word while matching. Updated template JSON:
```json
{
    "<bt>placeholders</bt>": "*$",
    "<bt>delimeters</bt>": " ",                       // added space character as a delimeter
    "$ * Balls": "There are $ of * colored balls.",
    "One * Ball": "There is one of * colored balls."  // added to completely cover the list
}
```
This template will skip occurrences like 'Forty Two Blue Balls' or 'Two Light Blue Balls' to avoid a faulty translation. This is a solution but it's not the only one.

### Grammar Difference and Template Precedence

_batchlate_ __uses regular expressions__ to match the keys and __prioritizes preceding JSON entries__. This can be used in our advantage to avoid errors and make efficient translations. Let's say we have a source JSON like this:
```json
{
  "object.wooden.house": "Wooden House",
  "object.wooden.house_stairs": "Wooden House Stairs",
  "object.wooden.house_windows": "Windows of Wooden House",
  ...
}
```
First, we need to look for patterns. It seems for every object, there is a material and a type identifier. Also only some of the entries identify parts of the object. From what we know so far `object.*.#` and `object.*.#_$` templates should represent this list of keys. For the sake of simplicity, we can assume that this particular JSON doesn't deviate much from these keys, but that is not always the case.  We could use the templates we created but then we run into a couple of problems.
1. Different grammar usage
2. Prioritized matches

Let's start with the first problem. If you look at the values of keys with `stairs` and `windows` parts, you'll notice how differently they are phrased. Change of grammar is one downside of our method since a singular template entry only allows for one type of declaration. Unless you want to change the source file to unify these similar types, we need to have an entry for each different value. Let's construct the template solving this issue:
```json
{
    "object.*.#": "* #",
    "object.*.#_stairs": "* # Stairs",
    "object.*.#_windows": "Windows of * #"
}
```
If we run the program with this template (after declaring used placeholders) it will want you to translate `[wooden, house, house_stairs, house_windows]` instead of `[wooden, house]`. It means that the program won't even consider the second and the third templates and matches all the keys with only the first template. This is because `#` placeholder in the first template will match anything until the end of string, including the keys that would also be matched by the other templates. If it's unclear, think of the first template as a more generalized version of the other templates.

<a name="precedence-rule"></a>
__Prior templates take precedence over subsequent ones__. Then we can fix the second problem by inserting the more generalized templates __after__ the ones that would otherwise be contained by it. Rearranging our template JSON like this would fix all the problems mentioned:
```json
{
    "object.*.#_stairs": "* # Stairs",
    "object.*.#_windows": "Windows of * #",
    "object.*.#": "* #"
}
```

### Entries with Different Amount of Placeholders 

Placeholder placement is pretty flexible if [grammar and precedence](#grammar-difference-and-template-precedence) rules are respected. There are a couple of ways we can take advantage of.

- ___No placeholders in keys:___ A template key without placeholders will match with keys literally and its value will be inserted directly. Since duplicate keys are not allowed ([see here](#no-duplicates-warning)), this type of key can only match a singular entry. Templates with no placeholders usually reside at the top of the template file as described in [Grammar Difference and Template Precedence](#grammar-difference-and-template-precedence). \
<a name="duplicate-removal-workaround"></a>
If your goal is to delete duplicate entries, there is a workaround. Copy one of the source JSON entries with no duplicates and paste it to the template JSON. After running the program, all duplicates saving the last one of each will be removed.

- ___Unmatching placeholders in keys:___ `{"* is used while # is not": "Using *"}` template captures two different phrases but only updates the value with the phrase captured by `*`  placeholder. This may be used when you don't want to translate a captured phrase but to only match it. The same logic applies to this template: `{"*": ""}` will match all the keys in the source and fill the values with empty strings.

- ___Unmatching placeholders in values:___ In the template `{"only * will be captured": "* is captured while # won't"}`, `*` will require translations while `#` will be used as is even though it is defined as a placeholder.

- ___Reusing placeholders in keys:___ In the template `{"* will be captured while * won't": "first * is used"}`, the phrase captured by the first `*` will be used in the value, no matter how many of the same placeholders exist in the key. If you want only to match a phrase, you can use this method instead of using another placeholder.

- ___Reusing placeholders in values:___ `{"three * in a row": "* * *"}` template will capture the phrase with `*` placeholder and place its translated value three times with a space between them.

# Limitations

## Regular Expression Matching

The program expects the wildcards to represent only what the constructed regular expression allows. The regex constructed for `$ * Balls` is `^(.+) (.+) Balls$`, if there are no delimeters. The first `(.+)` matches all characters until the space before the second `(.+)`. The second `(.+)` will also match all characters and it will continue until it reaches `" Balls"`. This forces the first placeholder to exhaustively match except the last two "words". This is the reason why `"Forty Two Blue Balls"` is correctly processed while `"Two Light Blue Balls"` produces incorrect warnings about untranslated `"Two Light"` and `"Blue"` instead of `"Two"` and `"Light Blue"`.

Unfortunately, this is how the program constructs the regex automatically. You need to be aware of the exhaustive behavior of placeholders.

### What can we do?

To detect any occurrence of this beforehand, you may analyze your data and look for exceptions. In this case, each key contained phrases separated by spaces. Since matched phrases aren't necessarily words, more than the expected amount of spaces may arise unwanted behavior. Although multiple words in the amount field is okay, the color field is bound to have only one word as mentioned before.

You have a couple of options to solve these kind of issues. Firstly, run the program without a filled translation file to see any erroneous detections if you haven't already noticed any errors while checking your data. Then do any of these:
1. ___Add entries to templates that covers all required colors___. If you respect the [precedence rule](#precedence-rule), you can add many entries that work with each other. This may solve the current problem or make it a bigger problem depending on how many colors there are. In our case, only the multi-word colors produce errors. If _Light_ colors are the only problem, this method can easily handle it.
2. ___Use a delimeter___ (simple). By setting the space character as a delimeter [as explained here](#placeholders-and-delimeters), entries with amount and colors that contain multiple words such as _Light_ colors won't be detected. Either handle them manually or add another element to templates that handles any _Light_ color.  
3. ___Update your source file___ (might break your intentional design). Since this problem originates from spaces, make it so that a multi-word element becomes a single-word like this: Forty-Two Light-Blue Balls
4. ___Use exclusions___. Exclude false positives like "Two Light" with "`<bt>excluded</bt>`" key in the template as a comma-separated list. Usefulness depends on the number of items that will be manually excluded. In this case detected false positives are too many to even consider this option. 
    
## Ambiguous Templates

Using ambiguous templates like `{"#.*": "* #"}` will eventually cause problems if you don't know what you are doing. This overgeneralized template is only useful when it's used alongside more specialized templates, respecting the [precedence rule](#precedence-rule).\
As explained [here](#grammar-difference-and-template-precedence), most of these "translations" will depend on the grammar. Similar arrangements of keys might have different interpretations and grammar usage.
For instance, both "house.red" and "dog.teeth" will match this template but they are interpreted differently.
`{"house.red": "Red House"}` is valid but `{"dog.teeth": "Teeth Dog"}` isn't. If these both are located in your file, you may not use an overgeneralized template. Refer to [this](#template-efficiency) for efficient templates.

# Contributing

Thank you for your contributions!

Open an issue for requests or bug reports.\
Create a pull request if you've made changes that will help improve this project.

# TODO
- Optimize code
- Test large data
- Proper project structure
- Migrate execution to shell commands
- Support more file types
- Enable entering regex directly as a key in templates
- Colored print messages
- Interactive usage
