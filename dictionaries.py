import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
MW_THESAURUS_API_KEY: str | None = os.getenv("MW_THESAURUS_KEY")
MW_DICTIONARY_API_KEY: str | None = os.getenv("MW_DICTIONARY_KEY")
YANDEX_API_KEY: str| None = os.getenv("YANDEX_API_KEY")


def clean_definition_text(text):
    """
    Cleans common Merriam-Webster formatting tags from definition text.
    """
    if not isinstance(text, str):
        return ""

    text = text.replace("{bc}", "")
    text = text.replace("{ldquo}", '"').replace("{rdquo}", '"')
    text = re.sub(r"\{(?:it|wi)\}(.*?)\{/(?:it|wi)\}", r"\1", text)
    text = re.sub(r"\{sx\|([^|}]+)(?:\|[^}]*)?\|\|(?:[^}]*)?\}", r"\1", text)
    text = re.sub(r"\{d_link\|([^|}]+)\|[^}]*\}", r"\1", text)
    text = re.sub(r"\{dx_def\}.*?\{/dx_def\}", "", text)
    text = re.sub(r"\{a_link\|([^|}]+)\|\}", r"\1", text)
    text = re.sub(r"\{[^}]+\}", "", text)
    return text.strip()


def parse_detailed_definitions(def_section_list):
    """
    Parses the complex 'def' section to extract definitions.
    Expects def_section_list to be the list associated with the 'def' key.
    """
    definitions = []
    if not def_section_list or not isinstance(def_section_list, list):
        return definitions

    for def_item in def_section_list:
        if not isinstance(def_item, dict):
            continue

        sseq_outer = def_item.get("sseq", [])
        for sseq_group in sseq_outer:
            for sseq_inner_list in sseq_group:
                if (
                    isinstance(sseq_inner_list, list)
                    and len(sseq_inner_list) > 1
                ):
                    sense_type = sseq_inner_list[0]
                    sense_content = sseq_inner_list[1]

                    current_defs_to_add = []
                    if sense_type in ["sense", "bs"]:
                        if "dt" in sense_content:
                            dt_array = sense_content.get("dt", [])
                            for dt_element in dt_array:
                                if (
                                    isinstance(dt_element, list)
                                    and dt_element[0] == "text"
                                ):
                                    raw_def_text = dt_element[1]
                                    cleaned_def = clean_definition_text(
                                        raw_def_text
                                    )
                                    if cleaned_def:
                                        current_defs_to_add.append(cleaned_def)
                        elif (
                            "sense" in sense_content
                            and "dt" in sense_content["sense"]
                        ):
                            dt_array = sense_content["sense"].get("dt", [])
                            for dt_element in dt_array:
                                if (
                                    isinstance(dt_element, list)
                                    and dt_element[0] == "text"
                                ):
                                    raw_def_text = dt_element[1]
                                    cleaned_def = clean_definition_text(
                                        raw_def_text
                                    )
                                    if cleaned_def:
                                        current_defs_to_add.append(cleaned_def)

                    elif sense_type == "pseq":
                        for p_sense_item in sense_content:
                            if (
                                isinstance(p_sense_item, list)
                                and len(p_sense_item) > 1
                                and p_sense_item[0] == "sense"
                            ):
                                p_sense_data = p_sense_item[1]
                                if "dt" in p_sense_data:
                                    dt_array = p_sense_data.get("dt", [])
                                    for dt_element in dt_array:
                                        if (
                                            isinstance(dt_element, list)
                                            and dt_element[0] == "text"
                                        ):
                                            raw_def_text = dt_element[1]
                                            cleaned_def = clean_definition_text(
                                                raw_def_text
                                            )
                                            if cleaned_def:
                                                current_defs_to_add.append(
                                                    cleaned_def
                                                )
                    definitions.extend(current_defs_to_add)
    return list(dict.fromkeys(definitions))


def get_definitions_from_entry(entry_data):
    """
    Extracts definitions from a single entry (a dictionary) from the API response.
    Prioritizes 'shortdef', then falls back to 'def'.
    """
    definitions = []
    if not isinstance(entry_data, dict):
        return definitions

    short_defs = entry_data.get("shortdef")
    if short_defs and isinstance(short_defs, list):
        for s_def in short_defs:
            cleaned_s_def = clean_definition_text(s_def)
            if cleaned_s_def:
                definitions.append(cleaned_s_def)
        if definitions:
            return list(dict.fromkeys(definitions))

    definitions = []
    def_section_list = entry_data.get("def")
    if def_section_list:
        detailed_definitions = parse_detailed_definitions(def_section_list)
        definitions.extend(detailed_definitions)

    return list(dict.fromkeys(definitions))


def process_api_response_to_string(api_response_data):
    """
    Processes the entire API response (a list of entry dictionaries).
    Accumulates the word, part of speech, and definitions into a single string.
    Returns the formatted string.
    """
    output_lines = []

    if not isinstance(api_response_data, list):
        output_lines.append("Error: Expected a list of entries.")
        return "\n".join(output_lines)

    for entry_index, entry in enumerate(api_response_data):
        if not isinstance(entry, dict):
            output_lines.append(
                f"Skipping invalid entry at index {entry_index}: {entry}"
            )
            continue

        word_id = entry.get("meta", {}).get("id", "N/A")
        hwi_data = entry.get("hwi", {})
        headword = (
            hwi_data.get("hw", word_id.split(":")[0])
            if isinstance(hwi_data, dict)
            else word_id.split(":")[0]
        )
        part_of_speech = entry.get("fl", "N/A")

        output_lines.append(f"--- Word: {headword} ({part_of_speech}) ---")
        if entry.get("hom"):
            output_lines.append(f"Homograph: {entry.get('hom')}")

        definitions = get_definitions_from_entry(entry)

        if definitions:
            output_lines.append("Definitions:")
            for i, definition in enumerate(definitions, 1):
                output_lines.append(f"  {i}. {definition}")
        else:
            # Check if it's a list of suggestions (strings) instead of a definition entry
            is_suggestion_list = True
            # Ensure the entry itself is a list and all its items are strings
            # This specific check for suggestions might need refinement based on actual API behavior for "not found"
            # The current JSON example doesn't show the "suggestion list" format directly at the top-level entry.
            # Typically, if the API can't find the word, the entire response `api_response_data` would be a list of strings.
            # Here, we are iterating through entries, so an individual `entry` being a list of strings is less common.
            # It's more likely `entry.get('def')` or `entry.get('shortdef')` is missing.
            output_lines.append(
                "  No definitions found for this entry structure."
            )

        output_lines.append(
            ""
        )  # Add a blank line for separation between entries

    return "\n".join(output_lines)


def get_mv_dictionary_output(word: str) -> str | None:
    response = requests.get(
        f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={MW_DICTIONARY_API_KEY}"
    )
    dict_response = response.json()
    return process_api_response_to_string(dict_response)


API_URL = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup"

def yandex_translate_en_ru(word):
    params = {
        "key": YANDEX_API_KEY,
        "lang": "en-ru",
        "text": word
    }
    r = requests.get(API_URL, params=params)
    r.raise_for_status()
    data = r.json()

    translations = []
    for def_item in data.get("def", []):
        for tr_item in def_item.get("tr", []):
            translations.append(tr_item.get("text"))

    return translations

