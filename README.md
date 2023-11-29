# Embedded Configuration Library

## Overview

This C library simplifies configuration management for embedded Linux systems, ideal for resource-constrained environments.
It enables easy creation, reading, and writing of configuration settings, eliminating the need for complex structures like XML.
Its straightforward approach facilitates portability across various platforms with minimal modifications.
Made for Linux Embedded, but easy to use on other systems too. The code is short and straightforward, so it's simple to adapt for different operating systems

Notably, this library offers nested and array configurations without requiring complex memory allocation and data structure,
ensuring simplicity in usage. Under the permissive BSD-2-Clause license, users can freely utilize and distribute the library without licensing complexities.

## Features

- **Simple and Lightweight:** Easily understandable source code, offering an alternative to complex memory allocation and data structures like libxml2.
- **Support for Simple and Nested Structs:** Enables the creation of configurations with hierarchical structures.
- **Array Data Configurations:** Efficiently handles configurations involving arrays of data.
- **Easy Integration:** Designed for seamless integration into embedded Linux projects with minimal overhead.

## Usage

Integration into the user app:
```
   +-----------------+                                                        +------------------------+
   |   .schema file  |                                                        | User app .c, .h files  |
   +-----------------+                                                        +------------------------+
            |                                                                           |
            V                                                                           V
   +-----------------+                                                          +-----------------+
   | config_tool.py  |------------------------+                     +---------> |   C compiler    |
   +-----------------+                        |                     |           +-----------------+
            |                                 |                     |                    |
            V                                 V                     |                    V
  +---------------------+          +---------------------+          |          +----------------------+
  |      .conf file     |          | config .c, .h Files |----------+          |   User app exec file |
  +---------------------+          +---------------------+                     +----------------------+


```

User app runtime configuration:
```
   +--------------------+
   |    .conf file      |
   +--------------------+
            |
            V
   +--------------------+
   | User app program   |
   +--------------------+
 ```

The `config_tool.py` script automates the generation of C code for configurations.
It operates by taking a `.schema` file as input and generates corresponding `.c`, `.h`, and `.conf` files.

- `.conf`: Serves as the runtime configuration file.
- `.c` and `.h`: These files can be seamlessly integrated into your project.

You need to create the input `.schema` file, the syntax is similar to the C code.
Please check the `.schema` example files in the `simple`, `array` and `complex` folder
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

The `simple_config.schema` file contains a simple data structure definition without nesting.
It defines two global variables, `abc` and `xyz`, intended for export to the user application.
Below is the structure of this file:

```
// Simple data struct without nesting <-- This is the comment line

struct ABC abc; //Global variable export to the user application

struct XYZ xyz; //Global variable export to the user application

struct ABC { //Struct definition
	int a;
	float b;
	int c;
};

struct XYZ {
	float x;
	double y;
	int z;
};
```

The `config_tool.py` generates `simple_config.conf` as a runtime template.
Initially, all parameters are commented out.
Users are required to add values and enable these parameters manually.
Here is the default template:
```
#CONF_abc = {
#	abc.a = <value>;
#	abc.b = <value>;
#	abc.c = <value>;
#};

#CONF_xyz = {
#	xyz.x = <value>;
#	xyz.y = <value>;
#	xyz.z = <value>;
#};
```

### Array Configuration

Demonstrates nested and array data structures.
The program reads the configuration file, modifies values,
and writes to a new configuration file.

```bash
$ cd array
$ make
$ ./array_config
```

The `array_config.schema` file contains the nested data structure and array.
It defines a global variables `abc`, intended for export to the user application.
Below is the structure of this file:
```
//Nested and array data structure <-- This is the comment line

#define MAX_MNP 2
#define MAX_XYZ 2

struct ABC abc; //Global variable export to the user application

struct MNP { //Struct definition
	int m;
	int n;
	int p;
};

struct XYZ { //Struct definition
	float x;
	double y;
	int z;
	struct MNP mnp[MAX_MNP];
};

struct ABC { //Struct definition
	int a;
	float b;
	int c;
	struct XYZ xyz[MAX_XYZ];
};
```

The `config_tool.py` generates `array_config.conf` as a runtime template.
Initially, all parameters are commented out.
Users are required to add values and enable these parameters manually.
Here is the default template:
```
#CONF_abc = {
#	abc.a = <value>;
#	abc.b = <value>;
#	abc.c = <value>;
#	abc.xyz[0].x = <value>;
#	abc.xyz[0].y = <value>;
#	abc.xyz[0].z = <value>;
#	abc.xyz[0].mnp[0].m = <value>;
#	abc.xyz[0].mnp[0].n = <value>;
#	abc.xyz[0].mnp[0].p = <value>;
#	abc.xyz[0].mnp[1].m = <value>;
#	abc.xyz[0].mnp[1].n = <value>;
#	abc.xyz[0].mnp[1].p = <value>;
#	abc.xyz[1].x = <value>;
#	abc.xyz[1].y = <value>;
#	abc.xyz[1].z = <value>;
#	abc.xyz[1].mnp[0].m = <value>;
#	abc.xyz[1].mnp[0].n = <value>;
#	abc.xyz[1].mnp[0].p = <value>;
#	abc.xyz[1].mnp[1].m = <value>;
#	abc.xyz[1].mnp[1].n = <value>;
#	abc.xyz[1].mnp[1].p = <value>;
#};
```

### Complex Configuration

Demonstrates nested structures with multiple levels.
The program reads the configuration file, modifies values,
and writes to a new configuration file.

```bash
$ cd complex
$ make
$ ./complex_config
```

The `complex_config.schema` file contains the nested data structure with multiple levels.
It defines a global variables `abc`, intended for export to the user application.
Below is the structure of this file:
```

//Nested data structure

struct ABC abc; //Global variable export to the user application

struct MNP { //Struct definition
	int m;
	int n;
	int p;
};

struct XYZ { //Struct definition
	float x;
	double y;
	int z;
	struct MNP mnp; //Level 2 nested
};

struct ABC { //Struct definition
	int a;
	float b;
	int c;
	struct XYZ xyz; //Level 1 nested
	struct MNP abc_mnp;
};
```

The `config_tool.py` generates `complex_config.conf` as a runtime template.
Initially, all parameters are commented out.
Users are required to add values and enable these parameters manually.
Here is the default template:
```
#CONF_abc = {
#	abc.a = <value>;
#	abc.b = <value>;
#	abc.c = <value>;
#	abc.xyz.x = <value>;
#	abc.xyz.y = <value>;
#	abc.xyz.z = <value>;
#	abc.xyz.mnp.m = <value>;
#	abc.xyz.mnp.n = <value>;
#	abc.xyz.mnp.p = <value>;
#	abc.abc_mnp.m = <value>;
#	abc.abc_mnp.n = <value>;
#	abc.abc_mnp.p = <value>;
#};
```

## License
This library is licensed under the BSD-2-Clause license. See the LICENSE file for details.

## TODO

- Generate unit tests for each `.schema` input file to ensure comprehensive
test coverage and validation of functionalities.
- Currently only the `int`, `float`, and `double` types are supported.
We will work to support the array char type to support string config.

## Contributions
Contributions are welcome!
If you find any bugs or have suggestions for improvements,
feel free to open an issue or create a pull request.
