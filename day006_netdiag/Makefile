BINARY = netdiag
BUILD_FLAGS = CGO_ENABLED=0

.PHONY: build test clean install

build:
	$(BUILD_FLAGS) go build -o $(BINARY) .

test:
	go test ./...

install: build
	cp $(BINARY) /usr/local/bin/$(BINARY)

clean:
	rm -f $(BINARY)
