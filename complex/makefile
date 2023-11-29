all: gen
	gcc complex_config.c main.c -o complex_config
gen:
	../config_tool.py -i complex_config.schema
clean:
	rm -rf complex_config complex_config.c complex_config.h complex_config.conf
