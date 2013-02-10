DIFF = git --no-pager diff --ignore-all-space --color-words --no-index

install:
	./setup.py install

test: install
	hipchat rooms list
	hipchat rooms list Med
	hipchat -i rooms list
