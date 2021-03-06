DIFF = git --no-pager diff --ignore-all-space --color-words --no-index

install:
	./setup.py install

test: install
	hipchat -i rooms list HipchatCLI | xargs -I _ hipchat rooms delete _
	hipchat users show $(USERNAME)
	hipchat -i users show $(USERNAME)
	hipchat rooms create $(USERNAME) HipchatCLITest
	hipchat rooms create $(USERNAME) HipchatCLITest2
	hipchat rooms list
	hipchat rooms list Test2
	echo 'hi there' | hipchat rooms message HipchatCLITest $(USERNAME)
	hipchat -i rooms list HipchatCLI | xargs -I _ hipchat rooms delete _
	hipchat rooms list
