class LocTreeCorruption(Exception):
    "The location tree has become corrupted and has either too many or too few items. Check to make sure you included a section heading and place."


# The triple hashtags tells the compiler what dictionary to define things under
# The double hashtag defines the name within that larger dictionary
# The single colon defines the item to put in the story list within the item withing the dictionary
# When the item doesn't accept story as a list, the only syntax used will be the syntax for options
# . (single period mark) defines options, either for dictionary items or story items
test_str = """
###Places
#Home
:Display
Hello, my name is James
"""


# This function will take in the file path in (something.story) and file path out
# It will then read the appropriate file and write the corresponding output string to the output file
# Most of the logic is abstracted outwards to compile_line, then the other compile functions
def compile(file_path_in: str, file_path_out: str):
    with open(file_path_in) as f:
        str_to_write = "from common_classes import *\nfrom state import People, Places, Routes, Scenes, player"
        tab_depth = 0
        loc_tree = None

        for line in f:
            output_str, tab_depth, loc_tree = compile_line(line, tab_depth, loc_tree)
            str_to_write += output_str
    return str_to_write


def compile_line(
    line, tab_depth: int = 0, loc_tree: list | None = None
) -> tuple[str, int, list]:
    if loc_tree == None:
        loc_tree = []

    output_str = ""

    if line[0] == "%":
        return "", tab_depth, loc_tree

    # Checking top-down (headers, then different places/routes/people, then options/things within story)
    # If the line is a header
    if line[0:3] == "###":
        output_str, tab_depth, loc_tree = compile_header(line, tab_depth, loc_tree)
    # If the line is an item in the current dictionary (for example, Places["name"]=...)
    elif line[0] == "#":
        output_str, tab_depth, loc_tree = compile_dict_item(line, tab_depth, loc_tree)
    # If it's a Display class, specifically the speaker-specific one. Because speaker dialogue is used so often, there's
    # shorthand to write it out. Not sure if I'll do that for display-text in general.
    elif line[0:2] == "::":
        output_str, tab_depth, loc_tree = compile_name_speaks(line, tab_depth, loc_tree)
    # If it's any Class. This should accept everything from Flag to Choice. This will be the most broad one to write.
    # Planned syntax:
    # :Display
    # .indent 1
    # This is text to display
    elif line[0] == ":":
        output_str, tab_depth, loc_tree = compile_story_item(line, tab_depth, loc_tree)
    elif line[0] == ".":
        output_str, tab_depth, loc_tree = compile_option(line, tab_depth, loc_tree)
    # TODO: Create the way to add text as a field to displayText. (I.e. when it's just text on a line)
    else:
        pass

    return output_str, tab_depth, loc_tree


def compile_header(line, tab_depth, loc_tree) -> tuple[str, int, list]:
    loc_tree = [line[3:]]
    return "", tab_depth, loc_tree


def compile_dict_item(line, tab_depth, loc_tree) -> tuple[str, int, list]:
    # TODO: Add support for People[""] or change to Persons[""]

    # This renders as something like Places["name"] = Place(
    output_str = f'{loc_tree[0]}["{line[1:]}"] = {loc_tree[0][:-1]}('
    tab_depth = 1  # updating tab_depth to be accurate to current tab_depth
    # tab_depth + loc_tree is important for telling when to write textToDisplay= vs. just writing "story text here"
    if len(loc_tree) == 1:
        loc_tree.append(line[1:])
    else:
        loc_tree[1] = line[1:]
    return output_str, tab_depth, loc_tree


def compile_name_speaks(
    line: str, tab_depth: int, loc_tree: list
) -> tuple[str, int, list]:
    output_str = ""

    # If story=[] hasn't been specified yet, which we can tell by the tab depth
    if tab_depth == 1:
        output_str = "\tstory=[\n"
        tab_depth = 2
    # TODO: Figure out how to close the story's opening bracket

    # Adds Display as an item in story, with the speaker set to the current speaker
    # Note that the speaker must be defined within People
    output_str += "\t" * tab_depth + f"Display(speaker=People['{line[2:]}'],"
    tab_depth += 1

    # This is because the loc tree needs to get updated when you go up/down
    # Still need to figure out how to remove items from loc_tree cleanly
    if len(loc_tree) == 2:
        loc_tree.append("Display")
    elif len(loc_tree) == 3:
        loc_tree[2] = "Display"
    else:
        print("Context:", line)
        raise LocTreeCorruption

    return output_str, tab_depth, loc_tree


def compile_story_item(
    line: str, tab_depth: int, loc_tree: list
) -> tuple[str, int, list]:
    output_str = ""

    if tab_depth == 1:
        output_str = "\tstory=[\n"
        tab_depth = 2

    story_item = line.strip()[1:]
    output_str += "\t" * tab_depth + f"{story_item}("

    if len(loc_tree) == 2:
        loc_tree.append(story_item)
    elif len(loc_tree) == 3:
        loc_tree[2] = story_item
    else:
        print("Context:", line)
        raise LocTreeCorruption

    return output_str, tab_depth, loc_tree


def compile_option(line: str, tab_depth: int, loc_tree: list) -> tuple[str, int, list]:
    output_str = "\t" * tab_depth

    i = 1

    while line[i] != " ":
        output_str += line[i]
        i += 1

    # TODO: Consider how to deal with integer options
    # Maybe check if the slice i+1 consists of only numbers by looping through the slice and checking against
    # '1234567890'
    output_str += ' = "'
    output_str += line[i + 1 :] + '"'

    return output_str, tab_depth, loc_tree


def test_basic_compile():
    # TODO: Organize these more cleanly into different tests to more easily see what breaks
    # Currently tests the file top-down, going from headers, to dictionary items, to story items
    _, tab_depth, loc_tree_test = compile_line("###Places")
    test_place_output, tab_depth, loc_tree = compile_line(
        "#Home", tab_depth, loc_tree_test.copy()
    )
    test_name_output, tab_depth, loc_tree = compile_line("::James", tab_depth, loc_tree)
    test_option_output, tab_depth, loc_tree = compile_option(
        ".color magenta", tab_depth, loc_tree
    )

    # Tests basic header functionality,
    # where headers as the defining if something should be defined under Places, People, Routes, or other
    assert loc_tree_test == ["Places"], (
        "Headers don't get compiled correctly into the location tree"
    )
    assert test_place_output == 'Places["Home"] = Place(', (
        "Places no longer get defined correctly"
    )
    assert test_name_output == "\tstory=[\n\t\tDisplay(speaker=People['James'],"
    assert test_option_output == '\t\t\tcolor = "magenta"'


"""
###Places
#Home
::James
.color magenta
"""

test_basic_compile()
