all: gen
	gcc simple_config.c main.c -o simple_config
gen:
	../config_tool.py -i simple_config.schema
clean:
	rm -rf simple_config simple_config.c simple_config.h simple_config.conf
