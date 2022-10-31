import os
import logging
import subprocess
import distutils.spawn
import shutil
import pathlib
from xml.etree import ElementTree

import pytest
import jinja2

from plugins.codegen_testing.errors import (
    CppFailureError,
    CppFailureRepr,
    GoogleTestFailure,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_ARGUMENTS = "codegen_testing"


def load_template(name):
    with open(os.path.join(os.path.dirname(__file__), "templates", name), "r") as f:
        return jinja2.Template(f.read())


JINJA_CMAKE_LISTS_TEMPLATE = load_template("project_cmakelists.jinja2")
JINJA_MAIN_TEMPLATE = load_template("main.jinja2")

GENERATED_DIR_NAME = ".generated"


def pytest_sessionstart(session):
    pass


def pytest_collect_file(parent, path):
    if not path.fnmatch("*.yaml") and not path.fnmatch("*.yml"):
        return

    return UnittestFile.from_parent(parent=parent, path=pathlib.Path(path))


def pytest_addoption(parser):
    parser.addini(
        "cmake_binary",
        type="string",
        default=distutils.spawn.find_executable("cmake"),
        help="Binary for execution",
    )


class UnittestFile(pytest.File):
    def __init__(self, *args, **kwargs):
        pytest.File.__init__(self, *args, **kwargs)

    def collect(self):
        # Build project & collect tests.
        project_path = os.path.dirname(self.path)

        project_name = os.path.split(project_path)[-1]
        logger.info("Building '%s' project", project_name)
        logger.info("Generating CMakeLists file for '%s' project", project_name)

        project_generated_dir = os.path.join(project_path, GENERATED_DIR_NAME)

        if os.path.exists(project_generated_dir):
            shutil.rmtree(project_generated_dir)

        os.makedirs(project_generated_dir, exist_ok=True)

        template_args = {
            "project_name": project_name,
        }

        with open(os.path.join(project_path, "CMakeLists.txt"), "w") as f:
            f.write(JINJA_CMAKE_LISTS_TEMPLATE.render(**template_args))

        with open(os.path.join(project_generated_dir, "main.cpp"), "w") as f:
            f.write(JINJA_MAIN_TEMPLATE.render(**template_args))

        logger.info("Running cmake configuration for project '%s'", project_name)

        cmake_bin = self.session.config.getini("cmake_binary")
        if cmake_bin is None:
            raise RuntimeError(
                "No cmake executable has been found. Specify cmake binary in .ini as `cmake_binary`"
            )

        project_build_dir = os.path.join(project_generated_dir, "build")
        os.makedirs(project_build_dir, exist_ok=True)

        process = subprocess.run(
            [
                cmake_bin,
                "-DCMAKE_BUILD_TYPE=Release",
                "-DCMAKE_EXPORT_COMPILE_COMMANDS=On",
                "../..",
            ],
            capture_output=True,
            cwd=project_build_dir,
        )

        if process.returncode != 0:
            logger.error("stderr:\n%s", process.stderr.decode("utf-8"))
            logger.error("stdout:\n%s", process.stdout.decode("utf-8"))
            raise RuntimeError(f"Unable to configure test project '{project_name}'")

        logger.info("Running project '%s' build", project_name)
        process = subprocess.run(
            [cmake_bin, "--build", ".", "--", "-j12"],
            capture_output=True,
            cwd=project_build_dir,
        )

        if process.returncode != 0:
            logger.error("stderr:\n%s", process.stderr.decode("utf-8"))
            logger.error("stdout:\n%s", process.stdout.decode("utf-8"))
            raise RuntimeError(f"Unable to build test project '{project_name}'")

        logger.info("Running test file of project '%s' to collect tests", project_name)

        # todo: currently this will work only on linux. fix this for other OS
        test_binary = os.path.join(project_build_dir, project_name)

        process = subprocess.run(
            [test_binary, "--gtest_list_tests"],
            capture_output=True,
        )

        if process.returncode != 0:
            logger.error("stderr:\n%s", process.stderr.decode("utf-8"))
            logger.error("stdout:\n%s", process.stdout.decode("utf-8"))
            raise RuntimeError(
                f"Unable to collect test project '{project_name}' test cases"
            )

        current_case = None
        for line in process.stdout.decode("utf-8").split("\n"):
            name = line.strip()
            if not name:
                continue

            if name[-1] == ".":
                current_case = name[:-1]
                continue

            yield UnittestItem.from_parent(
                parent=self,
                name=f"{current_case}.{name}",
                path=self.path,
                binary=test_binary,
            )


class UnittestItem(pytest.Item):
    def __init__(
        self,
        name: str,
        binary: str,
        parent,
        path: str,
    ):
        pytest.Item.__init__(self, name, parent)
        self._path = path
        self._binary = binary

    def runtest(self):
        failures, output = self._execute_test()
        self.add_report_section("call", "c++", output)

        if failures:
            raise CppFailureError(failures)

    def _execute_test(self):
        output = ""

        # todo: this will only work for linux. Use tmp lib for this.
        xml_path = "/tmp/gtest_output.xml"
        args = [
            f"--gtest_filter={self.name}",
            f"--gtest_output=xml:{xml_path}",
        ]

        process = subprocess.run(
            [self._binary, *args],
            capture_output=True,
        )

        stdout_ = process.stdout.decode("utf-8")
        return_code = process.returncode

        if return_code != 0:
            # Error here
            output = "\n".join((line.strip() for line in stdout_.split("\n")))
            if return_code != 1:
                msg = (
                    "Internal Error: calling {executable} "
                    "for test {test_id} failed (returncode={returncode}):\n"
                    "{output}"
                )
                failure = GoogleTestFailure(
                    msg.format(
                        executable=self._binary,
                        test_id=self.name,
                        output=output,
                        returncode=return_code,
                    )
                )

                return [failure], output

        results = self._parse_xml(xml_path)

        for (executed_test_id, failures, skipped) in results:
            if executed_test_id == self.name:
                if failures:
                    return [GoogleTestFailure(x) for x in failures], output
                if skipped:
                    pytest.skip()
                else:
                    return None, output

        msg = "Internal Error: could not find test " "{test_id} in results:\n{results}"
        results_list = "\n".join(x for (x, f) in results)
        failure = GoogleTestFailure(msg.format(test_id=self.name, results=results_list))
        return [failure], output

    def _parse_xml(self, xml_filename):
        root = ElementTree.parse(xml_filename)
        result = []
        for test_suite in root.findall("testsuite"):
            test_suite_name = test_suite.attrib["name"]
            for test_case in test_suite.findall("testcase"):
                test_name = test_case.attrib["name"]
                failures = []
                failure_elements = test_case.findall("failure")
                for failure_elem in failure_elements:
                    failures.append(failure_elem.text)
                skipped = (
                    test_case.attrib["status"] == "notrun"
                    or test_case.attrib.get("result", None) == "skipped"
                )
                result.append((f"{test_suite_name}.{test_name}", failures, skipped))

        return result

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, CppFailureError):
            return CppFailureRepr(excinfo.value.failures)
        return pytest.Item.repr_failure(self, excinfo)

    def reportinfo(self):
        return self.fspath, 0, self.name
