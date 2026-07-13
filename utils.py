'''
    utils.py  -- class and method definitions for batchlate
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
from pathlib import Path

import settings


def parse_arguments() -> argparse.Namespace:
    '''Parses command line arguments for batchlate

    Returns:
        argparse.Namespace: object containing parsed arguments
    '''

    arg_parser = argparse.ArgumentParser(
            prog='batchlate',
            usage='''python3 %(prog)s.py [OPTION]... source template
       python3 %(prog)s.py [OPTION]... source template translation''',
            description='%(prog)s is a Python program that uses a custom template to automatically fill or "translate" a JSON file.',
            epilog='Source and Documentation <https://github.com/draaurkh/batchlate>',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            allow_abbrev=False
            )

    version_info = f'''
%(prog)s {settings.PROGRAM_VERSION}

Free and open source under GNU GPLv3 license
Created and released by draaurkh <https://github.com/draaurkh/batchlate>
    '''

    arg_parser.add_argument('source', type=str, help='Path to a JSON file that\'s going to be translated. This file will be overwritten if a target file with \'--target\' option isn\'t provided.')
    arg_parser.add_argument('template', type=str, help='Path to a JSON file containing template keywords. The keys are used for searching keys in \'source\'. The values will be the replacements for the matching entries.')
    arg_parser.add_argument('translation', nargs='?', type=str, help='Path to a JSON file containing translated keywords for auto-replacement. Can be omitted. The file will be created if it\'s not found.')
    arg_parser.add_argument('-o', '--output', metavar='OUTPUT-PATH', type=str, help='Optional path to a JSON file that will contain the output. The file will be created automatically. Without this option, \'source\' JSON file will be overwritten instead.')
    arg_parser.add_argument('--output-indent', metavar='<space-indicator or "compact">', default=settings.DEFAULT_OUTPUT_INDENT, help='Indented space of the output JSON. Can be an integer, a string indicating a space such as "\\t", or "compact"')
    arg_parser.add_argument('--allow-nonstring-overwrite', action='store_true', help='Whether or not to update non-string valued entries with the produced string values')
    arg_parser.add_argument('-f', '--force', action='store_true', help='Forces to continue translation even though there are missing translations. Currently non-operational.')
    arg_parser.add_argument('-v', '--verbose', action='count', default=0)
    arg_parser.add_argument('--version', action='version', version=version_info.strip())

    return arg_parser.parse_args()


def read_json(file_path: str):
    """Extracts JSON from the provided path

    Args:
        file_path (str): Path to the JSON file that will be read

    Raises:
        FileNotFoundError: If file_path doesn't point to a file
        IsADirectoryError: If file_path is a directory
        Exception: If the file isn't a JSON or on any read errors

    Depending on top-level JSON element, returns:
        object -> dict
        array -> list | tuple
        string -> str
        number -> int | float | int- & float-derived Enums
        true -> True
        false -> False
        null -> None
    """

    p = Path(file_path)

    if not p.exists():
        raise FileNotFoundError(f'No such file: "{p}"')
    elif p.is_dir():
        raise IsADirectoryError(f'"{p}" exists but it\'s a directory. Please provide a file path.')

    with p.open('r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as je:
            raise Exception(f'"{p}" is not a properly formatted JSON file.\n{je.args[0]}')


def write_json(file_path: str, input_dict: dict[str, str], indent: int | str | None):
    """Writes a Python dictionary to a JSON file

    Args:
        file_path (str): Path that the JSON will be written to
        input_dict (dict[str, str]): The Python dictionary to be written as JSON object
        indent (int | str | None): JSON indentation

    Raises:
        FileExistsError: If the path isn't valid
        Exception: On any read errors
    """

    p = Path(file_path)

    try:
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)

        with p.open('w+') as f:
            json.dump(input_dict, f, indent=indent, ensure_ascii=False)
    except (FileExistsError, NotADirectoryError):
        raise FileExistsError(f'"{p}" could not be created. One of its parents is not a directory.')
    except Exception as e:
        raise e


class TConfig:
    """Translation configuration"""

    def __init__(self, template: dict[str, str]):
        self.template: dict[str, str] = template.copy()
        self.translation: dict[str, str] | None = None
        self.verbose_level: int = 0
        self.overwrite_nonstrings: bool = False

    def set_translation(self, translation: dict[str, str] | None):
        self.translation = None if translation is None else translation


class Batchlate:
    """Translator"""

    def __init__(self, source: dict[str, str], config: TConfig):
        self.__source: dict[str, str] = source
        self.__config: TConfig = config

    class TResult:
        def __init__(self, source: dict[str, str]):
            self.result: dict[str, str] = source.copy()    # a dictionary that combines the original file and updates 
            self.processed_keys: set[str] = set()    # a set of keys that are already processed
            self.updated_counter: int = 0    # counts how many elements of the source file will be updated
            self.__non_translated_keys: dict[str, str] = {}    # a set of detected keys that need to be translated in translations JSON

            self.__sorted_non_translated_keys: dict[str, str] | None = None

        def non_translated_keys(self):
            return self.__non_translated_keys.copy()

        def add_new_non_translated_key_or_not(self, key: str, value: str):
            if key not in self.__non_translated_keys:
                self.__non_translated_keys[key] = value
                self.__sorted_non_translated_keys = None

        def sorted_non_translated_keys(self, ):
            if self.__sorted_non_translated_keys is None:
                self.__sorted_non_translated_keys = dict(sorted(self.__non_translated_keys.items(), key=lambda item: item[1]))

            return self.__sorted_non_translated_keys.copy()

    def get_template_wildcard_property(self, key: str, default: str | None = None) -> str | None:
        value = self.__config.template.get(key)
        if value is None or len(value) == 0:
            return default

        return ''.join(set(value))  # extract unique letters

    def get_translation_value(self, key: str) -> str | None:
        if self.__config.translation is not None:
            return self.__config.translation.get(key)

        return None

    def translate(self) -> TResult:
        """Translates the TConfig object

        Raises:
            Exception: If settings.py doesn't provide DEFAULT_PLACEHOLDER

        Returns:
            TResult: The translation result that will either be complete or incomplete translation
        """

        # initialize output
        result = self.TResult(self.__source)

        template: dict[str, str] = self.__config.template

        # read and assign variables
        placeholder_types = self.get_template_wildcard_property(settings.PLACEHOLDERS_KEY, default=settings.DEFAULT_PLACEHOLDER)
        if placeholder_types is None:
            raise Exception('settings.py must provide an character value for DEFAULT_PLACEHOLDER')
        esc_placeholder_types = re.escape(placeholder_types)

        delimeters = self.get_template_wildcard_property(settings.DELIMETERS_KEY)
        esc_delimeters = re.escape(delimeters) if delimeters is not None else None

        excluded = template.get(settings.EXCLUDED_KEY)
        if excluded is not None:
            excluded = set(excluded.split(','))

        print(f'Selected placeholder(s): {placeholder_types}')
        print(f'Using delimeter(s): {delimeters}')
        print(f'Excluded translation key(s): {excluded}\n')

        for template_key in template:
            if template_key in [settings.PLACEHOLDERS_KEY, settings.DELIMETERS_KEY, settings.EXCLUDED_KEY]: 
                continue

            # get template translation value
            template_value = template.get(template_key)
            if template_value is None or not isinstance(template_value, str):
                if self.__config.verbose_level > 1:
                    print(f'Skipping the template key "{template_key}": value is non-string\n')
                continue

            # disect the key with placeholder characters
            # first is a literal, second is a placeholder
            template_key_parts: list[tuple[str, str]] = re.findall(
                rf'([^{esc_placeholder_types}]+)|([{esc_placeholder_types}])',
                template_key
            )

            # create a regular expression that would match the template
            pattern = r'^'
            placeholders = []
            for part in template_key_parts:
                # insert escape characters for literals
                pattern += re.escape(part[0])
                if part[1] == '' or part[1] not in placeholder_types:
                    continue

                placeholders.append(part[1])
                if esc_delimeters is None:
                    pattern += r'(.+)'
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

            for source_key, source_value in self.__source.items():
                if source_key in result.processed_keys:
                    # skip already processed items
                    continue

                if not self.__config.overwrite_nonstrings and not isinstance(source_value, str):
                    # skip items with non-string values if --allow-nonstring-overwrite flag isn't provided
                    if self.__config.verbose_level > 1:
                        print(f'Skipping the key "{source_key}": value is non-string\n')
                    continue

                translation_key = regex.match(source_key)

                if translation_key is None or excluded is not None and translation_key[1] in excluded:
                    # skip source_key if regex did not match or the first group of the match is excluded manually
                    continue

                if (self.__config.verbose_level > 1):
                    print(f'Parameterized string(s) for the key "{source_key}": ', translation_key.groups())

                if len(placeholders) < 1 or not is_value_parameterized:
                    # directly assign the value if it does not need replacements
                    # or the template key does not have placeholders
                    result.result[source_key] = template_value
                    result.processed_keys.add(source_key)
                    result.updated_counter += 1
                    continue

                translation_failed_flag = False
                result_value = template_value
                for i, placeholder in enumerate(placeholders):
                    if placeholder not in template_value:
                        # skip if placeholder does not need a translation
                        continue

                    # get template parameter value
                    translation = self.get_translation_value(translation_key[i+1])

                    # check if template parameter values are translated
                    if translation is None:
                        result.add_new_non_translated_key_or_not(translation_key[i+1], placeholder)
                        result.processed_keys.add(source_key)
                        translation_failed_flag = True
                        if (self.__config.verbose_level > 1):
                            print('Missing translation, skipping...\n')
                        continue
                    elif not isinstance(translation, str):
                        translation_failed_flag = True
                        if (self.__config.verbose_level > 1):
                            print('Translation is not a string, skipping...\n')
                        continue

                    result_value = result_value.replace(placeholder, translation)

                if not translation_failed_flag:
                    # translation success
                    result.result[source_key] = result_value
                    result.processed_keys.add(source_key)
                    result.updated_counter += 1
                    if (self.__config.verbose_level > 1):
                        print(f'Will translate to: "{result_value}"\n')

        return result


def cleanup():
    re.purge()

