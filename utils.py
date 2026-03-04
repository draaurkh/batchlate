'''
    utils.py  -- method definitions for batchlate
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

import argparse
import json
import re
import os.path

import settings

def parse_arguments():
    """Parses command line arguments

    Returns:
        argparse.Namespace: object containing parsed arguments
    """
    
    module_path = os.path.abspath(os.path.dirname(__file__))
    description_path = os.path.join(module_path, settings.DESC_REL_PATH)
    
    with open(description_path) as description_file:
        description_string = description_file.read()
    
    arg_parser = argparse.ArgumentParser(
        prog='batchlate',
        usage='python batchlate.py [OPTION]... source template translation',
        description='%(prog)s is a Python program that uses a custom template to fill or translate a JSON file. This is particularly useful on a JSON that contains many elements with repeated patterns.',
        epilog=description_string,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    arg_parser.add_argument('source', type=str, help="Path to a JSON file that's going to be translated. This file will be overwritten if a target file with '--target' option isn\'t provided.")
    arg_parser.add_argument('template', type=str, help='Path to a JSON file containing template keywords (keys with placeholders)')
    arg_parser.add_argument('translations', metavar='translation', type=str, help='Path to a JSON file containing translated keywords for auto-replacement')
    arg_parser.add_argument('-t', '--target', metavar='TARGET-FILE', type=str, help='Optional path to a JSON file that will contain the output. The file will be created automatically. Without this option, \'source\' JSON file will be overwritten.')
    arg_parser.add_argument('-x', '--exclude', metavar='EXCLUDED', type=str, help='A comma separated list of keywords to exclude from translating.')
    arg_parser.add_argument('--output-indent', metavar='INDENT', default=2, help="Indented space of the output JSON. Could be integer or a string indicating a space such as '\\t'. Default: 2")
    arg_parser.add_argument('-f','--force', action='store_true', help='Forces to continue translation even though there are missing translations. Currently non-operational.')
    arg_parser.add_argument('-v','--verbose', action='count', default=0)
    arg_parser.add_argument('--version', action='version', version=f'%(prog)s {settings.PROGRAM_VERSION}')
    
    return arg_parser.parse_args()

def read_json(file_path):
    with open(file_path, 'r') as file:
        result = json.load(file)
        
    return result

def write_json(file_path, dictionary, indent):
    with open(file_path, 'r+') as file:
        json.dump(dictionary, file, indent=indent, ensure_ascii=False)
        
def write_output(file_path, dictionary, indent):
    with open(file_path, 'w+') as file:
        json.dump(dictionary, file, indent=indent, ensure_ascii=False)

def get_template_properties(template_dict, key):
    value = template_dict.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        exit(f'{key} key defined in Template JSON file must be a string.')
    if len(value) == 0:
        return None
    
    return ''.join(set(value))        

def translate(source, template, translations, excluded=None, verbose_level=0):
    # initialize output
    result = source.copy()
    translation_needed = set()  # a set that holds detected keys that need to be translated in translations JSON
    updated_counter = 0         # counts how many elements of the original file will be updated

    # read and assign variables
    placeholder_types = get_template_properties(template, settings.PLACEHOLDERS_KEY)
    if placeholder_types is None:
        placeholder_types = settings.DEFAULT_PLACEHOLDER
    esc_placeholder_types = re.escape(placeholder_types)
        
    delimeters = get_template_properties(template, settings.DELIMETERS_KEY)
    esc_delimeters = re.escape(delimeters) if delimeters is not None else None
    
    print(f'Selected placeholder(s): {placeholder_types}')
    print(f'Using delimeter(s): {delimeters}\n')
    
    for template_key in template:
        if template_key == settings.PLACEHOLDERS_KEY or template_key == settings.DELIMETERS_KEY: 
            continue
        
        # get template translation value
        template_value = template.get(template_key)
        
        if not isinstance(template_value, str):
            print(f'Template with key "{template_key}" is not a string. Skipping...')
            continue
        
        # disect the key with placeholder characters
        template_key_parts = re.findall(
            fr'([^{esc_placeholder_types}]+)|([{esc_placeholder_types}])',
            template_key
        )
        
        # insert escape characters for regular expression search
        template_key_parts = [(re.escape(part[0]), part[1]) for part in template_key_parts]
        
        # create a regular expression that would match the template
        pattern = r'^'
        placeholders = []
        for part in template_key_parts:
            pattern += part[0]
            if part[1] == '' or part[1] not in placeholder_types:
                continue
            
            placeholders.append(part[1])
            if esc_delimeters is None:
                pattern += rf'(.+)'
            else: 
                pattern += rf'([^{esc_delimeters}]+)'
        
        pattern += r'$'
        
        regex = re.compile(pattern)
        
        # check if the template value needs replacements
        is_value_parameterized = False
        for placeholder in placeholders:
            if placeholder in template_value:
                is_value_parameterized = True
                break
        
        for source_key in source:
            translation_key = regex.match(source_key)
            
            if translation_key is None or excluded is not None and translation_key[1] in excluded:
                # skip source_key if regex did not match or the first group of the match is excluded manually
                continue
            
            if (verbose_level > 1):
                print(f'Parameterized string(s) for key "{source_key}": ', translation_key.groups())
            
            if len(placeholders) < 1 or not is_value_parameterized:
                # directly assign the value if it does not need replacements or the template key does not have placeholders
                result[source_key] = template_value
                updated_counter += 1
                continue
            
            placeholder_replacement_failed_flag = False
            result_value = template_value
            for i, placeholder in enumerate(placeholders):
                # get template parameter value
                translation = translations.get(translation_key[i+1])
                
                # check if template parameter values are translated
                if translation is None:
                    translation_needed.add(translation_key[i+1])
                    placeholder_replacement_failed_flag = True
                    if (verbose_level > 1):
                        print('Missing translation, skipping...\n')
                    break
                
                result_value = result_value.replace(placeholder, translation)
            
            if not placeholder_replacement_failed_flag:
                result[source_key] = result_value
                updated_counter += 1
                if (verbose_level > 1):
                    print(f'Will translate to: {result_value}\n')
                    
    return result, translation_needed, updated_counter

def cleanup(message=None):
    re.purge()
