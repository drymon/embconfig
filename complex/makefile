all: gen
	gcc complex_config.c main.c -o complex_config
gen:
	../config_tool.py -i complex_config.cfg -g complex_config.conf
clean:
	rm complex_config complex_config.c complex_config.h complex_config.conf
