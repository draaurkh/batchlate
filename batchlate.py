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
    args = utils.parse_arguments()
    
    # also updates non-string values with produced string results
    overwrite_nonstrings = args.allow_nonstring_overwrite
    
    # read output indentation
    try:
        output_indent = int(args.output_indent)
    except ValueError:
        output_indent = args.output_indent
        if output_indent == 'compact':
            output_indent = None
        elif output_indent != '' and not output_indent.isspace():
            exit('Invalid --output-indent argument. Please provide a string or an integer value that can specify an indentation level for output.')
     
    # read required JSON files
    try:
        source = utils.read_json(args.source)
        template = utils.read_json(args.template)
    except Exception as e:
        print(e)
        exit()
    
    translation_path = args.translation
    if translation_path is None:
        print('No translation file provided.')
        print('Enter a path to a translation file. It will be created if it\'s not found.') 
        translation_path = input('> ')
    
    # read translation path
    try:
        translation = utils.read_json(translation_path)
    except FileNotFoundError:
        translation = None
    except Exception as e:
        print(f'"{translation_path}" could not be opened.\n{e}')
        exit()

    # accept only OBJECT type JSONs
    if not isinstance(source, dict):
        exit('Source JSON must have a top-level Object.')
    if not isinstance(template, dict):
        exit('Template JSON must have a top-level Object.')
    if translation is not None and not isinstance(translation, dict):
        exit('Translation JSON must have a top-level Object.')
        
    # create translation configuration
    config = utils.TConfig(template)
    config.set_translation(translation)
    config.verbose_level = args.verbose
    config.overwrite_nonstrings = overwrite_nonstrings
    batchlate = utils.Batchlate(source, config)

    # start translation of source
    result = batchlate.translate()
    non_translated_keys = result.non_translated_keys()
    
    if len(non_translated_keys) > 0:
        # there is at least one untranslated element
        print('Untranslated elements found.')
        pressed_key = ''
        while pressed_key not in set('aq23'):
            print('\nPlease provide an acceptable action.')
            print('1. (l)ist keys')
            print(f'2. (a)uto-fill untranslated keys in "{translation_path}"')
            print('3. (q)uit')
            pressed_key = input('> ').lower()
            match pressed_key:
                case '1' | 'l':
                    print('You can do either of these to resolve missing translations:')
                    print(f' - provide translations for all of them in Translation JSON ({args.translation})')
                    print(f' - add delimeters in Template JSON ({args.template}) to eliminate faulty matches')
                    print(f' - add exclusions in Template JSON ({args.template})\n')
                    
                    print('Please examine the following keys:')
                    for value, placeholder_type in result.sorted_non_translated_keys().items():
                        print(f'  - {value} ({placeholder_type})')
                        
                        
                case '2' | 'a':
                    updated_translation = dict.fromkeys(result.sorted_non_translated_keys(), '')
                    if translation is not None:
                        # new elements are added to beginning
                        updated_translation.update(translation)

                    try:
                        utils.write_json(translation_path, updated_translation, indent=2)
                    except Exception as e:
                        print(e)
                        exit()
                        
                    print(f'Translation JSON "{translation_path}" is filled with all the required keys. Fill in the translations and run the program again.')
                 
                
        print('Finishing...')
        
    elif result.updated_counter > 0:
        message = f'{result.updated_counter} key(s) will be updated.'
        if args.output is None:
            target_file = args.source
            message += f' WARNING! Source file ({args.source}) will be overwritten because a target file is not provided.'
        else: 
            target_file = args.output
            message += f' Updated entries will be written to target file ({args.output})'
        
        print(message)
        print('Do you want to proceed?')
        
        pressed_key = ''
        while pressed_key not in set('yq12'):
            print('1. (y)es')
            print('2. (q)uit')
            pressed_key = input('Please provide an acceptable action: ').lower()
            
        match pressed_key:
            case 'y' | '1':
                try:
                    utils.write_json(target_file, result.result, indent=output_indent)
                except Exception as e:
                    print(e)
                    exit()
                print('\nDone.')
            
    else:
        print('Nothing to do. Finishing...')
        
    utils.cleanup()
