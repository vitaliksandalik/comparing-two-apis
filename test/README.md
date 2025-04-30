### Run all tests

```bash
python3.12 -m unittest discover test
```

### Run specific test files

```bash
python3.12 -m unittest test.test_api_classes
python3.12 -m unittest test.test_api_analyser
python3.12 -m unittest test.test_mock_api_data
```

### Run specific test

```bash
python3.12 -m unittest test.test_api_classes.TestOldAPIOrderBookAnalyser.test_get_latency
```
