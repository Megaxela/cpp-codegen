# cpp-codegen
This project implements small tooling that easily perform C++ code generation.

## Usage

### CMake

`cpp-codegen` supports cmake integration. Example usage:

```cmake
include(path_to_cpp_codegen/cmake/cpp_codegen.cmake)

file(GLOB_RECURSE SOURCES src/*.cpp)
add_executable(target_name ${SOURCES})

target_codegen(target_name)
```

### Raw

```
usage: main.py [-h] --project_dir PROJECT_DIR --project_include_dir PROJECT_INCLUDE_DIR --output_include_dir OUTPUT_INCLUDE_DIR --output_source_dir
               OUTPUT_SOURCE_DIR --namespace NAMESPACE [--ignore_path_glob IGNORE_PATH_GLOB]

options:
  -h, --help            show this help message and exit
  --project_dir PROJECT_DIR
  --project_include_dir PROJECT_INCLUDE_DIR
  --output_include_dir OUTPUT_INCLUDE_DIR
  --output_source_dir OUTPUT_SOURCE_DIR
  --namespace NAMESPACE
                        Namespace in dot separated form
  --ignore_path_glob IGNORE_PATH_GLOB
```

## Testing

C++ codegen testing is performed via example projects with `gtest` unit tests. Test projects located in `testsuite/tests` directory.

Example test directory structure.

- `test_<test_name>/`
    - `include` - optional directory for include files.
    - `src` - optional directory for source files.
    - `tests` - mandatory directory for `gtest` tests
    - `test_project.yml` - file, that describes test project. Empty for now.

## License
<img align="right" src="http://opensource.org/trademarks/opensource/OSI-Approved-License-100x137.png">

This tooling is licensed under the [MIT License](https://opensource.org/licenses/MIT) 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
