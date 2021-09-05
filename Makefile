test:
	pytest

profile:
	python3 -m cProfile -o profile -m pytest
	echo "import pstats; \
		p = pstats.Stats('profile'); \
		p.sort_stats('cumtime'); \
		p.print_stats(500)"|python3

coverage:
	pytest --cov=crcmanip --cov-report=term-missing

.PHONY: test profile coverage
