.PHONY: lint test smoke

lint:
	npm run lint:rt

test:
	npm run test

smoke:
	bash scripts/smoke.sh
