all: gen
	gcc array_config.c main.c -o array_config
gen:
	../config_tool.py -i array_config.schema
clean:
	rm -rf array_config array_config.c array_config.h array_config.conf
