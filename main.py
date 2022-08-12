import argparse
import sys
import os
import logging
import dataclasses
import typing as tp

import alive_progress
import clang.cindex

from generators.basic_generator import BasicGenerator
from generators.enum.generator import EnumGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def existing_dir(val: str):
    if not os.path.exists(val):
        raise ValueError(f"Path '{val}' does not exists")

    return val


def parse_args():
    args = argparse.ArgumentParser()

    args.add_argument("--project_dir", type=existing_dir, required=True)

    return args.parse_args()


def process_tu(tu: clang.cindex.TranslationUnit):
    nodes_to_parse: tp.List[clang.cindex.Cursor] = [tu.cursor]

    while nodes_to_parse:
        current_node = nodes_to_parse.pop(0)

        if current_node.kind == clang.cindex.CursorKind.ENUM_DECL:
            cmnt = current_node.raw_comment
            if cmnt is None:
                # We do not need to dig deeper, cause
                # node children - enum values.
                continue

            if "@delta_enable_codegen" not in cmnt:
                # We do not need to dig deeper, cause
                # node children - enum values.
                continue

            children = current_node.get_children()
            for ch in children:
                print(ch.spelling, ch.brief_comment, ch)
            continue

        nodes_to_parse += current_node.get_children()


@dataclasses.dataclass()
class GeneratingInfo:
    translation_unit: clang.cindex.TranslationUnit
    generators: tp.Set[BasicGenerator]


def main(args):
    logger.info("Creating generators")
    generators: tp.List[BasicGenerator] = [
        EnumGenerator(),
    ]
    logger.info("Created %d generators", len(generators))

    index = clang.cindex.Index.create()

    files_to_proceed = {
        os.path.join(dirpath, filename)
        for dirpath, dirnames, filenames in os.walk(args.project_dir)
        for filename in filenames
        if os.path.splitext(filename)[1] in {".cpp", ".hpp"}
        if not filename.startswith("test_")
        if "arguments.hpp" in filename
    }

    logger.info("Found %d files to proceed", len(files_to_proceed))

    generating_infos: tp.List[GeneratingInfo] = []

    with alive_progress.alive_bar(
        len(files_to_proceed),
        title="Parsing to AST",
    ) as progress:
        for file_path in files_to_proceed:
            progress.text = os.path.basename(file_path)
            tu = index.parse(
                file_path,
                [
                    "-fparse-all-comments",
                ],
            )

            applicable_generators = [
                generator for generator in generators if generator.need_to_generate(tu)
            ]
            if applicable_generators:
                generating_infos.append(
                    GeneratingInfo(
                        translation_unit=tu,
                        generators=applicable_generators,
                    )
                )

            progress()

    with alive_progress.alive_bar(
        len(generating_infos),
        title="Generating",
    ) as progress:
        for translation_unit in generating_infos:
            progress.text = os.path.basename(translation_unit.spelling)

            pass

            progress()


if __name__ == "__main__":
    sys.exit(main(parse_args()))
