all: gen
	gcc simple_config.c main.c -o simple_config
gen:
	../config_tool.py -i simple_config.cfg -g simple_config.conf
clean:
	rm simple_config simple_config.c simple_config.h simple_config.conf
