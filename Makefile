.PHONY: lint test smoke

lint:
	npm run lint:rt
	GM_STYLE=verbose npm run lint:rt
	python3 scripts/lint_doc_links.py
	python3 scripts/lint_umlauts.py
	npm run lint:links
	npm run lint:md
	npm run lint:presets

test:
	npm run test

smoke:
	bash scripts/smoke.sh
