SUBDIRS := simple array complex

.PHONY: all clean $(SUBDIRS)

all: $(SUBDIRS)

clean: $(SUBDIRS)

$(SUBDIRS):
	@cd $@ && $(MAKE) $(MAKECMDGOALS)
