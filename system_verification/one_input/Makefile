CC := g++ --std=c++17
exe := ./verifier
files := main.cpp
headers := periodic.h weaklyhard.h

$(exe): $(files) $(headers)
	$(CC) $(files) -O2 -o $(exe)

clean:
	rm -f $(exe)
