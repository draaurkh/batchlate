'''
    batchlate.py  -- fills a JSON file by matching keys provided by templates
    Copyright (C) 2026  draaurkh

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import utils

if __name__ == "__main__":
    # get file paths from arguments
    args = utils.parse_arguments()
    
    if (not isinstance(args.output_indent, str)
            and not isinstance(args.output_indent, int)
            and args.output_indent is not None):
        exit('Invalid argument. Please provide a string or an integer value that can specify the indentation level with --output-indent option.')

    # create dictionaries from json objects
    source = utils.read_json(args.source)
    template = utils.read_json(args.template)
    translations = utils.read_json(args.translations)
    
    # read exclusions
    excluded = None
    if args.exclude is not None:
        excluded = set(item.strip() for item in args.exclude.split(','))

    # check if created dictionaries are valid
    if not isinstance(source, dict):
        exit('Source JSON must have an Object at the top-level.')
    if not isinstance(template, dict):
        exit('Template JSON must have an Object at the top-level.')
    if not isinstance(translations, dict):
        exit('Translations JSON must have an Object at the top-level.')
        
    # start translation of source
    result, translation_needed, updated_counter = utils.translate(source, template, translations, excluded, args.verbose)     
    
    if len(translation_needed) > 0:
        # there is at least one untranslated element
        print('Untranslated elements found.')
        pressed_key = ''
        while pressed_key not in set('aq23'):
            print('\nPlease provide an acceptable action.')
            print('1. (l)ist keys')
            print(f'2. (a)uto-fill Translations JSON: {args.translations}')
            print('3. (q)uit')
            pressed_key = input('> ').lower()
            match pressed_key:
                case '1' | 'l':
                    print('You can do either of these to resolve missing translations:')
                    print(f' - provide translations for all of them in Translations JSON ({args.translations})')
                    print(f' - add delimeters in Template JSON ({args.template})')
                    print(" - add exclusions with '--exclude' option\n")
                    
                    print('Please examine the following keys:')
                    for item in sorted(translation_needed):
                        print(f'  - {item}')
                case '2' | 'a':
                    dictionary = utils.read_json(args.translations)
                    for translation_key in translation_needed:
                        dictionary[translation_key] = ''
                    utils.write_json(args.translations, dictionary, indent=args.output_indent)
                    print(f'Translations JSON "{args.translations}" is filled with all the required keys. Fill in the translations and run the program again.')
                 
        print('Finishing...')
        
    elif updated_counter > 0:
        message = f'{updated_counter} key(s) will be updated.'
        if args.target is None:
            message += f' WARNING! Source file ({args.source}) will be overwritten because a target file is not provided.'
        else: 
            message += f' Updated strings will be written to target file ({args.target})'
        
        print(message)
        print('Do you want to continue?')
        
        pressed_key = ''
        while pressed_key not in set('yq12'):
            print('1. (y)es')
            print('2. (q)uit')
            pressed_key = input('Please provide an acceptable action: ').lower()
            
        match pressed_key:
            case 'y' | '1':
                target_file = args.target if args.target is not None else args.source
                utils.write_output(target_file, result, indent=args.output_indent)
                print('\nDone.')
            
    else:
        print('Template(s) could not match anything. Finishing...')
        
    utils.cleanup()