
/* BSD 2-Clause License
*
* Copyright (c) 2023, nguyenvannam142@gmail.com
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*
* 1. Redistributions of source code must retain the above copyright notice, this
*    list of conditions and the following disclaimer.
*
* 2. Redistributions in binary form must reproduce the above copyright notice,
*    this list of conditions and the following disclaimer in the documentation
*    and/or other materials provided with the distribution.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
* FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include <stdio.h>
#include "complex_config.h"

#define READ_FILE "./complex_config.conf"
#define WRITE_FILE "./complex_config_write.conf"

int main(int argc, char *argv[])
{
	int res;
	char *rf = READ_FILE;
	char *wf = WRITE_FILE;

	if ((argc > 1) && (argc != 3)) {
		printf("usage: %s [read conf] [write conf]\n", argv[0]);
		return -1;
	}

	if (argc == 3) {
		rf = argv[1];
		wf = argv[2];
	}

	res = complex_config_read(rf);
	if (res < 0) {
		printf("Read %s FAILED\n", rf);
		return -1;
	}
	printf("Read %s OK\n", rf);

	abc.a = 100;
	abc.b = 1000.0;
	abc.c = 10000.0;
	abc.xyz.x = 1111;
	abc.xyz.y = 2222;
	abc.xyz.z = 3333;
	abc.xyz.mnp.m = 4444;
	abc.xyz.mnp.n = 5555;
	abc.xyz.mnp.p = 6666;
	abc.abc_mnp.m = 7777;
	abc.abc_mnp.n = 8888;
	abc.abc_mnp.p = 9999;

	printf("Change value of abc and write to new file: %s\n", wf);

	res = complex_config_write(wf);
	if (res < 0) {
		printf("Write %s FAILED\n", wf);
		return -1;
	}
	printf("Write %s OK\n", wf);

	return 0;
}
