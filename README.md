# cpp-codegen
This project implements small tooling that easily perform C++ code generation.

## Usage

### Code
To enable codegen in specific node, provide multiline comment to that node and declare new doxygen section `@cpp_codegen`.
Then provide activation strings for desired generator.

Example:
```cpp
/**
 * @cpp_codegen
 * string_serialization
 */
enum sample {
    val_1
};
```

## Generators
Supported generators:

### `enum`
This generator generates code for enumeration conversions. To enable this generator for specific enumeration enable one of the following subgenerators in `@cpp_codegen` comment section.
To override default serialization values, provide enumeration value comment with following format `//< "value"prefix[, "value"prefix]`.
Activation strings for this generator are subgenerator names.

#### Subgenerators
| Name                   | Description                                  |
|------------------------|----------------------------------------------|
| `string_serialization` | Provides enum conversion to string           |
| `json_serialization`   | Provides enum conversion to `nlohmann::json` |

#### Example
Code below will trigger generation of file `converters/simple_enum.hpp` with following converters:
- `std::string_view to_string(const ::some_ns::sample_enum&)`
- `void to_json(::nlohmann::json&, const ::some_ns::sample_enum&)`

```cpp
namespace some_ns {
/**
 * @cpp_codegen
 * string_serialization
 * json_serialization
 */
enum class sample_enum {
    sample_val_1,  //< "custom_val_1"s "custom_val_2"json
    sample_val_2,
};
} // some_ns

...

ASSERT_EQ(some_ns::to_string(some_ns::sample_enum::sample_val_1), "custom_val_1");
ASSERT_EQ(nlohmann::json(some_ns::sample_enum::sample_val_1), nlohmann::json("custom_val_1"));
```

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
usage: main.py [-h] --project_dir PROJECT_DIR --project_include_dir PROJECT_INCLUDE_DIR --output_include_dir OUTPUT_INCLUDE_DIR
               --output_source_dir OUTPUT_SOURCE_DIR --namespace NAMESPACE [--ignore_path_glob IGNORE_PATH_GLOB]
               [--clang_library CLANG_LIBRARY]

options:
  -h, --help            show this help message and exit
  --project_dir PROJECT_DIR
                        Path to project directory. This directory will be iterated to parse C++ files.
  --project_include_dir PROJECT_INCLUDE_DIR
                        Path to `project_dir` project include directories. Can be declared multiple times. This directory will be used
                        to convert paths to includes.
  --output_include_dir OUTPUT_INCLUDE_DIR
                        Path to directory for generated header files.
  --output_source_dir OUTPUT_SOURCE_DIR
                        Path to directory for generated source files.
  --namespace NAMESPACE
                        Namespace in dot separated form (not used right now).
  --ignore_path_glob IGNORE_PATH_GLOB
                        File globs that should be excluded from project parsing. For example `test_*.cpp`.
  --clang_library CLANG_LIBRARY
                        Absolute path to system clang library. If script will not be able to locate library by itself you may provide
                        this argument.
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
