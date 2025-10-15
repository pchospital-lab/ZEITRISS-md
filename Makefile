.PHONY: lint test smoke

lint:
	npm run lint:rt
	npm run lint:links
	npm run lint:md

test:
	npm run test

smoke:
	bash scripts/smoke.sh
