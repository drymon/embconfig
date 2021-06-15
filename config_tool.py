#!/usr/bin/env python3
import re
import sys
import getopt
import os.path

class ConfigParser():
    def __init__(self, fname, header_fname):
        header_recomp = re.compile(r"(\S+).h")
        r_header = header_recomp.match(header_fname)
        if r_header:
            self.header_fname = r_header.group(1)
        else:
            self.header_fname = header_fname
        # datadef_array in format: {'type', 'type_name', 'var_name', 'members', 'array_size'}
        # contain a list of user data type difinition e.g. struct ABC abc;
        # 'type'='struct', 'type_name'='ABC', 'var_name'='abc' and 'members' and 'array_size' = None
        self.datadef_array = []
        # vardef_array in format: {'type', 'type_name', 'var_name', 'value'}
        self.vardef_array = []
        self.macro_array = []
        self.basic_types_array = []
        self.parse_file(fname, self.datadef_array, self.vardef_array, self.macro_array)
        self.expand_member(self.datadef_array, self.vardef_array)
        self.get_basic_types(self.basic_types_array, self.datadef_array)

    def parse_file(self, file_name, datadef_array, vardef_array, macro_array):
        file_object = open(file_name, encoding = 'utf-8')
        structdef_start_recomp = re.compile(r"^\s*struct\s+(\S+)\s*{\s*(//.*)?")
        member_base_recomp = re.compile(r"^\s*(\S+)\s+(\S+)\s*;\s*(//.*)?")
        member_struct_recomp = re.compile(r"^\s*struct\s+(\S+)\s+(\S+)\s*;\s*(//.*)?")
        structdef_end_recomp = re.compile(r"^\s*};\s*(//.*)?")
        comment_line_recomp = re.compile(r"^\s*//.*")
        blank_line_recomp = re.compile(r"^\s+$")
        staticvar_struct_recomp = re.compile(r"^\s*struct\s+(\S+)\s+(\S+)\s*;\s*(//.*)?")
        staticvar_base_recomp = re.compile(r"^\s*(\S+)\s+(\S+)\s*(=\s*\S+)?;\s*(//.*)?")
        macro_recomp = re.compile(r"^\s*#define\s+(\S+)\s+(\S+)")
        array_recomp = re.compile(r"(\S+)\[\s*(\S+)\]\s*")
        line_number = 0
        while True:
            line = file_object.readline()
            if line == "":
                break
            line_number += 1

            r_macro = macro_recomp.match(line)
            if r_macro:
                macro_array.append((r_macro.group(1), r_macro.group(2)))
                continue

            r_datadef = structdef_start_recomp.match(line)
            if r_datadef:
                member_array = []
                while True:
                    line = file_object.readline()
                    if line == "":
                        break

                    line_number += 1

                    if comment_line_recomp.match(line) or blank_line_recomp.match(line):
                        continue

                    r_mem = member_base_recomp.match(line)
                    if r_mem:
                        r_array = array_recomp.match(r_mem.group(2))
                        if r_array:
                            member_array.append((r_mem.group(1), None,
                                                 r_array.group(1), [], r_array.group(2)))
                        else:
                            member_array.append((r_mem.group(1), None, r_mem.group(2), [], None))
                    else:
                        if structdef_end_recomp.match(line):
                            break
                        r_mem = member_struct_recomp.match(line)
                        if r_mem:
                            # e.g. struct ABC abc;
                            r_array = array_recomp.match(r_mem.group(2))
                            if r_array:
                                member_array.append(("struct", r_mem.group(1),
                                                     r_array.group(1), [], r_array.group(2)))
                            else:
                                member_array.append(("struct", r_mem.group(1),
                                                     r_mem.group(2), [], None))
                        else:
                            print("struct %s: line %d, expect };"
                                  %(r_datadef.group(1), line_number))
                            member_array.clear()
                            break

                if len(member_array) > 0:
                    datadef_array.append(("struct", r_datadef.group(1),
                                          None, member_array, None))

            else:
                if comment_line_recomp.match(line) or blank_line_recomp.match(line):
                    continue
                r_vardef = staticvar_struct_recomp.match(line)
                if r_vardef:
                   vardef_array.append(("struct", r_vardef.group(1),
                                        r_vardef.group(2), None))
                else:
                    value = None
                    r_vardef = staticvar_base_recomp.match(line)
                    if r_vardef:
                        if r_vardef.group(3) != None:
                            val_recomp = re.compile(r"=\s*(\S+)")
                            if val_recomp:
                                r_value = val_recomp.match(r_vardef.group(3))
                                value = r_value.group(1)
                        vardef_array.append((r_vardef.group(1),
                                             None, r_vardef.group(2), value))

    def expand_struct(self, datadef_array, struct_type):
        struct_members = struct_type[3]
        for member in struct_members:
            # Not a struct or already expanded => skip
            if member[0] != 'struct' or len(member[3]) != 0:
                continue
            for datadef in datadef_array:
                if datadef[0] != 'struct' or datadef[1] != member[1]:
                    continue
                self.expand_struct(datadef_array, datadef)
                # replace with an expanded struct
                member[3].append(datadef)
                break;

    def expand_member(self, datadef_array, vardef_array):
        for vardef in vardef_array:
            if vardef[0] != 'struct':
                continue
            for datadef in datadef_array:
                if datadef[0] != 'struct' or datadef[1] != vardef[1]:
                    continue
                self.expand_struct(datadef_array, datadef)

    def get_basic_types_from_struct(self, basic_types_array, struct_object):
        if struct_object[0] != 'struct':
            return
        for member in struct_object[3]:
            if member[0] == 'struct':
                self.get_basic_types_from_struct(basic_types_array, member)
            else:
                self.append_basic_type(basic_types_array, member[0])

    def append_basic_type(self, basic_types_array, basic_type):
        existed = False
        for basic in basic_types_array:
            if basic == basic_type: # existed already ~> Ignore
                existed = True
                break
        if existed == False:
            basic_types_array.append(basic_type)

    def get_basic_types(self, basic_types_array, datadef_array):
        for datadef in datadef_array:
            if datadef[0] == 'struct':
                self.get_basic_types_from_struct(basic_types_array, datadef)
            else:
                self.append_basic_type(basic_types_array, datadef[0])

    def generate_config_file(self, outf):
        for vardef in self.vardef_array:
            if vardef[0] == 'struct':
                outf.write("#CONF_%s = {\n" %vardef[2])

                for datadef in self.datadef_array:
                    if datadef[0] != 'struct' or datadef[1] != vardef[1]:
                        continue
                    self.generate_datatype_config_file(datadef[0], vardef[2],
                                   datadef[3], None, datadef[4], outf)
                    outf.write("#};\n\n")
            else:
                outf.write("#CONF_%s = {\n\t%s = <value>;\n};\n\n"
                           %(vardef[2], vardef[2]))

    def generate_datatype_config_file(self, datatype, name, member_array,
                                      father_name, array_size, outf):
        if array_size == None:
            if father_name == None:
                new_father = name
            elif name == None:
                new_father = father_name
            else:
                new_father = "%s.%s" %(father_name, name)

            if datatype == 'struct':
                for member in member_array:
                    if member[0] == 'struct':
                        self.generate_datatype_config_file(member[0], member[2],
                                  member[3], new_father, member[4], outf)
                    else:
                        outf.write("#\t%s.%s = <value>;\n" %(new_father, member[2]))
        else: #Array case
            if array_size.isnumeric():
                size = int(array_size)
            else:
                size = self.get_define_value(array_size)
            if size <= 0:
                print("No valid define: %s!!!" %array_size)
                return
            for i in range(size):
                if father_name == None:
                    new_father = "%s[%d]" %(name, i)
                elif name == None:
                    new_father = father_name
                else:
                    new_father = "%s.%s[%d]" %(father_name, name, i)
                if datatype == 'struct':
                    for member in member_array:
                        if member[0] == 'struct':
                            self.generate_datatype_config_file(member[0], member[2],
                                        member[3], new_father, member[4], outf)
                        else:
                            outf.write("#\t%s.%s = <value>;\n" %(new_father, member[2]))

    def generate_header_file(self, outf):
        for macro in self.macro_array:
            outf.write("#define %s %s\n\n" %(macro[0], macro[1]))

        self.generate_extern_global_variable(outf)

        for datadef in self.datadef_array:
            if datadef[0] != 'struct':
                continue
            outf.write("struct %s {\n" %datadef[1])
            for member in datadef[3]:
                if member[0] == 'struct':
                    if member[4] != None:
                        outf.write("\tstruct %s %s[%s];\n" %(member[1], member[2], member[4]))
                    else:
                        outf.write("\tstruct %s %s;\n" %(member[1], member[2]))
                else:
                    if member[4] != None:
                        outf.write("\t%s %s[%s];\n" %(member[0], member[2], member[4]))
                    else:
                        outf.write("\t%s %s;\n" %(member[0], member[2]))
            outf.write("};\n\n")

        outf.write("int %s_read(const char* file_name);\n\n" %self.header_fname)
        outf.write("int %s_write(const char* file_name);\n\n" %self.header_fname)

    def generate_global_variable_option(self, outf, extern):
        for vardef in self.vardef_array:
            if extern == True:
                globalvar = "extern %s " %vardef[0]
            else:
                globalvar = "%s " %vardef[0]

            if vardef[0] == 'struct':
                globalvar += "%s %s;" % (vardef[1], vardef[2])
            else:
                if vardef[3] != None:
                    globalvar += "%s = %s;" % (vardef[2], vardef[3])
                else:
                    globalvar += "%s;" % vardef[2]

            outf.write("%s\n\n" %globalvar)

    def generate_global_variable(self, outf):
        self.generate_global_variable_option(outf, False)

    def generate_extern_global_variable(self, outf):
        self.generate_global_variable_option(outf, True)

    def generate_datatype_read_function(self, datatype, name, member_array,
                                        father_name, array_size, outf):
        if array_size == None:
            if father_name == None:
                new_father = name
            elif name == None:
                new_father = father_name
            else:
                new_father = "%s.%s" %(father_name, name)

            if datatype == 'struct':
                for member in member_array:
                    if member[0] == 'struct':
                        self.generate_datatype_read_function(member[0], member[2],
                                     member[3], new_father, member[4], outf)
                    else:
                        var_access = "%s.%s" % (new_father, member[2])
                        outf.write("\tread_%s(&%s, \"%s\", buffs, nbuffs);\n"
                                   %(member[0], var_access, var_access))
        else: #Array case
            if array_size.isnumeric():
                size = int(array_size)
            else:
                size = self.get_define_value(array_size)
            if size <= 0:
                print("No valid define: %s!!!" %array_size)
                return
            for i in range(size):
                if father_name == None:
                    new_father = "%s[%d]" %(name, i)
                elif name == None:
                    new_father = father_name
                else:
                    new_father = "%s.%s[%d]" %(father_name, name, i)

                if datatype == 'struct':
                    for member in member_array:
                        if member[0] == 'struct':
                            self.generate_datatype_read_function(member[0], member[2],
                                         member[3], new_father, member[4], outf)
                        else:
                            var_access = "%s.%s" % (new_father, member[2])
                            outf.write("\tread_%s(&%s, \"%s\", buffs, nbuffs);\n"
                                       %(member[0], var_access, var_access))

    def get_define_value(self, name):
        for macro in self.macro_array:
            if macro[0] == name:
                return int(macro[1])
        return -1

    def generate_read_function(self, outf):
        for vardef in self.vardef_array:
            outf.write("static int read_%s(char **buffs, int nbuffs) \n{\n" %vardef[2])
            if vardef[0] == 'struct':
                for datadef in self.datadef_array:
                    if datadef[0] != 'struct' or datadef[1] != vardef[1]:
                        continue
                    self.generate_datatype_read_function(datadef[0], vardef[2],
                                  datadef[3], None, datadef[4], outf)
            else:
                outf.write("\tread_%s(&%s, \"%s\", buffs, nbuffs);\n"
                           %(vardef[0], vardef[2], vardef[2]))
            outf.write("\n\treturn 0;\n")
            outf.write("}\n\n")

        # export function
        outf.write("int %s_read(const char* file_name)" %self.header_fname)
        ctext = '''
{
	struct config_region regions[NUM_REGIONS_MAX];
	int nregions;
	FILE *file;
	int i;

	file = fopen(file_name, "r");
	if (file == NULL) {
		printf("%s:Unable to open file %s for reading.\\n", __func__, file_name);
		return -1;
	}

	nregions = parse_regions(file, regions, NUM_REGIONS_MAX);
	for (i = 0; i < nregions; i++) {
'''
        outf.write(ctext)

        for vardef in self.vardef_array:
            outf.write("\t\tif (strcmp(regions[i].name, \"CONF_%s\") == 0) {\n"
                       % vardef[2])
            outf.write("\t\t\tmemset(&%s, 0, sizeof(%s));\n" %(vardef[2], vardef[2]))
            outf.write("\t\t\tread_%s(regions[i].buffs, regions[i].nbuffs);\n"
                       % vardef[2])
            outf.write("\t\t}\n")

        outf.write("\t}\n\n")
        outf.write("\trelease_regions(regions, nregions);\n")
        outf.write("\tfclose(file);\n\n")
        outf.write("\treturn 0;\n")
        outf.write("}\n")

    def get_ctype_print_format(self, data_type):
        if data_type == 'int':
            return "%d"
        elif data_type == 'float':
            return "%f"
        elif data_type == 'double':
            return "%lf"
        elif data_type == 'char':
            return "%c"
        else:
            return  "unknown"

    def generate_datatype_write_function(self, datatype, name, member_array,
                                         father_name, array_size, outf):
        if array_size == None:
            if father_name == None:
                new_father = name
            elif name == None:
                new_father = father_name
            else:
                new_father = "%s.%s" %(father_name, name)

            if datatype == 'struct':
                for member in member_array:
                    if member[0] == 'struct':
                        self.generate_datatype_write_function(member[0], member[2],
                                     member[3], new_father, member[4], outf)
                    else:
                        var_access = "%s.%s" % (new_father, member[2])
                        outf.write("\t\tfprintf(file, \"\\t%s = %s;\\n\", %s);\n"
                              %(var_access, self.get_ctype_print_format(member[0]), var_access))
        else: #Array case
            if array_size.isnumeric():
                size = int(array_size)
            else:
                size = self.get_define_value(array_size)
            if size <= 0:
                print("No valid define: %s!!!" %array_size)
                return
            for i in range(size):
                if father_name == None:
                    new_father = "%s[%d]" %(name, i)
                elif name == None:
                    new_father = father_name
                else:
                    new_father = "%s.%s[%d]" %(father_name, name, i)

                outf.write("\tif (%s.isInUsed != 0) {\n" %new_father)

                if datatype == 'struct':
                    for member in member_array:
                        if member[0] == 'struct':
                            self.generate_datatype_write_function(member[0], member[2],
                                          member[3], new_father, member[4], outf)
                        else:
                            var_access = "%s.%s" % (new_father, member[2])
                            outf.write("\t\tfprintf(file, \"\\t%s = %s, %s;\\n\");\n"
                                %(var_access, self.get_ctype_print_format(member[0]), var_access))
                outf.write("\t}\n")

    def generate_write_function(self, outf):
        for vardef in self.vardef_array:
            outf.write("\nstatic int config_write_%s(FILE *file) \n{\n" % vardef[2])
            if vardef[0] == 'struct':
                outf.write("\tfprintf(file, \"CONF_%s = {\\n\");\n" %vardef[2])
                for datadef in self.datadef_array:
                    if datadef[0] != 'struct' or datadef[1] != vardef[1]:
                        continue
                    self.generate_datatype_write_function(datadef[0], vardef[2],
                                  datadef[3], None, datadef[4], outf)
                outf.write("\tfprintf(file, \"};\\n\");\n")
            else:
                outf.write("\tfprintf(file, \"CONF_%s = %s\\n\", %s);\n"
                      %(vardef[2], self.get_ctype_print_format(vardef[0]), vardef[2]))
            outf.write("\treturn 0;\n")
            outf.write("}\n")

        # export function
        outf.write("\nint %s_write(const char* file_name)\n" %self.header_fname)

        ctext = '''
{
	FILE *file = fopen(file_name, "w");
	if (file == NULL) {
		printf("%s:Unable to open file\\n", __func__);
		return -1;
	}
'''
        outf.write(ctext)

        for vardef in self.vardef_array:
            outf.write("\tconfig_write_%s(file);\n" % vardef[2])
        outf.write("\tfclose(file);\n\n\treturn 0;\n}")

    def generate_static_source(self, outf):
        ctext = '''
//Optimize the size for your usecase
#define REGION_NBUFF_MAX 128
#define READ_BUFF_SIZE 512
#define NUM_REGIONS_MAX 16
#define REGION_NAME_SIZE 32

struct config_region {
	char name[REGION_NAME_SIZE];
	char *buffs[REGION_NBUFF_MAX];
	int nbuffs;
};

'''
        outf.write(ctext)

        ctext_start = '''
	int i;

	for (i = 0; i < nbuffs; i++) {
		if (buffs[i] == NULL) {
			continue;
		}
		if (strstr(buffs[i], tag) != NULL) {
			char *endtag;
			char *value = strstr(buffs[i], "=");
			if (value == NULL) {
				printf("%s:Missing value: %s\\n", __func__, buffs[i]);
				return -1;
			}
			value += 1; //skip '='
			endtag = strstr(value, ";");
			if (endtag == NULL) {
				printf("%s:Missing ';': %s\\n", __func__, buffs[i]);
				return -1;
			}
			*endtag = 0;
'''

        ctext_end = '''
			return 0;
		}
	}

	return -1;
}
'''
        data_types = []
        for basic_type in self.basic_types_array:
            if basic_type == 'int':
                data_types.append(('int', 'atoi'))
            elif basic_type == 'float':
                data_types.append(('float', 'atof'))
            elif basic_type == 'double':
                data_types.append(('double', 'atof'))

        for data_type in data_types:
            outf.write("\nstatic int read_%s(%s *var, const char *tag, "
                       "char **buffs, int nbuffs) \n{"
                       %(data_type[0], data_type[0]))
            outf.write(ctext_start)
            outf.write("\t\t\t*var = (%s)%s(value);\n" %(data_type[0], data_type[1]))
            outf.write(ctext_end)

        ctext = '''
static void remove_space(char *str)
{
	int i;
	int j = 0;

	for (i = 0; str[i] != 0; i++) {
		if ((str[i] != ' ') && (str[i] != '\\t') && (str[i] != '\\n')) {
			if (j != i) {
				str[j] = str[i];
			}
			j++;
		}
	}
	str[j] = 0;
}

static int conf_readline(FILE *inf, char *line, int size)
{
	char a;
	int res;
	int rp=0;

	if (feof(inf))
		return 0;

	while ((res = fread(&a, 1, 1, inf))) {
		if (res < 0) {
			if (feof(inf)) {
				return 0;
			} else {
				printf("%s:error to read config file\\n", __func__);
				return -1;
			}
		}

		if (a == '\\n') {
			break;
		}

		line[rp++] = a;
		if (rp >= size-1) {
			printf("%s:too long line\\n", __func__);
			return -1;
		}
	}

	line[rp++] = 0;

	return rp;
}

static int load_region(struct config_region *region, char *name, int name_size,
					   FILE *file, char *bufread, int bufsize)
{
	int result = 0;
	bool end_region = false;
	int size;

	if (name_size >= REGION_NAME_SIZE) {
		printf("%s:name region too long: %s\\n", __func__, name);
		return -1;
	}
	memset(region->name, 0, REGION_NAME_SIZE);
	memcpy(region->name, name, name_size);
	region->nbuffs = 0;

	while (conf_readline(file, bufread, bufsize) > 0) {
		remove_space(bufread);
		if (bufread[0] == '#') {
			continue;
		}
		if (strstr(bufread, "};") == bufread) {
			end_region = true;
			break;
		}
		size = strlen(bufread) + 1;
		region->buffs[region->nbuffs] = malloc(size);
		if (region->buffs[region->nbuffs] == NULL) {
			printf("%s:unable to malloc\\n", __func__);
			break;
		}
		memset(region->buffs[region->nbuffs], 0, size);
		memcpy(region->buffs[region->nbuffs], bufread, size);
		region->nbuffs++;
	}

	if (end_region == false) {
		int i;

		printf("%s:Missing '};' region: %s\\n", __func__, region->name);
		for (i = 0; i < region->nbuffs; i++) {
			free(region->buffs[i]);
		}
		region->nbuffs = 0;
		result = -1;
	}

	return result;
}

static int parse_regions(FILE *file, struct config_region *regions, int max_regions)
{
	char region_name[REGION_NAME_SIZE];
	char buff[READ_BUFF_SIZE];
	int nregions = 0;
	char *temp;

	while (conf_readline(file, buff, sizeof(buff)) > 0) {
		remove_space(buff);
		if (buff[0] == '#') {
			continue;
		}
		if (strstr(buff, "CONF_") != buff) {
			continue;
		}
		temp = strstr(buff, "={");
		if (temp == NULL) {
			continue;
		}

		*temp = 0; //Set NULL terminate
		strncpy(region_name, buff, REGION_NAME_SIZE-1);

		if (load_region(&regions[nregions], buff, temp - buff,
						file, buff, sizeof(buff)) == 0) {
			nregions++;
		} else {
			printf("%s:Unable to load region: %s\\n", __func__, region_name);
		}

		if (nregions == max_regions) {
			break;
		}
	}

	return nregions;
}

static void release_regions(struct config_region *regions, int nregions)
{
	int i;
	int j;

	for (i = 0; i < nregions; i++) {
		for (j = 0; j < regions[i].nbuffs; j++) {
			if (regions[i].buffs[j] != NULL) {
				free(regions[i].buffs[j]);
				regions[i].buffs[j] = NULL;
			}
		}
	}
}

'''
        outf.write(ctext)

    def generate_include_header(self, outf):
        outf.write("#include <stdint.h>\n")
        outf.write("#include <stdbool.h>\n")
        outf.write("#include <string.h>\n")
        outf.write("#include <stdio.h>\n")
        outf.write("#include <stdlib.h>\n")
        outf.write("#include \"%s.h\"\n\n" %self.header_fname)

    def generate_source_file(self, outf):
        self.generate_include_header(outf)
        self.generate_global_variable(outf)
        self.generate_static_source(outf)
        self.generate_read_function(outf)
        self.generate_write_function(outf)

