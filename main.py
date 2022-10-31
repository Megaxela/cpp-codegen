import argparse
import sys
import os
import logging
import dataclasses
import typing as tp
import fnmatch

import alive_progress
import clang.cindex

from generators.basic_generator import BasicGenerator, FileInfo, GeneratingConfig
from generators.enum.generator import EnumGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def existing_dir(val: str):
    if not os.path.exists(val):
        raise ValueError(f"Path '{val}' does not exists")

    return val


def namespace(val: str):
    return val.split(".")


def parse_args():
    args = argparse.ArgumentParser()

    args.add_argument(
        "--project_dir",
        type=existing_dir,
        required=True,
    )

    args.add_argument(
        "--project_include_dir",
        type=existing_dir,
        required=True,
        action="append",
    )

    args.add_argument(
        "--output_include_dir",
        type=existing_dir,
        required=True,
    )

    args.add_argument(
        "--output_source_dir",
        type=existing_dir,
        required=True,
    )

    args.add_argument(
        "--namespace",
        type=namespace,
        required=True,
        help="Namespace in dot separated form",
    )

    args.add_argument(
        "--ignore_path_glob",
        type=str,
        action="append",
    )

    args.add_argument(
        "--clang_library",
        type=existing_dir,
    )

    return args.parse_args()


@dataclasses.dataclass()
class GeneratingInfo:
    translation_unit: clang.cindex.TranslationUnit
    generator_nodes: tp.Dict[BasicGenerator, tp.List[clang.cindex.Cursor]]
    namespace: tp.List[str]
    file_info: FileInfo


def visit_ast(
    cursor: clang.cindex.Cursor,
    func: tp.Callable[[clang.cindex.Cursor], None],
):
    nodes_to_parse: tp.List[clang.cindex.Cursor] = [cursor]

    while nodes_to_parse:
        current_node = nodes_to_parse.pop(0)

        func(current_node)

        nodes_to_parse += current_node.get_children()


def main(args):
    logger.info("Creating generators")

    if args.clang_library is not None:
        clang.cindex.Config.library_file = args.clang_library

    generator_config = {
        "include_path": args.output_include_dir,
        "source_path": args.output_source_dir,
    }

    generators: tp.List[BasicGenerator] = [
        EnumGenerator(**generator_config),
    ]
    logger.info("Created %d generators", len(generators))

    index = clang.cindex.Index.create()

    files_to_proceed = {
        os.path.join(dirpath, filename)
        for dirpath, dirnames, filenames in os.walk(args.project_dir)
        for filename in filenames
        if os.path.splitext(filename)[1] in {".cpp", ".hpp"}
        if not any(
            (
                fnmatch.fnmatch(os.path.join(dirpath, filename), pattern)
                for pattern in args.ignore_path_glob
            )
        )
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

            applicable_generators = {}

            def node_processor(node: clang.cindex.Cursor):
                for generator in generators:
                    node_comment = node.raw_comment
                    if node_comment is None:
                        continue

                    if "@cpp_codegen" not in node_comment:
                        continue

                    if generator.need_to_generate(node):
                        applicable_generators.setdefault(generator, list()).append(node)

            visit_ast(tu.cursor, node_processor)

            if applicable_generators:
                generating_infos.append(
                    GeneratingInfo(
                        translation_unit=tu,
                        generator_nodes=applicable_generators,
                        namespace=args.namespace,
                        file_info=FileInfo(
                            project_include_dirs=args.project_include_dir,
                            path=file_path,
                        ),
                    )
                )

            progress()

    # Calculating total amount of nodes to proceed
    # (just for progress bar)
    total_nodes = sum(
        (
            len(nodes)
            for info in generating_infos
            for generator, nodes in info.generator_nodes.items()
        )
    )

    # Generating
    with alive_progress.alive_bar(
        total_nodes,
        title="Generating",
    ) as progress:
        for info in generating_infos:
            for generator, nodes in info.generator_nodes.items():
                for node in nodes:
                    progress.text = f"{generator.__class__.__name__}({node.spelling})"

                    generator.generate(
                        node=node,
                        file_info=info.file_info,
                        generating_config=GeneratingConfig(
                            #
                        ),
                    )

                    progress()


if __name__ == "__main__":
    sys.exit(main(parse_args()))
