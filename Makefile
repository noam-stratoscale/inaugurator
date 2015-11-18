# This can be set to "remote", in which case, the installation will take the images build product from the
# object store (using solvent) instead of building them.
IMAGES_SOURCE=build

all: build unittest check_convention

clean:
	rm -fr build dist inaugurator.egg-info

check_convention:
	pep8 inaugurator --max-line-length=109 --exclude=samplegrubconfigs.py
	sh/check_spelling.sh

UNITTESTS=$(shell find inaugurator -name 'test*.py' | sed 's@/@.@g' | sed 's/\(.*\)\.py/\1/' | sort)
unittest:
	PYTHONPATH=$(PWD) python -m unittest $(UNITTESTS)

integration_test:
	PYTHONPATH=inaugurator python inaugurator/tests/integration_test.py $(TESTS)

include Makefile.build

uninstall:
	-sudo mkdir /usr/share/inaugurator
	-yes | sudo pip uninstall inaugurator

PRODUCTS = $(IMAGES_SOURCE)/inaugurator.thin.initrd.img $(IMAGES_SOURCE)/inaugurator.fat.initrd.img $(IMAGES_SOURCE)/inaugurator.vmlinuz
.PHONY: bring_images_from_remote
bring_images_from_remote:
	-mkdir remote
	sudo solvent bring --repositoryBasename=`basename $(PWD)` --product images --destination=remote

.PHONY: submitimages
submitimages: build
	-mkdir build/images_product
	cp $(PRODUCTS) build/images_product
	solvent submitproduct images build/images_product

remote/inaugurator.thin.initrd.img: bring_images_from_remote
remote/inaugurator.fat.initrd.img: bring_images_from_remote
remote/inaugurator.vmlinuz: bring_images_from_remote

install: $(PRODUCTS)
	$(MAKE) install_nodeps

install_nodeps:
	-sudo mkdir /usr/share/inaugurator
	-yes | sudo pip uninstall inaugurator
	sudo python setup.py install
	sudo cp $(PRODUCTS) /usr/share/inaugurator
	sudo chmod 644 /usr/share/inaugurator/*

prepareForCleanBuild:
	sudo pip install pika