def print_usage():
    pname=sys.argv[0][sys.argv[0].rfind('/')+1:]
    print("%s [options]" % pname)
    print("    -h|--help: this help")
    print("    -i|--input: input .cfg file name")
    print("    -c|--cfile: output .c source file")
    print("    -f|--hfile: output .h header file")
    print("    -g|--conf: output .conf file")

def set_options():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:c:f:g:",
                                   ["help", "input=", "cfile", "hfile"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        print_usage()
        sys.exit(1)

    if len(args) > 0:
        print("Invalid args:")
        print(args)
        print_usage()
        sys.exit(1)

    res = {'input':'example.cfg', 'hfile':None, 'cfile':None, 'conf':None}

    for o, a in opts:
        if o in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        elif o in ("-i", "--input"):
            res['input'] = a
        elif o in ("-f", "--hfile"):
            res['hfile'] = a
        elif o in ("-c", "--cfile"):
            res['cfile'] = a
        elif o in ("-g", "--conf"):
            res['conf'] = a
        else:
            assert False, "unhandled option"

    input_recomp = re.compile(r"(\S+).cfg")
    r_input = input_recomp.match(res['input'])
    if r_input == None:
        print("Input should be a .cfg file")
        sys.exit(1)

    if res['hfile'] == None:
        res['hfile'] = r_input.group(1) + ".h"
    if res['cfile'] == None:
        res['cfile'] = r_input.group(1) + ".c"

    return res

copyright = """
/* BSD 2-Clause License
*
* Copyright (c) 2023, nguyenvannam142@gmail.com
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*
* 1. Redistributions of source code must retain the above copyright notice, this
*    list of conditions and the following disclaimer.
*
* 2. Redistributions in binary form must reproduce the above copyright notice,
*    this list of conditions and the following disclaimer in the documentation
*    and/or other materials provided with the distribution.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
* FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
"""

if __name__ == "__main__":

    options = set_options()

    hfile_basename = os.path.basename(options['hfile'])
    parser = ConfigParser(options['input'], hfile_basename)

    hfile_recomp = re.compile(r"(\S+).h")
    r_hfile = hfile_recomp.match(hfile_basename)
    if r_hfile == None:
        print("Header file should be a .h file")
        sys.exit(1)
    hfile_out = open(options['hfile'], "w")
    hfile_out.write("%s\n" %copyright)
    hfile_out.write("#ifndef %s_H\n" %r_hfile.group(1).upper())
    hfile_out.write("#define %s_H\n\n" %r_hfile.group(1).upper())
    parser.generate_header_file(hfile_out)
    hfile_out.write("#endif //%s_H\n" %r_hfile.group(1).upper())
    hfile_out.close()

    cfile_out = open(options['cfile'], "w")
    cfile_out.write("%s\n" %copyright)
    parser.generate_source_file(cfile_out)
    cfile_out.close()

    if options['conf'] != None:
        conf_out = open(options['conf'], "w")
        parser.generate_config_file(conf_out)
        conf_out.close()

    sys.exit(0)
