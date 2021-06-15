# Embedded Configuration Library

## Overview

This C library simplifies configuration management for embedded Linux systems, ideal for resource-constrained environments.
It enables easy creation, reading, and writing of configuration settings, eliminating the need for complex structures like XML.
Its straightforward approach facilitates portability across various platforms with minimal modifications.

Notably, this library offers nested and array configurations without requiring complex memory allocation,
ensuring simplicity in usage. Under the permissive BSD-2-Clause license, users can freely utilize and distribute the library without licensing complexities.

## Features

- **Simple and Lightweight:** Easily understandable source code, offering an alternative to complex memory allocation and data structures like libxml2.
- **Support for Simple and Nested Structs:** Enables the creation of configurations with hierarchical structures.
- **Array Data Configurations:** Efficiently handles configurations involving arrays of data.
- **Easy Integration:** Designed for seamless integration into embedded Linux projects with minimal overhead.

## Usage

The `config_tool.py` script automates the generation of C code for configurations.
It operates by taking a `.cfg` file as input and generates corresponding `.c`, `.h`, and `.conf` files.

- `.conf`: Serves as the runtime configuration file.
- `.c` and `.h`: These files can be seamlessly integrated into your project.

You need to create the input `.cfg` file, the syntax is similar to the C code.
Please check the `.cfg` example files in the `simple`, `array` and `complex` folder
for the reference.

For comprehensive usage instructions and command-line options,
consult the script's help documentation: `config_tool.py --help`.

## Example

### Simple Configuration

Demonstrates a basic data structure without nesting.
The program reads the configuration file, modifies values,
and writes to a new configuration file.

```bash
$ cd simple
$ make
$ ./simple_config
```

### Array Configuration

Illustrates nested and array data structures.
The program reads the configuration file, modifies values,
and writes to a new configuration file.

```bash
$ cd array
$ make
$ ./array_config
```

### Complex Configuration

Showcases nested structures with multiple levels.
The program reads the configuration file, modifies values,
and writes to a new configuration file.

```bash
$ cd complex
$ make
$ ./complex_config
```

## License
This library is licensed under the BSD-2-Clause license. See the LICENSE file for details.

Feel free to tailor the sections, add licensing information, or expand on any other details specific to your library!

## TODO

- Generate unit tests for each `.cfg` input file to ensure comprehensive
test coverage and validation of functionalities.

## Contributions
Contributions are welcome!
If you find any bugs or have suggestions for improvements,
feel free to open an issue or create a pull request.
