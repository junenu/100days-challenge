GO := /opt/homebrew/opt/go@1.23/bin/go

.PHONY: build run clean

build:
	$(GO) build -o pet .

clean:
	rm -f pet
	rm -f ~/.pet-cli/pet.json
