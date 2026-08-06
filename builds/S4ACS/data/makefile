# LVZMQ GNU-MAKE BUILD SCRIPT
# for both Windows and Linux targets

SRC = zmq_labview.c

# WINDOWS BUILD RULES
ifeq ($(OS),Windows_NT)
	SHELL := C:\Windows\System32\cmd.exe
	# figure out the architecture cl is set up for
	ifeq ($(ARCH),)
        $(error Target architecture undefined)
	else ifeq ($(ARCH),32)
		LABVIEW = "C:\Program Files (x86)\National Instruments\LabVIEW 2010"
	else ifeq ($(ARCH),64)
		LABVIEW = "C:\Program Files\National Instruments\LabVIEW 2013"
	else
        $(error Unknown architecture on Windows "$(ARCH)")
	endif
	# set appropriate flags
	CC = cl /nologo
	ZMQ = win$(ARCH)
	# note that we define DLL_EXPORT to prevent trying to link to DLL stub functions
	CFLAGS = /DZMQ_BUILD_DRAFT_API /O1 /W3 /MD /I . /I $(ZMQ) /I $(LABVIEW)\cintools
	LDLIBS = /link $(ZMQ)\libzmq-v120-mt-4_3_2.lib user32.lib $(LABVIEW)\cintools\labviewv.lib
	ifdef DEBUG
		CFLAGS += /DDEBUG
	endif
all : win$(ARCH)\lvzmq$(ARCH).dll
# copy the product to the labview directory
	@del *.obj
	@copy $< $(LABVIEW)\vi.lib\addons\zeromq

# LINUX BUILD RULES
else
	# omg so much simpler!
	LABVIEW = /usr/local/natinst/LabVIEW-2010
	CFLAGS = -DZMQ_BUILD_DRAFT_API -Wall -O3 -m32 -fpic -I $(LABVIEW)/cintools
	LDLIBS = -lzmq -llvrt
	ifdef DEBUG
		CFLAGS += -DDEBUG
	endif
all : ../lvzmq32.so
# copy the product to the labview directory
	@cp $< $(LABVIEW)/vi.lib/addons/zeromq
endif

# Linux shared-library target
../lvzmq32.so : $(SRC)
	$(CC) -shared -o $@	$^ $(CFLAGS) $(LDFLAGS) $(LDLIBS)

# Architecture-dependent build rules -- note explicit checks machine type
win32\lvzmq32.dll : $(SRC)
	$(CC) /LD /Fe$@ $^ $(CFLAGS) $(LDFLAGS) $(LDLIBS) /machine:X86

win64\lvzmq64.dll : $(SRC)
	$(CC) /LD /Fe$@ $^ $(CFLAGS) $(LDFLAGS) $(LDLIBS) /machine:X64
