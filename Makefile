.PHONY: lint test smoke

NPM_ENV := env -u npm_config_http_proxy -u npm_config_https_proxy

lint:
	$(NPM_ENV) npm run lint:rt
	GM_STYLE=verbose $(NPM_ENV) npm run lint:rt
	python3 scripts/lint_doc_links.py
	python3 scripts/lint_umlauts.py
	$(NPM_ENV) npm run lint:links
	$(NPM_ENV) npm run lint:md
	$(NPM_ENV) npm run lint:presets

test:
	$(NPM_ENV) npm run test

smoke:
	bash scripts/smoke.sh
